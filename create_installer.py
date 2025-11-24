"""
Build script to create a Windows installer for the Clicky Automation application.
This script requires NSIS (Nullsoft Scriptable Install System) to be installed.

You can download NSIS from: https://nsis.sourceforge.io/Download
"""

import os
import sys
import subprocess
import datetime
from PIL import Image
import tempfile

def create_ico_from_png(png_path):
    """Convert a PNG file to ICO format."""
    try:
        # Check if pillow is installed
        from PIL import Image
        
        # Create a temporary ICO file
        ico_fd, ico_path = tempfile.mkstemp(suffix='.ico')
        os.close(ico_fd)  # Close the file descriptor
        
        # Open the PNG and save as ICO
        img = Image.open(png_path)
        img.save(ico_path, format='ICO')
        
        print(f"Converted PNG to ICO: {ico_path}")
        return ico_path
    except Exception as e:
        print(f"Warning: Could not convert PNG to ICO: {e}")
        return None

# NSIS script template
NSIS_SCRIPT = r'''
; Clicky Installer Script
Unicode True

!define APP_NAME "Clicky"
!define EXE_NAME "Clicky.exe"
!define COMPANY_NAME "Kazakuba"
!define VERSION "1.0.0"
!define COPYRIGHT "Copyright (c) {year}"
!define DESCRIPTION "Desktop automation tool"
!define LICENSE_TXT "LICENSE.txt"
!define INSTALLER_NAME "Clicky_Setup.exe"
!define MAIN_APP_EXE "${{EXE_NAME}}"
!define INSTALL_TYPE "SetShellVarContext current"
!define REG_ROOT "HKCU"
!define REG_APP_PATH "Software\Microsoft\Windows\CurrentVersion\App Paths\${{MAIN_APP_EXE}}"
!define UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${{APP_NAME}}"

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Modern UI
!define MUI_ABORTWARNING
{icon_directives}

; Installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Set UI language
!insertmacro MUI_LANGUAGE "English"

Name "${{APP_NAME}}"
OutFile "${{INSTALLER_NAME}}"
InstallDir "$PROGRAMFILES\${{APP_NAME}}"
InstallDirRegKey "${{REG_ROOT}}" "${{REG_APP_PATH}}" ""

Function .onInit
    InitPluginsDir
FunctionEnd

Section "MainSection" SEC01
    ${{INSTALL_TYPE}}
    SetOutPath "$INSTDIR"
    
    ; Add files
    File "dist\${{MAIN_APP_EXE}}"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\${{APP_NAME}}\${{APP_NAME}}.lnk" "$INSTDIR\${{MAIN_APP_EXE}}"
    CreateShortCut "$DESKTOP\${{APP_NAME}}.lnk" "$INSTDIR\${{MAIN_APP_EXE}}"
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Registry information for add/remove programs
    WriteRegStr ${{REG_ROOT}} "${{REG_APP_PATH}}" "" "$INSTDIR\${{MAIN_APP_EXE}}"
    WriteRegStr ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "DisplayIcon" "$INSTDIR\${{MAIN_APP_EXE}}"
    WriteRegStr ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "DisplayVersion" "${{VERSION}}"
    WriteRegStr ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "Publisher" "${{COMPANY_NAME}}"
    
    ; Calculate and store installation size
    ${{GetSize}} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD ${{REG_ROOT}} "${{UNINSTALL_PATH}}" "EstimatedSize" "$0"
SectionEnd

Section "Uninstall"
    ${{INSTALL_TYPE}}
    
    ; Remove application files
    Delete "$INSTDIR\${{MAIN_APP_EXE}}"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\${{APP_NAME}}\${{APP_NAME}}.lnk"
    Delete "$DESKTOP\${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\${{APP_NAME}}"
    
    ; Remove directories
    RMDir "$INSTDIR"
    
    ; Remove registry keys
    DeleteRegKey ${{REG_ROOT}} "${{REG_APP_PATH}}"
    DeleteRegKey ${{REG_ROOT}} "${{UNINSTALL_PATH}}"
SectionEnd
'''

def check_nsis():
    """Check if NSIS is installed."""
    nsis_paths = [
        r"C:\Program Files\NSIS\makensis.exe",
        r"C:\Program Files (x86)\NSIS\makensis.exe"
    ]
    
    for path in nsis_paths:
        if os.path.exists(path):
            print(f"Found NSIS at: {path}")
            return path
    
    print("NSIS not found. Please install NSIS from https://nsis.sourceforge.io/Download")
    print("After installing, run this script again.")
    return None

def build_installer():
    """Build the installer using NSIS."""
    print("Starting installer build process...")
    
    # First check if we have a compiled executable
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, "dist", "Clicky.exe")
    
    if not os.path.exists(exe_path):
        print("Executable not found at:", exe_path)
        print("Please run build_app.py first to create the executable.")
        return False
    else:
        print(f"Found executable at: {exe_path}")
    
    # Check for NSIS
    nsis_exe = check_nsis()
    if not nsis_exe:
        return False
    
    # Handle icon for the installer
    print("Looking for icon files...")
    icon_path = None
    ico_temp_file = None
    icon_directives = ""
    
    # Look for existing .ico file
    ico_path = os.path.join(current_dir, "resources", "images", "app_icon.ico")
    if os.path.exists(ico_path):
        print(f"Found ICO file at: {ico_path}")
        icon_path = ico_path
    else:
        print(f"ICO file not found at: {ico_path}")
        # Try to convert PNG to ICO if PNG exists
        png_path = os.path.join(current_dir, "resources", "images", "app_icon.png")
        if os.path.exists(png_path):
            print(f"Found PNG file at: {png_path}")
            try:
                # Try to convert PNG to ICO
                ico_temp_file = create_ico_from_png(png_path)
                if ico_temp_file:
                    icon_path = ico_temp_file
            except ImportError:
                print("Warning: PIL/Pillow not installed, cannot convert PNG to ICO")
        else:
            print(f"PNG file not found at: {png_path}")
    
    # Set up icon directives for NSIS script
    if icon_path and os.path.exists(icon_path) and icon_path.lower().endswith('.ico'):
        print(f"Using icon: {icon_path}")
        # Manually create the directive string without f-strings
        icon_path_nsis = icon_path.replace("\\", "\\\\")
        mui_icon = '!define MUI_ICON "' + icon_path_nsis + '"'
        mui_unicon = '!define MUI_UNICON "' + icon_path_nsis + '"'
        icon_directives = mui_icon + '\n' + mui_unicon
    else:
        # No icon or conversion failed, use default icon
        icon_directives = ''; # Skip icon directives
        print("Warning: No valid .ico file found for the installer. Using default NSIS icon.")
    
    # Fill in the NSIS script template
    print("Preparing NSIS script...")
    script_content = NSIS_SCRIPT.format(
        year=datetime.datetime.now().year,
        icon_directives=icon_directives
    )
    
    # Write the NSIS script to a file
    script_path = os.path.join(current_dir, "installer.nsi")
    with open(script_path, "w") as f:
        f.write(script_content)
    print(f"Created NSIS script at: {script_path}")
    
    # Run NSIS to build the installer
    print("Building installer with NSIS...")
    try:
        # Capture full output
        process = subprocess.Popen(
            [nsis_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        print("NSIS Output:")
        print(stdout)
        
        if stderr:
            print("NSIS Errors:")
            print(stderr)
            
        if process.returncode == 0:
            print("\nInstaller created successfully!")
            installer_path = os.path.join(current_dir, 'ClickyAutomation_Setup.exe')
            print(f"Installer file: {installer_path}")
            if os.path.exists(installer_path):
                print(f"Verified installer exists at {installer_path}")
            else:
                print(f"Warning: Expected installer file not found at {installer_path}")
            return True
        else:
            print(f"Error building installer: NSIS returned code {process.returncode}")
            return False
    except Exception as e:
        print(f"Exception during build: {e}")
        return False
    finally:
        print("Cleaning up temporary files...")
        # Clean up the script file
        if os.path.exists(script_path):
            try:
                os.remove(script_path)
                print(f"Removed temporary script: {script_path}")
            except Exception as e:
                print(f"Failed to remove script file: {e}")
        
        # Delete temporary icon file if we created one
        if ico_temp_file and os.path.exists(ico_temp_file):
            try:
                os.remove(ico_temp_file)
                print(f"Removed temporary icon: {ico_temp_file}")
            except Exception as e:
                print(f"Failed to remove temporary icon: {e}")

if __name__ == "__main__":
    try:
        print("=== Clicky Automation Installer Builder ===")
        # Check if the executable exists first
        current_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(current_dir, "dist", "Clicky.exe")
        
        if not os.path.exists(exe_path):
            print("Executable not found. Building it first...")
            try:
                exec(open("build_app.py").read())
            except Exception as e:
                print(f"Error building executable: {e}")
                sys.exit(1)
        
        # Now build the installer
        success = build_installer()
        if success:
            print("Installer build completed successfully!")
            sys.exit(0)
        else:
            print("Installer build failed.")
            sys.exit(1)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 