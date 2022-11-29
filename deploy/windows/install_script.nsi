;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "PgManage"
  OutFile "pgmanage_setup.exe"
  Unicode True

  ;Default installation folder
  InstallDir "$LOCALAPPDATA\$(^Name)"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\$(^Name)" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel user

;--------------------------------
;Interface Configuration

  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "install_header.bmp" ; optional
  !define MUI_ICON win-icon.ico
  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_LICENSE "license.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES

  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English"

;--------------------------------
;Installer Sections

Section "Program" AppFiles
  SectionIn RO

  SetOutPath "$INSTDIR"

  File /r ${SRCDIR}\*.*

  ;Store installation folder
  WriteRegStr HKCU "Software\$(^Name)" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd


Section "Start menu shortcut"
  CreateShortcut "$SMPrograms\$(^Name).lnk" "$InstDir\pgmanage-app.exe"
SectionEnd

Section "Desktop shortcut"
  CreateShortcut "$Desktop\$(^Name).lnk" "$InstDir\pgmanage-app.exe"
SectionEnd


;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_AppFiles ${LANG_ENGLISH} "Application Files."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${AppFiles} $(DESC_AppFiles)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...

  Delete "$INSTDIR\Uninstall.exe"

  RMDir /r "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\$(^Name)"
  Delete "$SMPROGRAMS\$(^Name).lnk"
  Delete "$Desktop\$(^Name).lnk"
SectionEnd