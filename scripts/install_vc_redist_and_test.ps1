Param(
    [string]$PythonExe = "python",
    [string]$Package = "cv2"
)

$Url = "https://aka.ms/vs/16/release/vc_redist.x64.exe"
$Out = Join-Path $env:TEMP "vc_redist.x64.exe"

Write-Output "Downloading $Url to $Out ..."
try {
    Invoke-WebRequest -Uri $Url -OutFile $Out -UseBasicParsing -ErrorAction Stop
} catch {
    Write-Error "Download failed: $_"
    exit 2
}

Write-Output "Running installer (may prompt for admin)."
$args = "/install /quiet /norestart"
$proc = Start-Process -FilePath $Out -ArgumentList $args -Wait -PassThru -Verb RunAs
Write-Output "Installer exited with code $($proc.ExitCode)."

Write-Output "Preparing Python check script..."
$pyfile = Join-Path $env:TEMP "vc_redist_check.py"
$pycode = @"
import sys, struct, importlib, traceback
print('PYTHON_EXECUTABLE:', sys.executable)
print('BITNESS:', struct.calcsize('P')*8)
try:
    importlib.import_module('$Package')
    print('IMPORT_OK')
except Exception:
    traceback.print_exc()
    sys.exit(3)
"@

Set-Content -Path $pyfile -Value $pycode -Encoding UTF8

Write-Output "Running Python checks with $PythonExe ..."
& $PythonExe $pyfile
$exit = $LASTEXITCODE
if ($exit -eq 0) {
    Write-Output "Package import succeeded."
} else {
    Write-Warning "Package import failed with exit code $exit. See traceback above for details."
}

Write-Output "Done. If the installer reported success but imports still fail, please reboot and re-run the script or try reinstalling the Python package in your venv."
