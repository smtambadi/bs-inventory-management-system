$startupFolder = [Environment]::GetFolderPath('Startup')
$vbsPath = Join-Path $startupFolder "BierSymphonyAutoSync.vbs"

# Automatically get the directory where this script is located
$projectRoot = $PSScriptRoot
$syncScriptPath = Join-Path $projectRoot "sync_engine\auto_sync.py"

$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "pythonw.exe ""$syncScriptPath""", 0, False
"@

Set-Content -Path $vbsPath -Value $vbsContent
Write-Host "Successfully installed background sync engine!"
Write-Host "Startup script created at: $vbsPath"
Write-Host "It will execute: $syncScriptPath"
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
