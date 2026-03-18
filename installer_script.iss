[Setup]
AppName=FB Profile Manager
AppVersion=1.0
AppPublisher=Roshaan
DefaultDirName={autopf}\FBProfileManager
DefaultGroupName=FB Profile Manager
OutputBaseFilename=FBProfileManager_Setup
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
Source: "{#SourcePath}\dist\FBProfileManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\FB Profile Manager"; Filename: "{app}\FBProfileManager.exe"; IconFilename: "{app}\FBProfileManager.exe"
Name: "{commondesktop}\FB Profile Manager"; Filename: "{app}\FBProfileManager.exe"; IconFilename: "{app}\FBProfileManager.exe"; Tasks: desktopicon
Name: "{group}\Uninstall FB Profile Manager"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\FBProfileManager.exe"; Description: "Launch FB Profile Manager"; Flags: nowait postinstall skipifsilent