# Clicky

A desktop automation tool that allows you to create and run custom workflows for automating repetitive tasks.

## Features

- Create and manage automated workflows
- Add multiple actions to each workflow
- Record and replay mouse clicks and keyboard inputs
- Run workflows in the background with system tray support
- Support for multiple themes (Light, Dark, Default)

## Running the Application

### Standalone Executable (Recommended)

The easiest way to run the application is to use the standalone executable:

1. **Download the installer**:
   Download and run `Clicky_Setup.exe` to install the application with desktop and start menu shortcuts.

2. **Or use the portable version**:
   Simply run `Clicky.exe` from the `dist` folder.

### Development Mode

To run the application during development:

```
python main.py
```

## System Tray Functionality

When "Run in background" is enabled in settings (default: disabled):

- The application will minimize to the system tray when closed
- Right-click the tray icon to access options:
  - Show Window: Restore the main window
  - Exit: Completely exit the application
- Single-click the tray icon to toggle the window visibility

To completely exit the application, either:
1. Right-click the tray icon and select "Exit"
2. Disable "Run in background" in settings before closing the window

## Themes

The application supports multiple themes:
- Default
- Dark
- Light

You can change the theme in the Settings dialog. The theme will be applied immediately to all open windows.

## Changing the Application Icon

The application includes utilities to easily change the application icon:

1. **Using the PowerShell script**:
   ```
   .\change_icon.ps1 path\to\your\icon.png
   ```

2. **Using the batch file**:
   ```
   change_icon.bat path\to\your\icon.jpg
   ```

3. **Or simply drag and drop** an image file onto `change_icon.bat`

These scripts will:
- Convert your image to a proper Windows ICO file with multiple resolutions
- Rebuild the application with the new icon
- Create a new installer with the updated icon

## Building from Source

### Requirements

- Python 3.6 or higher
- PyQt6
- PyAutoGUI
- Pillow (for icon generation)
- PyInstaller (for building the executable)
- NSIS (for creating the installer)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/clicky.git
   cd clicky
   ```

2. Install dependencies:
   ```
   python -m venv venv 
   
   pip install PyQt6 pyautogui pillow pyinstaller
   ```

3. Run the application:
   ```
   python main.py
   ```

### Building the Executable

```
python build_app.py
```

This will create a standalone `Clicky.exe` in the `dist` folder.

### Creating an Installer

1. Install NSIS from https://nsis.sourceforge.io/Download
2. Run the installer script:
   ```
   python create_installer.py
   ```

This will create a Windows installer (`Clicky_Setup.exe`) in the project root directory.

## Troubleshooting

### Missing Icons in Taskbar
If the taskbar icon doesn't appear, make sure you have the file `app_icon.ico` in the `resources/images` directory.

### Theme Not Working
If themes don't apply correctly:
1. Check that your theme files exist in `resources/styles/` with proper names:
   - `style_default.qss`
   - `style_dark.qss`
   - `style_light.qss`
2. Rebuild the application using `python build_app.py`

### PyQt6 Missing
If you get an error about missing PyQt6 module:
```
pip install PyQt6
```
Then rebuild the application.

## Developer Information

### Project Structure

- `ui/`: User interface components
- `controllers/`: Business logic
- `models/`: Data models
- `services/`: Service classes for external interactions
- `resources/`: Assets like icons, stylesheets, etc.
- `workflows/`: Directory where workflows are stored
- `main.py`: Application entry point
- `build_app.py`: Script for building the executable
- `create_installer.py`: Script for creating the installer

### Adding New Themes

To add a new theme:
1. Create a new QSS file in `resources/styles/` named `style_themename.qss`
2. Update the `Settings` and `SettingsDialog` classes to include the new theme
3. Add the theme name to the validation in `utils.py`