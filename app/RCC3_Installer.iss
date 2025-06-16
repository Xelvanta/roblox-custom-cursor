; RCC3_Installer.iss
[Setup]
AppName=Roblox Custom Cursor
AppVersion=3.0.0
AppVerName=Roblox Custom Cursor  ; <--- This overrides the default display name
DefaultDirName={pf}\Xelvanta Softworks\Roblox Custom Cursor
DefaultGroupName=Roblox Custom Cursor
OutputDir=.
OutputBaseFilename=RCC3_Installer
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE

[Files]
; Main executable
Source: "Roblox Custom Cursor.pyw"; DestDir: "{app}"; Flags: ignoreversion

; Launcher executable
Source: "rcur_importer_launcher.exe"; DestDir: "{app}"; Flags: ignoreversion

; Data images folder
Source: "data\images\*"; DestDir: "{app}\data\images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Roblox Custom Cursor"; Filename: "{app}\Roblox Custom Cursor.pyw"; IconFilename: "{app}\data\images\rcur_icon_variable.ico"
Name: "{group}\Uninstall Roblox Custom Cursor"; Filename: "{uninstallexe}"; IconFilename: "{app}\data\images\rcur_icon_variable.ico"

[Registry]
; Associate .rcur file with the app
Root: HKCR; Subkey: ".rcur"; ValueType: string; ValueData: "rcurfile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "rcurfile"; ValueType: string; ValueData: "Roblox Custom Cursor Profile"; Flags: uninsdeletekey
Root: HKCR; Subkey: "rcurfile\DefaultIcon"; ValueType: string; ValueData: "{app}\data\images\rcur_icon_variable.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "rcurfile\shell\open\command"; ValueType: string; ValueData: """{app}\rcur_importer_launcher.exe"" ""%1"""; Flags: uninsdeletekey
