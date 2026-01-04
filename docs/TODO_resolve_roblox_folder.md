TODO: Replace the `find_valid_roblox_folder` in the main app with a function such as this one, which uses the registry key to get the version folder.

```py
import winreg

def resolve_roblox_folder():
    """
    Locate the currently registered Roblox version folder using the registry.
    If the registry key or value does not exist, show an error and exit.

    :raises SystemExit: If the Roblox version cannot be determined.
    :rtype: str
    """
    local_appdata = os.environ.get("LOCALAPPDATA")
    versions_path = os.path.join(local_appdata, "Roblox", "Versions")

    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"roblox-player\shell\open\command") as key:
            version_folder = winreg.QueryValueEx(key, "version")[0]  # returns (value, type)
            if version_folder:
                exe_path = os.path.join(versions_path, version_folder, "RobloxPlayerBeta.exe")
                content_path = os.path.join(versions_path, version_folder, "content")
                if os.path.isfile(exe_path) and os.path.isdir(content_path):
                    return os.path.join(versions_path, version_folder)
    except FileNotFoundError:
        # Registry key or value doesn't exist
        pass

    # If we reach here, registry lookup failed
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "No registered Roblox version found in the registry.")
    root.destroy()
    sys.exit(1)
```

Current function for reference:

```py
def find_valid_roblox_version_folder():
    """
    Locate and validate the existence of the Roblox 'Versions' folder on a Windows system.

    This function attempts to construct the path to the Roblox Versions directory within
    the user's local app data directory. If the directory does not exist, it displays
    an error message in a GUI window and exits the program.

    :raises SystemExit: If the Roblox Versions folder is not found.
    :rtype: None
    """
    local_appdata = os.environ.get("LOCALAPPDATA")
    versions_path = os.path.join(local_appdata, "Roblox", "Versions")

    if not os.path.isdir(versions_path):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "Roblox Versions folder not found.")
        root.destroy()
        sys.exit(1)

    for subfolder in os.listdir(versions_path):
        full_path = os.path.join(versions_path, subfolder)
        content_path = os.path.join(full_path, "content")
        exe_path = os.path.join(full_path, "RobloxPlayerBeta.exe")

        if os.path.isdir(content_path) and os.path.isfile(exe_path):
            # Uncomment this line as needed to debug the matched folder
            # print(f"Matched folder: {full_path}")
            return full_path
```
