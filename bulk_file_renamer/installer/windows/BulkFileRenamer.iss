; Bulk File Renamer - Windows Installer
; Copyright (c) 2024 Dominic Ritzmann
; Licensed under the MIT License
; Clean, standalone installer with only essential files

#define MyAppName "Bulk File Renamer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Dominic Ritzmann"
#define MyAppURL "https://github.com/dominic-ritzmann/bulk-file-renamer"
#define MyAppExeName "Bulk File Renamer.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{BULK_FILE_RENAMER_GUID_HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputBaseFilename=BulkFileRenamer_Windows_Installer
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; SetupIconFile=..\assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no
MinVersion=6.1sp1
LicenseFile=..\legal\en\eula.txt
InfoBeforeFile=..\legal\en\privacy.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
; Main executable
Source: "..\dist\Bulk File Renamer\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Essential runtime files from _internal directory
Source: "..\dist\Bulk File Renamer\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifdoesntexist

[Code]
var
  LanguagePage: TInputOptionWizardPage;
  ThemePage: TInputOptionWizardPage;

procedure InitializeWizard;
begin
  // Create language selection page
  LanguagePage := CreateInputOptionPage(wpSelectDir,
    'Language Selection', 'Choose your preferred language',
    'Please select the language for Bulk File Renamer:', True, False);
  LanguagePage.Add('English');
  LanguagePage.Add('German');
  LanguagePage.SelectedValueIndex := 0;

  // Create theme selection page
  ThemePage := CreateInputOptionPage(LanguagePage.ID,
    'Theme Selection', 'Choose your preferred theme',
    'Please select the theme for Bulk File Renamer:', True, False);
  ThemePage.Add('Light Theme');
  ThemePage.Add('Dark Theme');
  ThemePage.Add('System Default');
  ThemePage.SelectedValueIndex := 2;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = ThemePage.ID then
  begin
    // Create settings file with user preferences
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '{' + #13#10, False);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "language": "' + 
      IIf(LanguagePage.SelectedValueIndex = 0, 'en', 'de') + '",' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "theme": "' + 
      IIf(ThemePage.SelectedValueIndex = 0, 'light', 
          IIf(ThemePage.SelectedValueIndex = 1, 'dark', 'system')) + '",' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "window_geometry": {' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '    "width": 1200,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '    "height": 800,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '    "x": 100,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '    "y": 100' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  },' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "max_recent_items": 10,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "auto_clean_names": true,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "show_notifications": true,' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '  "history_file_path": "history.json"' + #13#10, True);
    SaveStringToFile(ExpandConstant('{app}\settings.json'), '}', True);
  end;
end;

function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;
