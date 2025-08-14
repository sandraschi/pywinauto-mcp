Set-Location "D:\Dev\repos\pywinauto-mcp\src"
python -c "import pywinauto_mcp.main; print('Import successful')" > test_import.txt 2>&1
Get-Content test_import.txt -ErrorAction SilentlyContinue