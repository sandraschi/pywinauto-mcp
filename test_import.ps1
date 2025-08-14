Set-Location "D:\Dev\repos\pywinauto-mcp\src"
$env:PYTHONPATH = "D:\Dev\repos\pywinauto-mcp\src"
python -c "import pywinauto_mcp.main; print('✅ Import successful')" > test_import_result.txt 2>&1
Get-Content test_import_result.txt -ErrorAction SilentlyContinue