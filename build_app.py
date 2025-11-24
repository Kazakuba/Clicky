"""
Build script to create a standalone executable for the Clicky application
using PyInstaller.

This script will create a single .exe file that can be run on any Windows system
without requiring Python to be installed.
"""

import os
import sys
import subprocess
import shutil
import time
import signal
import psutil

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller.")
            return False

def check_psutil():
    """Check if psutil is installed, install if not."""
    try:
        import psutil
        print("psutil is already installed.")
        return True
    except ImportError:
        print("psutil not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install psutil. Will skip process termination.")
            return False

def terminate_existing_app():
    """Terminate any running instances of the application."""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            # Check if the process name contains our app name
            if 'Clicky.exe' in proc.info['name'] or 'ClickyAutomation.exe' in proc.info['name']:
                print(f"Terminating existing application process: {proc.info['name']} (PID: {proc.info['pid']})")
                try:
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()
                    # Give it a moment to terminate gracefully
                    process.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    print(f"Could not terminate process {proc.info['pid']} gracefully, attempting to kill...")
                    try:
                        process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        print(f"Failed to kill process {proc.info['pid']}.")
        print("Process termination complete.")
        # Wait a moment to ensure all file handles are released
        time.sleep(1)
    except Exception as e:
        print(f"Error when trying to terminate existing processes: {e}")

def clean_dist_folder():
    """Try to clean up the dist folder before building."""
    dist_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    
    if os.path.exists(dist_folder):
        try:
            print(f"Cleaning dist folder: {dist_folder}")
            # Try to rename or delete the exe file first
            exe_path = os.path.join(dist_folder, "Clicky.exe")
            old_exe_path = os.path.join(dist_folder, "Clicky.exe.old")
            
            if os.path.exists(exe_path):
                try:
                    # Try to rename it first (sometimes works when file is in use)
                    if os.path.exists(old_exe_path):
                        os.remove(old_exe_path)  # Remove previous .old file if it exists
                    os.rename(exe_path, old_exe_path)
                    os.remove(old_exe_path)  # Try to remove it after renaming
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not remove existing executable: {e}")
                    print("Will try to continue anyway.")
        except Exception as e:
            print(f"Warning: Error cleaning dist folder: {e}")
            print("Will try to continue with the build anyway.")

def build_exe():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define icon path
    icon_path = os.path.join(current_dir, "resources", "images", "app_icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(current_dir, "resources", "images", "app_icon.png")
    
    icon_option = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    
    # Check if PyQt6 is installed
    try:
        import PyQt6
        print("PyQt6 is installed. Adding necessary hidden imports...")
    except ImportError:
        print("Warning: PyQt6 not found. Please install with: pip install PyQt6")
        return False
    
    # First terminate any running instances of the app
    if check_psutil():
        terminate_existing_app()
    
    # Clean the dist folder to avoid permission issues
    clean_dist_folder()
    
    # PyInstaller command with PyQt6 hidden imports
    cmd = [
        "pyinstaller",
        "--name=Clicky",
        "--onefile",  # Create a single executable
        "--windowed",  # No console window
        "--clean",  # Clean PyInstaller cache and remove temp files
        f"{icon_option}",
        "--add-data=resources;resources",  # Include resources folder
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets", 
        "--hidden-import=PyQt6.sip",
        # Add the following to ensure all QtWidgets submodules are included
        "--collect-submodules=PyQt6.QtWidgets",
        "main.py"  # Main script
    ]
    
    # Filter out empty options
    cmd = [item for item in cmd if item]
    
    # Run PyInstaller
    try:
        subprocess.check_call(cmd)
        
        print("\nBuild completed successfully!")
        print(f"Executable created at: {os.path.join(current_dir, 'dist', 'Clicky.exe')}")
        
        # Create a shortcut for easier access
        try:
            # Clean up the build directory if it exists
            build_dir = os.path.join(current_dir, "build")
            if os.path.exists(build_dir):
                print("Cleaning up build directory...")
                shutil.rmtree(build_dir)
            
            print("\nYou can now run Clicky.exe from the 'dist' folder.")
            return True
        except Exception as e:
            print(f"Warning: Could not clean up build directory: {e}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        print("Try closing any running instances of the application and restarting your file explorer.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if check_pyinstaller():
        success = build_exe()
        if not success:
            print("Failed to build executable. See error messages above.")
            sys.exit(1)
    else:
        print("Failed to install PyInstaller. Please install it manually with:")
        print("pip install pyinstaller")
        sys.exit(1) 