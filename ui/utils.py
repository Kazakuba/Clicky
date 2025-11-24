import os
import sys
import shutil

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    return os.path.join(base_path, relative_path)

def get_data_directory():
    appdata_local = os.environ.get('LOCALAPPDATA')
    if appdata_local:
        app_data_dir = os.path.join(appdata_local, "Clicky")
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
            
        themes_dir = os.path.join(app_data_dir, "themes")
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
            
        return app_data_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

def load_stylesheet(theme="Default"):
    if theme not in ["Default", "Dark", "Light"]:
        theme = "Default"
    
    appdata_dir = get_data_directory()
    themes_dir = os.path.join(appdata_dir, "themes")
    user_theme_file = os.path.join(themes_dir, f"style_{theme.lower()}.qss")
    
    builtin_theme_file = get_resource_path(f"resources/styles/style_{theme.lower()}.qss")
    original_style = get_resource_path("resources/styles/style.qss")
    default_style = get_resource_path("resources/styles/style_default.qss")
    
    if os.path.exists(user_theme_file):
        theme_file = user_theme_file
    elif os.path.exists(builtin_theme_file):
        theme_file = builtin_theme_file
        
        try:
            if not os.path.exists(user_theme_file):
                shutil.copy(builtin_theme_file, user_theme_file)
                print(f"Copied built-in theme to user directory: {user_theme_file}")
        except Exception as e:
            print(f"Warning: Could not copy theme to user directory: {e}")
    else:
        print(f"Theme file not found: {builtin_theme_file}")
        
        if os.path.exists(default_style):
            theme_file = default_style
            try:
                user_default_file = os.path.join(themes_dir, "style_default.qss")
                if not os.path.exists(user_default_file):
                    shutil.copy(default_style, user_default_file)
            except Exception as e:
                print(f"Warning: Could not copy default theme: {e}")
        elif os.path.exists(original_style):
            theme_file = original_style
            try:
                user_default_file = os.path.join(themes_dir, "style_default.qss")
                if not os.path.exists(user_default_file):
                    shutil.copy(original_style, user_default_file)
            except Exception as e:
                print(f"Warning: Could not copy original style: {e}")
        else:
            print(f"No stylesheet files found")
            return ""

    try:
        print(f"Loading stylesheet from: {theme_file}")
        with open(theme_file, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading stylesheet: {e}")
        return ""