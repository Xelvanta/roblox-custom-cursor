; RCC3_Installer.iss
[Setup]
AppId={{c1004246-945e-4b7c-863e-e6c0184d4086}_rcc3
AppName=Roblox Custom Cursor
AppVersion=3.0.0
AppVerName=Roblox Custom Cursor
DefaultDirName={pf}\Xelvanta Softworks\Roblox Custom Cursor
DefaultGroupName=Roblox Custom Cursor
OutputDir=.
OutputBaseFilename=RCC3_Installer
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE

[Files]
; Main app
Source: "Roblox Custom Cursor.pyw"; DestDir: "{app}"; Flags: ignoreversion

; Importer script
Source: "rcur_importer.pyw"; DestDir: "{app}"; Flags: ignoreversion

; Importer launcher executable
Source: "rcur_importer_launcher.exe"; DestDir: "{app}"; Flags: ignoreversion

; Data images folder
Source: "data\images\*"; DestDir: "{app}\data\images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: desktopicon; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Icons]
Name: "{group}\Roblox Custom Cursor"; Filename: "{app}\Roblox Custom Cursor.pyw"; IconFilename: "{app}\data\images\rcur_icon_variable.ico"
Name: "{group}\Uninstall Roblox Custom Cursor"; Filename: "{uninstallexe}"; IconFilename: "{app}\data\images\rcur_icon_variable.ico"
Name: "{userdesktop}\Roblox Custom Cursor"; Filename: "{app}\Roblox Custom Cursor.pyw"; IconFilename: "{app}\data\images\rcur_icon_variable.ico"; Tasks: desktopicon

[Registry]
; Associate .rcur file with the app
Root: HKCR; Subkey: ".rcur"; ValueType: string; ValueData: "rcurfile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "rcurfile"; ValueType: string; ValueData: "Roblox Custom Cursor Profile"; Flags: uninsdeletekey
Root: HKCR; Subkey: "rcurfile\DefaultIcon"; ValueType: string; ValueData: "{app}\data\images\rcur_icon_variable.ico"; Flags: uninsdeletekey
Root: HKCR; Subkey: "rcurfile\shell\open\command"; ValueType: string; ValueData: """{app}\rcur_importer_launcher.exe"" ""%1"""; Flags: uninsdeletekey

[Code]
function IsAppInstalled(): Boolean;
var
  uninstallKeyExists: Boolean;
  installDirExists: Boolean;
  uninstallRegKey: String;
begin
  uninstallRegKey := 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{c1004246-945e-4b7c-863e-e6c0184d4086}_rcc3_is1';

  uninstallKeyExists := RegKeyExists(HKLM, uninstallRegKey);
  installDirExists := DirExists(ExpandConstant('{pf}\Xelvanta Softworks\Roblox Custom Cursor'));

  Result := uninstallKeyExists or installDirExists;
end;


function TrimString(const S: String): String;
var
  startIdx, endIdx: Integer;
begin
  startIdx := 1;
  endIdx := Length(S);
  // Trim left spaces and quotes
  while (startIdx <= endIdx) and ((S[startIdx] = ' ') or (S[startIdx] = '"')) do
    Inc(startIdx);
  // Trim right spaces and quotes
  while (endIdx >= startIdx) and ((S[endIdx] = ' ') or (S[endIdx] = '"')) do
    Dec(endIdx);
  if endIdx >= startIdx then
    Result := Copy(S, startIdx, endIdx - startIdx + 1)
  else
    Result := '';
end;

function GetUninstallPath(): String;
var
  uninstallRegKey: String;
  uninstallPathRaw: String;
  uninstallPathClean: String;
begin
  uninstallRegKey := 'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{c1004246-945e-4b7c-863e-e6c0184d4086}_rcc3_is1';
  uninstallPathRaw := '';
  
  if not RegQueryStringValue(HKLM, uninstallRegKey, 'UninstallString', uninstallPathRaw) then
    uninstallPathRaw := '';
  
  uninstallPathClean := TrimString(uninstallPathRaw);
  
  Result := uninstallPathClean;
end;

function InitializeSetup(): Boolean;
var
  res: Integer;
  uninstallPath: String;
begin
  if IsAppInstalled() then
  begin
    uninstallPath := GetUninstallPath();
    // DEBUG
    // MsgBox('UninstallString from registry: ' + uninstallPath, mbInformation, MB_OK);

    res := MsgBox('Roblox Custom Cursor is already installed. Do you want to uninstall it before continuing?', mbConfirmation, MB_YESNO);
    if res = IDYES then
    begin
      if (uninstallPath = '') or (not FileExists(uninstallPath)) then
      begin
        MsgBox('Uninstaller not found at path: ' + uninstallPath + #13#10 + 'Please uninstall manually before continuing.', mbError, MB_OK);
        Result := False;
        Exit;
      end;

      if Exec(uninstallPath, '/VERYSILENT /NORESTART', '', SW_SHOW, ewWaitUntilTerminated, res) then
      begin
        if res = 0 then
        begin
          MsgBox('Uninstall completed. Please restart the installer.', mbInformation, MB_OK);
          Result := False;  // exit so user restarts installer fresh
          Exit;
        end
        else
        begin
          MsgBox('Uninstall failed. Please uninstall manually before continuing.', mbError, MB_OK);
          Result := False;
          Exit;
        end;
      end
      else
      begin
        MsgBox('Failed to execute uninstaller. Please uninstall manually before continuing.', mbError, MB_OK);
        Result := False;
        Exit;
      end;
    end
    else
    begin
      Result := False;
      Exit;
    end;
  end;

  Result := True;
end;
