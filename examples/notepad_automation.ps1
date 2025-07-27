# Notepad Automation Example
# This script demonstrates how to use PyWinAutoMCP to automate Notepad

# Start Notepad if it's not already running
$notepad = Get-Process -Name "notepad" -ErrorAction SilentlyContinue
if (-not $notepad) {
    Start-Process notepad
    Start-Sleep -Seconds 1  # Give Notepad time to start
}

# Find the Notepad window
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/windows/find" -Method Post -Body (@{
    title = "Untitled - Notepad"
    timeout = 5
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "Found Notepad window:" ($response | ConvertTo-Json -Depth 5)

# Type some text
Invoke-RestMethod -Uri "http://localhost:8000/api/element/type" -Method Post -Body (@{
    window_handle = $response.window_handle
    text = "Hello from PyWinAuto MCP!`nThis is a test of the Windows automation capabilities.`n"
} | ConvertTo-Json) -ContentType "application/json"

# Get information about the edit control
$editInfo = Invoke-RestMethod -Uri "http://localhost:8000/api/element/info" -Method Post -Body (@{
    window_handle = $response.window_handle
    control_type = "Edit"
} | ConvertTo-Json) -ContentType "application/json"

Write-Host "Edit control info:" ($editInfo | ConvertTo-Json -Depth 5)

# Click the File menu
Invoke-RestMethod -Uri "http://localhost:8000/api/element/click" -Method Post -Body (@{
    window_handle = $response.window_handle
    title = "File"
    control_type = "MenuItem"
} | ConvertTo-Json) -ContentType "application/json"

# Click Save As (this will open the Save As dialog)
Start-Sleep -Milliseconds 500  # Wait for menu to open
Invoke-RestMethod -Uri "http://localhost:8000/api/element/click" -Method Post -Body (@{
    window_handle = $response.window_handle
    title = "Save As..."
    control_type = "MenuItem"
} | ConvertTo-Json) -ContentType "application/json"

# Note: The Save As dialog would require additional handling
# This is a simplified example to demonstrate the concept

Write-Host "Notepad automation complete!"
