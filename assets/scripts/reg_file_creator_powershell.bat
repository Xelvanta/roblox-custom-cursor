@echo off
setlocal enabledelayedexpansion

REM Define base paths using %SystemDrive%
set "BASE_DIR=%SystemDrive%\Program Files\Xelvanta Softworks\Roblox Custom Cursor"
set "ICON_PATH=%BASE_DIR%\data\images\rcur_icon_variable.ico"
set "LAUNCHER_PATH=%BASE_DIR%\rcur_importer_launcher.exe"

REM Define the .reg file path to generate
set "REG_FILE=%~dp0rcur_association.reg"

REM Create the .reg file with header
(
echo Windows Registry Editor Version 5.00
echo.
echo [HKEY_CLASSES_ROOT\.rcur]
echo @="rcurfile"
echo.
echo [HKEY_CLASSES_ROOT\rcurfile]
echo @="Roblox Custom Cursor Profile"
echo.
echo [HKEY_CLASSES_ROOT\rcurfile\DefaultIcon]
echo @="!ICON_PATH!"
echo.
echo [HKEY_CLASSES_ROOT\rcurfile\shell\open\command]
echo @="\"!LAUNCHER_PATH!\" \"%%1\""
) > "%REG_FILE%"

REM Replace placeholders with actual paths (handle backslashes properly)
powershell -Command ^
  "$content = Get-Content -Raw '%REG_FILE%';" ^
  "$icon = '%ICON_PATH%';" ^
  "$launcher = '%LAUNCHER_PATH%';" ^
  "$patternIcon = [regex]::Escape('!ICON_PATH!');" ^
  "$patternLauncher = [regex]::Escape('!LAUNCHER_PATH!');" ^
  "$replacementIcon = $icon.Replace('\\','\\\\');" ^
  "$replacementLauncher = $launcher.Replace('\\','\\\\');" ^
  "$content = $content -replace $patternIcon, $replacementIcon -replace $patternLauncher, $replacementLauncher;" ^
  "Set-Content -Encoding ASCII '%REG_FILE%' -Value $content"

REM To automatically import the registry file, remove the REM from the next line.
REM If you uncomment the following line to import automatically, you might want to
REM change the REG_FILE path to a writable temp folder, for example:
REM    set "REG_FILE=%TEMP%\rcur_association.reg"
REM reg import "%REG_FILE%"

REM echo Successfully registered .rcur file type.
REM pause
