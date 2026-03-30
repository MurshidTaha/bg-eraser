!define APPNAME "BG Eraser"
!define DESCRIPTION "Offline AI Background Remover"
!define VERSION "1.0"

# The name of the installer file it will generate
OutFile "BG_Eraser_Setup.exe"

# Default installation directory (64-bit Program Files)
InstallDir "$PROGRAMFILES64\${APPNAME}"

# Request admin privileges to write to Program Files
RequestExecutionLevel admin

# Installer pages
Page directory
Page instfiles

# --- INSTALLATION SECTION ---
Section "Install"
    
    # 1. Copy the main PyInstaller application files
    SetOutPath "$INSTDIR"
    # This grabs EVERYTHING inside your dist/BGEraser folder
    File /r "dist\BGEraser\*"

    # 2. Pre-install the AI Model so the app is 100% offline immediately
    # rembg always looks for the model in the user's home directory
    SetOutPath "$PROFILE\.u2net"
    # This requires u2net.onnx to be in the same folder as this .nsi script before compiling
    File "u2net.onnx"

    # 3. Create a Desktop Shortcut
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\BGEraser.exe"

    # 4. Create Start Menu Shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\BGEraser.exe"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    # 5. Create the Uninstaller file
    WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

# --- UNINSTALLATION SECTION ---
Section "Uninstall"

    # Remove the application folder
    RMDir /r "$INSTDIR"
    
    # Remove the Desktop shortcut
    Delete "$DESKTOP\${APPNAME}.lnk"
    
    # Remove the Start Menu shortcuts
    RMDir /r "$SMPROGRAMS\${APPNAME}"

    # Note: We intentionally DO NOT delete the .u2net model folder during uninstall 
    # just in case the user has other apps that use it.

SectionEnd