; Bulk File Renamer - NSIS Installer Script
; Copyright (c) 2024 Dominic Ritzmann
; Licensed under the MIT License
; Completely free for commercial use

!define APPNAME "Bulk File Renamer"
!define COMPANYNAME "Dominic Ritzmann"
!define DESCRIPTION "A powerful tool for bulk file renaming"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/dominic-ritzmann/bulk-file-renamer"
!define UPDATEURL "https://github.com/dominic-ritzmann/bulk-file-renamer"
!define ABOUTURL "https://github.com/dominic-ritzmann/bulk-file-renamer"
!define INSTALLSIZE 50000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\${APPNAME}"
Name "${APPNAME}"
outFile "BulkFileRenamer_Windows_Installer.exe"

!include LogicLib.nsh
!include MUI2.nsh

!define MUI_ABORTWARNING
; !define MUI_ICON "..\assets\app.ico"
; !define MUI_UNICON "..\assets\app.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\legal\en\eula.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
; Removed auto-launch checkbox to avoid drag & drop issues with elevated processes
; Users will manually start the application from desktop shortcut or start menu
!define MUI_FINISHPAGE_TEXT "Bulk File Renamer has been successfully installed on your computer.$\r$\n$\r$\nNote: If Windows Security prompts for a scan, you can safely allow it or add the application to Windows Defender exclusions for faster startup.$\r$\n$\r$\nClick Finish to close this wizard."
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "German"

Section "install"
  SetOutPath $INSTDIR
  
  ; Main executable (single-file build)
  File "..\..\dist\Bulk File Renamer.exe"
  
  ; Create settings file with default values
  FileOpen $0 "$INSTDIR\settings.json" w
  FileWrite $0 '{\r\n'
  FileWrite $0 '  "preview_auto_refresh": true,\r\n'
  FileWrite $0 '  "auto_resolve_conflicts": false,\r\n'
  FileWrite $0 '  "default_prefix": "",\r\n'
  FileWrite $0 '  "default_suffix": "",\r\n'
  FileWrite $0 '  "default_base_name": "",\r\n'
  FileWrite $0 '  "default_start_number": 1,\r\n'
  FileWrite $0 '  "theme": "Light",\r\n'
  FileWrite $0 '  "show_tooltips": true,\r\n'
  FileWrite $0 '  "confirm_before_rename": true,\r\n'
  FileWrite $0 '  "show_file_count": true,\r\n'
  FileWrite $0 '  "backup_before_rename": false,\r\n'
  FileWrite $0 '  "backup_location": "backups/",\r\n'
  FileWrite $0 '  "overwrite_existing": false,\r\n'
  FileWrite $0 '  "create_backup_folder": false,\r\n'
  FileWrite $0 '  "case_sensitive_sorting": true,\r\n'
  FileWrite $0 '  "preserve_file_attributes": true,\r\n'
  FileWrite $0 '  "log_operations": false,\r\n'
  FileWrite $0 '  "log_file": "bulk_renamer.log",\r\n'
  FileWrite $0 '  "language": "en",\r\n'
  FileWrite $0 '  "recent_folders": [],\r\n'
  FileWrite $0 '  "recent_profiles": [],\r\n'
  FileWrite $0 '  "max_recent_items": 10,\r\n'
  FileWrite $0 '  "history_file": "history.json",\r\n'
  FileWrite $0 '  "_metadata": {\r\n'
  FileWrite $0 '    "version": "1.0",\r\n'
  FileWrite $0 '    "last_updated": "2025-01-01T00:00:00.000000"\r\n'
  FileWrite $0 '  }\r\n'
  FileWrite $0 '}'
  FileClose $0
  
  ; Create shortcuts with admin privileges
  CreateShortCut "$SMPROGRAMS\${APPNAME}.lnk" "$INSTDIR\Bulk File Renamer.exe" "" "$INSTDIR\Bulk File Renamer.exe" "" "" "" "Run Bulk File Renamer"
  CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\Bulk File Renamer.exe" "" "$INSTDIR\Bulk File Renamer.exe" "" "" "" "Run Bulk File Renamer"
  
  ; Note: Removed RUNASADMIN to allow drag & drop to work properly
  ; The app will run with normal privileges instead of elevated privileges
  
  ; Registry entries
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\Bulk File Renamer.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "uninstall"
  Delete "$INSTDIR\Bulk File Renamer.exe"
  RMDir /r "$INSTDIR\_internal"
  Delete "$INSTDIR\settings.json"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
  
  Delete "$SMPROGRAMS\${APPNAME}.lnk"
  Delete "$DESKTOP\${APPNAME}.lnk"
  
  ; Note: No admin privileges registry entry to remove
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

