import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from models.settings import Settings

def get_application_path():
    """Get the base path for the application, works for dev and PyInstaller"""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (PyInstaller)
        application_path = os.path.dirname(sys.executable)
    else:
        # If the application is run in a normal Python environment
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    return application_path

def get_data_directory():
    """Get the data directory for storing application data"""
    # Use LocalAppData for Windows
    appdata_local = os.environ.get('LOCALAPPDATA')
    if appdata_local:
        # Create app data directory
        app_data_dir = os.path.join(appdata_local, "Clicky")
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
        return app_data_dir
    else:
        # Fallback to application directory
        return get_application_path()

def main():
    """Main application entry point"""
    # Set application path
    app_path = get_application_path()
    os.chdir(app_path)
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set app details for Windows registry
    app.setOrganizationName("Kazakuba")
    app.setApplicationName("Clicky")
    
    # Get data directory
    data_dir = get_data_directory()
    
    # Load settings
    settings_path = os.path.join(data_dir, "settings.json")
    settings = Settings()
    settings.load(settings_path)
    
    # Create and show main window
    main_window = MainWindow(settings)
    main_window.show()
    
    # Save settings on exit
    app.aboutToQuit.connect(lambda: settings.save(settings_path))
    
    # Run application event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()