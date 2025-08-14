Set-Location "D:\Dev\repos\pywinauto-mcp\src"
$env:PYTHONPATH = "D:\Dev\repos\pywinauto-mcp\src"
Write-Host "Testing module execution with timeout..."
$job = Start-Job -ScriptBlock {
    Set-Location "D:\Dev\repos\pywinauto-mcp\src"
    $env:PYTHONPATH = "D:\Dev\repos\pywinauto-mcp\src"
    python -m pywinauto_mcp.main 2>&1
}

Start-Sleep -Seconds 3
$job | Stop-Job
$result = $job | Receive-Job

if ($result) {
    $result | Out-File -FilePath "test_module_result.txt" -Encoding UTF8
    Write-Host "✅ Module execution test completed"
    Write-Host "Result:"
    Get-Content "test_module_result.txt" -ErrorAction SilentlyContinue
} else {
    Write-Host "❌ No output from module execution"
}

$job | Remove-Job