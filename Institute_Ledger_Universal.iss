#define MyAppName "Institute Ledger"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "Institute Ledger"

[Setup]
AppId={{61EA2D2E-7CB6-4B1C-A5F9-6A1DCD9F14C8}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\Institute Ledger
DefaultGroupName=Institute Ledger
UninstallDisplayName=Institute Ledger
UninstallDisplayIcon={app}\Institute_Ledger.exe
OutputDir=output
OutputBaseFilename=Institute_Ledger_Setup
SetupIconFile=app_icon.ico
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x86 x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist64\Institute_Ledger_64bit.exe"; DestDir: "{app}"; DestName: "Institute_Ledger.exe"; Check: Is64BitInstallMode; Flags: ignoreversion
Source: "dist32\Institute_Ledger_32bit.exe"; DestDir: "{app}"; DestName: "Institute_Ledger.exe"; Check: not Is64BitInstallMode; Flags: ignoreversion

Source: "first_install.flag"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Institute Ledger"; Filename: "{app}\Institute_Ledger.exe"
Name: "{autodesktop}\Institute Ledger"; Filename: "{app}\Institute_Ledger.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
Filename: "{app}\Institute_Ledger.exe"; Description: "Launch Institute Ledger"; Flags: nowait postinstall skipifsilent

