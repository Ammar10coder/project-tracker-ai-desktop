; Inno Setup script — produces a proper Windows installer
; (ProjectTrackerAI-Setup.exe) that installs the app, adds a Start Menu
; shortcut, and an optional Desktop shortcut.
;
; Requires Inno Setup 6: https://jrsoftware.org/isdl.php
; Build order:
;   1. build_windows.bat   -> creates dist\ProjectTrackerAI.exe
;   2. Open this file in Inno Setup Compiler and click Compile
;      (or run: "iscc build\installer.iss" from Command Prompt)
; Output: build\Output\ProjectTrackerAI-Setup.exe

#define MyAppName "Project Tracker AI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Mohammed Ammar"
#define MyAppExeName "ProjectTrackerAI.exe"

[Setup]
AppId={{9F2B7C2E-7A0B-4E4D-9F2C-2B1B6C1E9A11}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=ProjectTrackerAI-Setup
OutputDir=Output
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
; No admin rights required — installs to the user's local app folder.
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Ship a starter .env.example so users can create their own .env after install.
Source: "..\.env.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
