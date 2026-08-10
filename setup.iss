[Setup]
AppName=CRM_BoletosZap
AppVersion=1.0.0
AppPublisher=CRM BoletosZap Inc.
DefaultDirName= {localappdata}\Programs\CRM_BoletosZap
DefaultGroupName=CRM_BoletosZap
OutputBaseFilename=CRM_BoletosZap_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\CRM_BoletosZap.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CRM_BoletosZap"; Filename: "{app}\CRM_BoletosZap.exe"
Name: "{autodesktop}\CRM_BoletosZap"; Filename: "{app}\CRM_BoletosZap.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CRM_BoletosZap.exe"; Description: "{cm:LaunchProgram,CRM BoletosZap}"; Flags: nowait postinstall skipifsilent
