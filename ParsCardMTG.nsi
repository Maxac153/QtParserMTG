Name "ParsCard"
OutFile "ParsCard_Setup.exe"

InstallDir $PROGRAMFILES\ParsCard
InstallDirRegKey HKLM "Software\ParsCard" "Install_Dir"

Section "ParsCard (required)"
  SectionIn RO
  SetOutPath $INSTDIR
  
  File /r "C:\Users\Turgor\Desktop\dist\logo"
  File /r "C:\Users\Turgor\Desktop\dist\src"
  File "C:\Users\Turgor\Desktop\dist\ParsCard.exe"
  
  WriteRegStr HKLM SOFTWARE\ParsCard "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ParsCard" "DisplayName" "ParsCard"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ParsCard" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Start Menu Shortcuts (required)"
  CreateDirectory "$SMPROGRAMS\ParsCard"
  CreateShortcut "$SMPROGRAMS\ParsCard\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$SMPROGRAMS\ParsCard\ParsCard.lnk" "$INSTDIR\ParsCard.exe" "" "$INSTDIR\ParsCard.exe" 0
  CreateShortcut "$DESKTOP\ParsCard.lnk" "$INSTDIR\ParsCard.exe" "" "$INSTDIR\ParsCard.exe" 0
  CreateShortcut "$QUICKLAUNCH\ParsCard.lnk" "$INSTDIR\ParsCard.exe" "" "$INSTDIR\ParsCard.exe" 0
SectionEnd

Section "Uninstall"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ParsCard"
  DeleteRegKey HKLM SOFTWARE\ParsCard
  Delete $INSTDIR\logo
  Delete $INSTDIR\src
  Delete $INSTDIR\ParsCard.exe
  Delete $INSTDIR\uninstall.exe
  Delete "$SMPROGRAMS\ParsCard\*.*"
  RMDir "$SMPROGRAMS\ParsCard"
  RMDir "$INSTDIR"
SectionEnd