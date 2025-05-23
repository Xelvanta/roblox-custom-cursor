import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import base64

def find_valid_roblox_version_folder():
    local_appdata = os.environ.get("LOCALAPPDATA")
    versions_path = os.path.join(local_appdata, "Roblox", "Versions")
    
    if not os.path.isdir(versions_path):
        return None

    for subfolder in os.listdir(versions_path):
        full_path = os.path.join(versions_path, subfolder)
        content_path = os.path.join(full_path, "content")
        exe_path = os.path.join(full_path, "RobloxPlayerBeta.exe")

        if os.path.isdir(content_path) and os.path.isfile(exe_path):
            return full_path

    return None

def import_cursors_from_rcur(rcur_path):
    folder = find_valid_roblox_version_folder()
    if not folder:
        tk.Tk().withdraw()
        messagebox.showerror("Error", "Roblox version folder not found.")
        return

    cursor_filenames = ["ArrowFarCursor.png", "ArrowCursor.png", "IBeamCursor.png"]
    cursor_paths = [os.path.join(folder, "content", "textures", "Cursors", "KeyboardMouse", fn) for fn in cursor_filenames]

    try:
        with open(rcur_path, "r", encoding="utf-8") as f:
            base64_lines = [line.strip() for line in f if line.strip()]

        if len(base64_lines) != len(cursor_filenames):
            raise ValueError("The .rcur file should contain exactly {} base64 lines.".format(len(cursor_filenames)))

        for i, b64data in enumerate(base64_lines):
            decoded = base64.b64decode(b64data)
            with open(cursor_paths[i], "wb") as img_file:
                img_file.write(decoded)

        tk.Tk().withdraw()
        messagebox.showinfo("Success", "Cursors imported and applied successfully.")

    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("Error", "Failed to import cursors:\\n{}".format(e))

def main():
    if len(sys.argv) < 2:
        sys.exit(0)  # Silent exit if no file passed

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        sys.exit(0)

    import_cursors_from_rcur(file_path)

if __name__ == "__main__":
    main()