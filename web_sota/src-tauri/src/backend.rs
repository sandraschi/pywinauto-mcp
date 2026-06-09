use std::fs;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::thread;

use tauri::{AppHandle, Emitter, Manager};
use tauri::path::BaseDirectory;

pub struct BackendProcess(pub Mutex<Option<Child>>);

const BACKEND_NAME: &str = "pywinauto-mcp-backend.exe";

fn dev_backend_path() -> Option<PathBuf> {
    if !cfg!(debug_assertions) {
        return None;
    }
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("binaries")
        .join("pywinauto-mcp-backend-x86_64-pc-windows-msvc.exe");
    path.exists().then_some(path)
}

/// Copy the PyInstaller binary from the app bundle into cache (not beside the operator exe).
pub fn materialize_backend(app: &AppHandle) -> Result<PathBuf, String> {
    if let Some(dev_path) = dev_backend_path() {
        return Ok(dev_path);
    }

    let bundled = app
        .path()
        .resolve(BACKEND_NAME, BaseDirectory::Resource)
        .map_err(|e| format!("bundled backend missing from resources: {e}"))?;

    let cache_dir = app
        .path()
        .app_cache_dir()
        .map_err(|e| format!("app cache dir: {e}"))?;
    fs::create_dir_all(&cache_dir).map_err(|e| format!("create cache dir: {e}"))?;

    let cached = cache_dir.join(BACKEND_NAME);
    let version_file = cache_dir.join("backend-version.txt");
    let current_version = app.package_info().version.to_string();
    let cached_version = fs::read_to_string(&version_file).unwrap_or_default();

    if !cached.exists() || cached_version != current_version {
        fs::copy(&bundled, &cached).map_err(|e| format!("copy backend to cache: {e}"))?;
        fs::write(&version_file, current_version).map_err(|e| format!("write version: {e}"))?;
    }

    Ok(cached)
}

pub fn spawn_backend(app: AppHandle, state: &BackendProcess) -> Result<String, String> {
    let backend_path = materialize_backend(&app)?;

    let mut child = Command::new(&backend_path)
        .env("PYWINAUTO_MCP_PORT", "10789")
        .env("PYWINAUTO_MCP_HOST", "127.0.0.1")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to spawn {}: {e}", backend_path.display()))?;

    let stdout = child.stdout.take();
    let stderr = child.stderr.take();
    state.0.lock().unwrap().replace(child);

    if let Some(out) = stdout {
        let app_handle = app.clone();
        thread::spawn(move || watch_backend_stream(out, false, app_handle));
    }
    if let Some(err) = stderr {
        let app_handle = app.clone();
        thread::spawn(move || watch_backend_stream(err, true, app_handle));
    }

    Ok("Backend starting on 10789".into())
}

fn watch_backend_stream<R: std::io::Read + Send + 'static>(
    stream: R,
    is_stderr: bool,
    app: AppHandle,
) {
    let reader = BufReader::new(stream);
    let mut ready = false;
    for line in reader.lines().map_while(Result::ok) {
        if is_stderr {
            eprintln!("[backend] {}", line.trim());
        } else {
            eprintln!("[backend] {}", line.trim());
        }
        if !ready
            && (line.contains("Uvicorn running") || line.contains("Application startup complete"))
        {
            ready = true;
            let _ = app.emit("backend-status", "ready");
        }
    }
}
