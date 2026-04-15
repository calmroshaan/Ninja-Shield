[Setup]
AppName=Ninja Shield
AppVersion=V4.1.2
AppPublisher=Roshaan
DefaultDirName={autopf}\NinjaShield
DefaultGroupName=Ninja Shield
OutputBaseFilename=NinjaShield_Setup
SetupIconFile={#SourcePath}\icon.ico
OutputDir={#SourcePath}\installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{#SourcePath}\dist\NinjaShield\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Ninja Shield"; Filename: "{app}\NinjaShield.exe"; IconFilename: "{app}\NinjaShield.exe"
Name: "{commondesktop}\Ninja Shield"; Filename: "{app}\NinjaShield.exe"; IconFilename: "{app}\NinjaShield.exe"; Tasks: desktopicon
Name: "{group}\Uninstall Ninja Shield"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\NinjaShield.exe"; Description: "Launch Ninja Shield"; Flags: nowait postinstall skipifsilent