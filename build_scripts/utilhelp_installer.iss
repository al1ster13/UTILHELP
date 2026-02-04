[Setup]
AppId={{F7E8D9C6-B5A4-3210-9876-543210FEDCBA}
AppName=UTILHELP
AppVersion=1.0
AppVerName=UTILHELP 1.0
AppPublisher=al1ster13
AppPublisherURL=https://github.com/al1ster13/UTILHELP
AppSupportURL=https://github.com/al1ster13/UTILHELP/issues
AppUpdatesURL=https://github.com/al1ster13/UTILHELP/releases
DefaultDirName={autopf}\UTILHELP
DefaultGroupName=UTILHELP
AllowNoIcons=yes
LicenseFile=..\LICENSE
InfoBeforeFile=..\docs\INSTALL_INFO.md
OutputDir=..\installer_output
OutputBaseFilename=UTILHELP_Setup_v1.0
SetupIconFile=..\Icons\utilhelp.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
CreateUninstallRegKey=yes
UninstallDisplayName=UTILHELP
UninstallDisplayIcon={app}\utilhelp.ico
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousSetupType=yes
UsePreviousLanguage=yes
WizardImageFile=..\Icons\installer2.png
WizardSmallImageFile=..\Icons\utilhelplogo24.png
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no
DisableWelcomePage=no
CreateAppDir=yes
VersionInfoVersion=1.0.0.0
VersionInfoCompany=al1ster13
VersionInfoDescription=UTILHELP Setup - Universal Windows Helper
VersionInfoTextVersion=1.0
VersionInfoCopyright=Copyright (C) 2026 al1ster13
VersionInfoProductName=UTILHELP
VersionInfoProductVersion=1.0.0.0
VersionInfoProductTextVersion=1.0

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startmenu"; Description: "Создать ярлык в меню Пуск"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\dist\UTILHELP\UTILHELP.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\UTILHELP\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "LICENSE,PORTABLE_MODE.txt"
Source: "..\Icons\utilhelp.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LICENSE"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\UTILHELP"; Filename: "{app}\UTILHELP.exe"; IconFilename: "{app}\utilhelp.ico"; Comment: "Универсальный помощник для Windows"; Tasks: startmenu
Name: "{autodesktop}\UTILHELP"; Filename: "{app}\UTILHELP.exe"; IconFilename: "{app}\utilhelp.ico"; Comment: "Универсальный помощник для Windows"; Tasks: desktopicon
Name: "{group}\{cm:UninstallProgram,UTILHELP}"; Filename: "{uninstallexe}"; Tasks: startmenu

[Registry]

Root: HKCR; Subkey: ".utilhelp"; ValueType: string; ValueName: ""; ValueData: "UTILHELPFile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "UTILHELPFile"; ValueType: string; ValueName: ""; ValueData: "UTILHELP File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "UTILHELPFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\utilhelp.ico"
Root: HKCR; Subkey: "UTILHELPFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\UTILHELP.exe"" ""%1"""

[Run]
Filename: "{app}\UTILHELP.exe"; Description: "{cm:LaunchProgram,UTILHELP}"; Flags: nowait postinstall skipifsilent runascurrentuser

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\Temp\UTILHELPTEMP"
Type: filesandordirs; Name: "{localappdata}\Temp\UTILHELP"
Type: filesandordirs; Name: "{localappdata}\Temp\UH"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: files; Name: "{app}\PORTABLE_MODE.txt"

[Code]
function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  if (Version.Major < 10) then
  begin
    MsgBox('UTILHELP требует Windows 10 или более новую версию.', mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

function IsDotNetDetected(version: string; service: cardinal): boolean;
var
    key: string;
    install, release, serviceCount: cardinal;
    check: boolean;
begin
    key := 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\';
    
    if RegQueryDWordValue(HKLM, key, 'Release', release) then
    begin
        check := release >= 461808; // .NET 4.7.2
        Result := check;
    end
    else
        Result := false;
end;

function IsUpgrade(): Boolean;
var
  PrevPath: String;
  PrevVersion: String;
begin
  PrevPath := '';
  PrevVersion := '';
  Result := RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{F7E8D9C6-B5A4-3210-9876-543210FEDCBA}_is1', 'InstallLocation', PrevPath);
  if Result then
  begin
    Result := DirExists(PrevPath) and FileExists(PrevPath + '\UTILHELP.exe');

    if Result then
    begin
      if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{F7E8D9C6-B5A4-3210-9876-543210FEDCBA}_is1', 'DisplayVersion', PrevVersion) then
      begin
        Result := (PrevVersion <> '') and (PrevVersion <> '1.0');
      end;
    end;
  end;
end;

procedure CopyDir(SourceDir, DestDir: String);
var
  FindRec: TFindRec;
  SourcePath, DestPath: String;
begin
  CreateDir(DestDir);
  if FindFirst(SourceDir + '\*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Name <> '.') and (FindRec.Name <> '..') then
        begin
          SourcePath := SourceDir + '\' + FindRec.Name;
          DestPath := DestDir + '\' + FindRec.Name;
          
          if FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY <> 0 then
            CopyDir(SourcePath, DestPath)
          else
            FileCopy(SourcePath, DestPath, False);
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

procedure BackupUserDataForUpgrade();
var
  AppDir, BackupDir: String;
begin
  if IsUpgrade() then
  begin
    AppDir := ExpandConstant('{app}');
    BackupDir := ExpandConstant('{tmp}\UTILHELP_Backup');
    
    CreateDir(BackupDir);
    
    if DirExists(AppDir + '\UHDOWNLOAD') then
      CopyDir(AppDir + '\UHDOWNLOAD', BackupDir + '\UHDOWNLOAD');
    if DirExists(AppDir + '\cache') then
      CopyDir(AppDir + '\cache', BackupDir + '\cache');
    if DirExists(AppDir + '\data') then
      CopyDir(AppDir + '\data', BackupDir + '\data');
    if FileExists(AppDir + '\settings.db') then
      FileCopy(AppDir + '\settings.db', BackupDir + '\settings.db', False);
  end;
end;

procedure RestoreUserDataAfterUpgrade();
var
  AppDir, BackupDir: String;
begin
  AppDir := ExpandConstant('{app}');
  BackupDir := ExpandConstant('{tmp}\UTILHELP_Backup');
  if DirExists(BackupDir) then
  begin
    if DirExists(BackupDir + '\UHDOWNLOAD') then
      CopyDir(BackupDir + '\UHDOWNLOAD', AppDir + '\UHDOWNLOAD');
    if DirExists(BackupDir + '\cache') then
      CopyDir(BackupDir + '\cache', AppDir + '\cache');
    if DirExists(BackupDir + '\data') then
      CopyDir(BackupDir + '\data', AppDir + '\data');
    if FileExists(BackupDir + '\settings.db') then
      FileCopy(BackupDir + '\settings.db', AppDir + '\settings.db', False);
    
    DelTree(BackupDir, True, True, True);
  end;
end;

procedure BackupUserSettings();
var
  SourcePath, DestPath: string;
begin
  SourcePath := ExpandConstant('{localappdata}\UTILHELP\settings.db');
  DestPath := ExpandConstant('{localappdata}\UTILHELP\settings_backup.db');
  if FileExists(SourcePath) then
  begin
    FileCopy(SourcePath, DestPath, False);
  end;
end;

procedure RestoreUserSettings();
var
  SourcePath, DestPath: string;
begin
  SourcePath := ExpandConstant('{localappdata}\UTILHELP\settings_backup.db');
  DestPath := ExpandConstant('{localappdata}\UTILHELP\settings.db');
  if FileExists(SourcePath) then
  begin
    FileCopy(SourcePath, DestPath, False);
    DeleteFile(SourcePath);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    BackupUserDataForUpgrade();
    BackupUserSettings();
  end;
  
  if CurStep = ssPostInstall then
  begin
    RestoreUserDataAfterUpgrade();
    RestoreUserSettings();
    DeleteFile(ExpandConstant('{app}\README.md'));
    DeleteFile(ExpandConstant('{app}\COPYRIGHT.md'));
    DeleteFile(ExpandConstant('{app}\docs\README.md'));
    DeleteFile(ExpandConstant('{app}\docs\COPYRIGHT.md'));
    if IsUpgrade() then
    begin
      MsgBox('UTILHELP успешно обновлен!' + #13#10 + 
             'Все ваши данные и настройки сохранены.', 
             mbInformation, MB_OK);
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  if CheckForMutexes('UTILHELP_MUTEX') then
  begin
    Result := 'UTILHELP в данный момент запущен. Пожалуйста, закройте программу и повторите попытку.';
    exit;
  end;
  Result := '';
end;

function IsProcessRunning(ProcessName: String): Boolean;
var
  ResultCode: Integer;
  WbemLocator, WbemServices, WbemObjectSet: Variant;
begin
  Result := False;
  try
    WbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    WbemServices := WbemLocator.ConnectServer('localhost', 'root\cimv2');
    WbemObjectSet := WbemServices.ExecQuery('SELECT * FROM Win32_Process WHERE Name="' + ProcessName + '"');
    
    if WbemObjectSet.Count > 0 then
      Result := True;
  except
    if Exec('cmd', '/c tasklist /FI "IMAGENAME eq ' + ProcessName + '" | find /I "' + ProcessName + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      Result := (ResultCode = 0);
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
begin
  if IsProcessRunning('UTILHELP.exe') then
  begin
    if MsgBox('UTILHELP в данный момент запущен. Для продолжения удаления необходимо закрыть программу.' + #13#10#13#10 + 
              'Закрыть UTILHELP и продолжить удаление?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      if Exec('taskkill', '/f /im UTILHELP.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      begin
        Sleep(2000);
        
        if IsProcessRunning('UTILHELP.exe') then
        begin
          MsgBox('Не удалось закрыть UTILHELP. Пожалуйста, закройте программу вручную и повторите попытку удаления.', 
                 mbError, MB_OK);
          Result := False;
        end
        else
        begin
          MsgBox('UTILHELP успешно закрыт. Продолжаем удаление...', mbInformation, MB_OK);
          Result := True;
        end;
      end
      else
      begin
        MsgBox('Не удалось закрыть UTILHELP. Пожалуйста, закройте программу вручную и повторите попытку удаления.', 
               mbError, MB_OK);
        Result := False;
      end;
    end
    else
      Result := False;
  end
  else
    Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Response: Integer;
  AppDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppDir := ExpandConstant('{app}');
    Response := MsgBox('Удалить пользовательские данные?' + #13#10 + 
                       '• Скачанные файлы (UHDOWNLOAD)' + #13#10 +
                       '• Кэш и настройки' + #13#10#13#10 +
                       'Эти данные можно будет использовать при переустановке.',
                       mbConfirmation, MB_YESNO);
    
    if Response = IDYES then
    begin
      DelTree(AppDir + '\UHDOWNLOAD', True, True, True);
      DelTree(AppDir + '\cache', True, True, True);
      DelTree(AppDir + '\data', True, True, True);
      DeleteFile(AppDir + '\settings.db');
      MsgBox('Пользовательские данные удалены.', mbInformation, MB_OK);
    end
    else
    begin
      MsgBox('Пользовательские данные сохранены в папке:' + #13#10 + AppDir, mbInformation, MB_OK);
    end;
  end;
end;