import base64
import ctypes
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import urllib.parse
import webbrowser
from io import BytesIO
from tkinter import filedialog, messagebox, PhotoImage

from PIL import Image, ImageTk

# Uncomment these lines to test enforcement on posix os
# from unittest.mock import patch
# @patch('os.name', 'posix')

# Enforce Windows-only execution
def enforce_nt_os():
    """
    Enforce that the application runs only on Windows (NT-based) operating systems.

    This function checks the operating system and, if it is not Windows, displays an error
    message using a GUI dialog box and then exits the program with a non-zero status code.

    Uses `tkinter` for displaying the error message in a graphical window.

    :raises SystemExit: If the operating system is not Windows (i.e., ``os.name != 'nt'``).
    :rtype: None
    """
    if os.name != "nt":
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "This application is only supported on Windows.")
        root.destroy()
        sys.exit(1)

enforce_nt_os()

# --- Utility functions ---

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

    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "No valid Roblox version folder found.")
    root.destroy()
    sys.exit(1)

def load_cursor_images(folder_path):
    """
    Load and resize specific cursor images from a given folder.

    This function looks for three specific image files in the specified directory:
    "ArrowFarCursor.png", "ArrowCursor.png", and "IBeamCursor.png". If found, each image
    is resized to 64x64 pixels using LANCZOS resampling and returned with its label and full path.
    If a file is missing, `None` is returned in place of the image.

    :param folder_path: The path to the folder containing the cursor images.
    :type folder_path: str
    :return: A list of tuples, each containing a label (str), a PIL.Image object or None,
             and the full path to the image file.
    :rtype: list[tuple[str, PIL.Image.Image | None, str]]
    """
    filenames = ["ArrowFarCursor.png", "ArrowCursor.png", "IBeamCursor.png"]
    labels = ["Arrow Far", "Arrow", "I-Beam"]
    result = []
    for filename, label in zip(filenames, labels):
        full_path = os.path.join(folder_path, filename)
        if os.path.exists(full_path):
            img = Image.open(full_path).resize((64, 64), Image.Resampling.LANCZOS)
            result.append((label, img, full_path))
        else:
            result.append((label, None, full_path))
    return result

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    """
    Draw a rounded rectangle on a tkinter canvas.

    This function creates a polygon that approximates a rectangle with rounded corners
    using Bézier smoothing. The rectangle is drawn between the points (x1, y1) and (x2, y2),
    with the specified corner radius.

    Additional styling options (such as fill, outline, width, etc.) can be passed
    via keyword arguments and will be forwarded to `canvas.create_polygon`.

    :param canvas: The tkinter canvas to draw on.
    :type canvas: tkinter.Canvas
    :param x1: The x-coordinate of the top-left corner.
    :type x1: int | float
    :param y1: The y-coordinate of the top-left corner.
    :type y1: int | float
    :param x2: The x-coordinate of the bottom-right corner.
    :type x2: int | float
    :param y2: The y-coordinate of the bottom-right corner.
    :type y2: int | float
    :param radius: The radius of the rounded corners. Defaults to 20.
    :type radius: int | float
    :param kwargs: Additional keyword arguments forwarded to `create_polygon`.
    :return: The ID of the created polygon object on the canvas.
    :rtype: int
    """
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    canvas.create_polygon(points, smooth=True, **kwargs)

# --- Base64 Strings for Default Images ---

# Arrow Far: assets/ArrowFarCursor.png
# Arrow: assets/ArrowCursor.png
# I-Beam: assets/IBeamCursor.png
default_cursor_base64 = {
    "Arrow Far": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAP3SURBVHgB7Zg7TBRRFIbPzsy+WFYeSwQUCCHEGkNjQkIorChIJKEkamEsjDEx1IaG2hZiDwWFjfYUEI2gFRBjASGQyCNZgUV2dmZ2xv8Ms+tKeIiMAyznS07uvDPnv/89984QCYIgCIIgCIIgCIIgCIIgCIIgCIIgCIIg/Eeqq6sf1tbW/kAsp1Kph3SNCDmOE+LEV1ZWHI6Ojg4HIjzic1TmcIIKQoMAToGCCDj2mMpcBDf51tbWWKkAR4hQfrDt0Sjt7e1RJHnjsADXwQmhnp4erbGxsSKZTKaOEqBUhHKsCZyMhqgEN48ToFQEzBTl4wQeAp2dneG6urpkRUVF40kClKUTvBoQ5vEPAW6dJkA51oSiAHDBXwlQbk5wh8BZHHCECA+wS36hULD885u3tLTQyMgI2bb9KBQKqeSTEzQKEK4BDHqe4ABO5sTrZ2Zm/tifnp4m3F6NTXV4eNhBuI+lq4JXBCMnDYHt7e3idnd3Nxc/N2pqagrteH19fQLP0bznnYtAhwB6j5tje2xiYoIGBweL+729vW6LRL+g+Yx4m8/nXyP4vZWQ98CrRHEWQDG7XeqA8fHxYm/D6kU3tLW1ZXDtfSyI7mL1eIedAxdU4TlR8qEDVQoW91sgm82GkQgn8LKqqorm5uZoaGiIz+8h0js7O5X9/f0Ui8VoY2MjMjs7m7Us66OqqkY8HjegjYlnWKgB9tTU1LlqQKAW8oogfwbHdV2vRIKfcPi2d3oPRfEF2g5FUZ4vLS0Ri8OFsK+vL4PkO2F9FmJ/d3dXx3UmwqJzFsGga4D7skjQSSQSNloe8HM8xpH8M+x/RbzHsb3R0VH3nq6uLmpubk4i+ZRpmno0GjXIh8QLBCqAV7XZBg4StZHQimEYj5H8E5xbgCty6OE0rnk3NjZG8/PzrgNWV1cJApjhcNjY2toyBwYG8riG49wiXMQQUJqamiKZTCaG5BORSCQKATS0Si6X48vgdvUe4g2v+LxCv6ZpWs/m5uZ3bLMDfEmeuYgh4KytrdlI2ERSWbhgH9t7SDaD3v+JxLOIDxDlFY59wz2zaJ+i6O1g/uf/CacuoM70ThQwBRdgU0NCGgRQ+RgHbK4iIrB6HG0MrYZrLS5+SBqmyezTVXYA47nAxji2MMUZDQ0NOuZ5HXN+FlOjDjewK9gFOhzBNcHAton7bAwdB/e5LiKfCHodUGRhYcEVY3Jy0k6n0yyIg562l5eXHf5OgBAOimIePc/TXQ5TZm59fd1aXFxk//smwGVbSir4XFbhDA3Ja+h9t4MwFCyu/nRgfd/sf1lR+Mcp2gj/OqeDJW8YDlH9+Pg5zGX9mAjR73dz1w4lIQiC4Bu/ABsKDEIN5oAYAAAAAElFTkSuQmCC",
    "Arrow": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAARbSURBVHgB7Zm7TytHFMbP7voR27wJwghCLl2EIoEuLQX/ARVUUEQpgkSTIj2UgJIoHdClooyiFOlQ0kdRIhERBVEAhiAeAvzA9u56vfm+tU1uHARXZHdz8Z2fdLT27qw155sz58yMRRQKhUKhUCgUCoVCoVAoFAqFQqFQKBQKhUKhUCgCoqur60V3d/cPPT09LuwXfpe3CB1O/7q6uuoSXikG7mvS4tBBHWZw5F+F32dmZgx81KSFhaBjEVj8PgF4nyJIqwqwvLzM0Y/19/en7hOgr6+vDc+jUouSUIhISDC0gT40NGTk8/mYYRj/amNZVhTPnePj46qERGhK19Fs29Ydx7lXeIhyUCwW/0Q0fCnh9y1wOK9jsDaEerp5CiwuLro3Nzfu4eGh97m3t/dHtLmu21fSAmjpdLoP5e7DZDI50CwAHW9AIZoFQftlec7Aga9HRkbcsbExOpNpFqCZZkEYCVKbFs+vQqDzH83NzXmOkPX1dfcxAZqpl0lOId2trRV8IdAqwI7Ozs7q29vbLzo7O4VGFhYW5CmgfLJKsJxU5JnAkI1i9D7jCG5tbblPhe8PDw93Q4AEfpMrRnnT8VZ97DA2Ou/DgSPmgJ2dHfcpUID29vZ38ZtJqS2WfCHoWqt1dHQYlUqlBB8Wstlsfn5+Xo6OjuQpVKvVCEqor30OfLFxfn6uMReg83/APqXz09PTAjFe+zcabROJhHZxcdFIgL4kwkAFmJiYkMvLyyqSVtU0TV5/gghfoMQJI+F12djYYEIVrBJZURqO+5IEDAkObXJyUnZ3dzUsfPR4PG5wGQx+h0UymcxLNmKbh8BZgaytrQnE+yYWi32PqwUhWAVC2y/8F7wqMDAwkBwcHOxFCL+HRPYByuFLrAh/Hh8ffzDxraysuPUToxMk0qlUKpXmjhGRxST45k8BqYWpc3p6ap+cnJQjkUgJG54yzMT9zx9Lhpubm7ycwj6GHhlOJUSPr/Uv6O1wo7PO6OiojV2gDiF0CMCp8NtjLzP5wfFP4Didr+CdytnZWZUmPhHWuvruKAyhn4AAKXxuY2V46CUmPth4NBrFtC/mkUeKmA7m3t6e5VckhLXnZmc5as719bWFimBibWDCuW/vGtSc/YeB7zhdEDnl29tb8+rqyt7f32ckiF+EvbNizyMYxXfgBI+/2iEEIyKO0yADOULDd8GIw2fHZr5AlBRwr1goFIpob0GYCqaDb3kgtCOxOuy4SwcR0hYdhHMUxYUgBpwVOM6ToSquFu6X8LyM0GfStGGOn86TINcB9zI1NaUjnHk0pkEIRqAnCASw4SwXChac9CoFl9B4ZqL8WblcjrXf9x1Q6OduEKB6cHBQoVMY5SKsUCqVsrAcIiALy+FeHmcHBSx8yriaOCS1l5aWvOgRn/k/Tlcaf3x4VYFX7PN1OO7tGRjizPD1UtcwR+rTR1qEOwEQEcxD0frq7lWLyN9HYG/FX2ZeBDR9VigC5i/opj7Y1mqD/AAAAABJRU5ErkJggg==",
    "I-Beam": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAC5SURBVHgB7djBCcQgEIXh57IFhOSeGlJCqrWOtGIDYgeuIyukgV0h838gmjllHl4cCQAAAAAAAAAcCZpgXdf6PZZa6xVCONt5sULOeco//ZUFYFJKNcZYSyn9+xbMs1mjto7j6I3bPmryZNyEmY2/5BwByDkCkHMEIOcIQM4RgJwjADlHAHLurQnG+3/fd932XnM1ErNRmI3EbDQ2azAy5QaYbdtkGbTj1dbZBqOLAAAAAAAAAAC/9QHAaU/wMJ9VTQAAAABJRU5ErkJggg=="
}

# icon_base64: assets/RobloxCustomCursorIcon.png
icon_base64 = "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"

# --- Main app class ---
class CursorViewerApp(tk.Tk):
    """
    A tkinter-based application to display custom Roblox cursor images.

    This class extends `tk.Tk` to create a GUI application that displays Roblox custom
    cursors, using a tkinter canvas to render images. It initializes the window and sets
    up basic properties like title, geometry, and icon. The `build_ui` method is used to
    construct the user interface.

    :param image_data: The image data to be displayed in the application, typically a
                       list of tuples with cursor labels, images, and file paths.
    :type image_data: list[tuple[str, PIL.Image.Image | None, str]]
    """
    def __init__(self, image_data):
        """
        Initialize the CursorViewerApp window with a title, icon, and a canvas for displaying
        the cursor images.

        :param image_data: The image data to be displayed, containing the images of cursors.
        :type image_data: list[tuple[str, PIL.Image.Image | None, str]]
        """
        super().__init__()
        self.title("Roblox Custom Cursor")
        self.configure(bg="#1e1e1e")
        self.geometry("400x280")
        self.resizable(False, False)

        # Decode base64 data
        icon_data = base64.b64decode(icon_base64)
        icon_image = PhotoImage(data=icon_data)
        self.iconphoto(True, icon_image)
        
        self.image_refs = []  # Prevent garbage collection
        self.canvas_dict = {}  # Initialize canvas_dict here
        self.build_ui(image_data)

        self.registrar = FileTypeRegistrar()

    def build_ui(self, image_data):
        """
        Build the user interface for displaying cursor images, labels, and buttons.

        This method creates the main UI components, including a container frame, labels
        for cursor names, canvas widgets for images, and buttons for interacting with
        the cursor files. It also sets up hover and click events for the labels, and
        includes disclaimers and credits.

        :param image_data: The image data to be displayed in the UI, containing cursor labels,
                           images, and file paths.
        :type image_data: list[tuple[str, PIL.Image.Image | None, str]]
        :return: None
        :rtype: None
        """
        container = tk.Frame(self, bg="#1e1e1e")
        container.place(relx=0.5, rely=0.42, anchor="center")

        for index, (label_text, pil_image, filepath) in enumerate(image_data):
            col = index % 3

            # Default label (white text, no underline)
            label = tk.Label(
                container, text=label_text,
                fg="white", bg="#1e1e1e",
                font=("Segoe UI", 10),
                cursor="hand2"
            )
            label.grid(row=0, column=col, pady=(0, 5))

            # Change to folder emoji on hover
            def on_hover_in(event, label=label, label_text=label_text):
                """
                Change the label text to include a folder emoji when the mouse hovers over it.

                :param event: The event object representing the hover event.
                :param label: The label whose text is being modified.
                :param label_text: The original label text to restore when the mouse leaves.
                :return: None
                :rtype: None
                """
                label.config(text="🗁 " + label_text)

            def on_hover_out(event, label=label, label_text=label_text):
                """
                Restore the original label text when the mouse leaves the label.
    
                :param event: The event object representing the hover-out event.
                :param label: The label whose text is being restored.
                :param label_text: The original label text to restore.
                :return: None
                :rtype: None
                """
                label.config(text=label_text)

            label.bind("<Enter>", on_hover_in)
            label.bind("<Leave>", on_hover_out)

            # Click to open file in Explorer
            label.bind("<Button-1>", lambda e, path=filepath: self.open_in_explorer(path))

            # Canvas with rounded frame, axes, and image
            canvas = tk.Canvas(container, width=100, height=100, bg="#1e1e1e", highlightthickness=0)
            canvas.grid(row=1, column=col, padx=15)

            draw_rounded_rect(canvas, 10, 10, 90, 90, radius=20, fill="#2e2e2e", outline="#444444", width=2)
            canvas.create_line(0, 50, 100, 50, fill="#666666", width=1)
            canvas.create_line(50, 0, 50, 100, fill="#666666", width=1)

            if pil_image:
                tk_img = ImageTk.PhotoImage(pil_image)
                self.image_refs.append(tk_img)
                canvas.create_image(50, 50, image=tk_img)
            else:
                canvas.create_text(50, 50, text="Not found", fill="gray", font=("Arial", 8))

            self.canvas_dict[label_text] = canvas  # Save canvas widget reference

            # Add Change, Default, and Photopea buttons
            self.add_buttons(container, col, filepath, label_text, pil_image)

        # Disclaimer
        disclaimer_label = tk.Label(
            self, text="Roblox Custom Cursor is not affiliated with or endorsed by Photopea",
            fg="#525252", bg="#1e1e1e", font=("Segoe UI", 8)
        )
        disclaimer_label.place(relx=0.5, rely=1, anchor="s")

        # Credits label

        credits_text = "Made with ♡ by Xelvanta™ Softworks"

        credits_label = tk.Label(
            self, text=credits_text,
            fg="#A9A9A9", bg="#1e1e1e", font=("Segoe UI", 8), cursor="heart"
        )
        credits_label.place(relx=0.5, rely=0.95, anchor="s")

        # Make the credits label a clickable link
        credits_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Xelvanta/roblox-custom-cursor"))
        
        # Change font to underlined when hovering and revert when leaving
        credits_label.bind("<Enter>", lambda e: credits_label.config(font=("Segoe UI", 8, "underline"), text="Roblox Custom Cursor GitHub Repository ↗"))
        credits_label.bind("<Leave>", lambda e: credits_label.config(font=("Segoe UI", 8), text=credits_text))

        # Settings button
        settings_button = tk.Button(
        self, text="⚙", font=("Segoe UI Symbol", 12),
        bg="#1e1e1e", fg="#AAAAAA", bd=0, cursor="hand2",
        command=self.show_settings_window
        )

        settings_button.place(relx=1.0, rely=0.0, anchor="ne", x=0, y=-5)
        settings_button.bind("<Enter>", lambda e: settings_button.config(fg="white"))
        settings_button.bind("<Leave>", lambda e: settings_button.config(fg="#AAAAAA"))

    def add_buttons(self, container, col, filepath, label_text, pil_image):
        """
        Add buttons for changing the cursor image, restoring the default image, and opening
        the cursor image in Photopea for editing.

        This method creates three buttons:
        1. A "Change Cursor" button that allows the user to select a new image to replace the
           existing cursor image.
        2. A "Restore Default" button that restores the original cursor image from base64 data.
        3. A "Edit in Photopea" button that opens the image in Photopea for further editing.

        :param container: The tkinter container widget in which the buttons are placed.
        :type container: tk.Frame
        :param col: The column index where the buttons will be placed in the container.
        :type col: int
        :param filepath: The file path of the cursor image.
        :type filepath: str
        :param label_text: The label text associated with the cursor image.
        :type label_text: str
        :param pil_image: The PIL image object of the cursor.
        :type pil_image: PIL.Image.Image | None
        :return: None
        :rtype: None
        """
        # Change button
        def change_button_action():
            """
            Handle the action for changing the cursor image.
            Prompts the user to select a new PNG file and updates the cursor image.

            :return: None
            :rtype: None
            """
            new_file = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
            if new_file:
                try:
                    img = Image.open(new_file).resize((64, 64), Image.Resampling.LANCZOS)
                    img.save(filepath)
                    self.update_gui_with_new_image(filepath, label_text)
                except Exception as e:
                    messagebox.showerror("Error", f"Error updating image:\n\n{e}\n\n"
          "• Errno 2: This usually occurs when the Roblox folder or file was moved or deleted during runtime. "
          "Restarting the application should fix this.\n"
          "• Errno 13: This usually occurs when the application doesn't have permission to access the file. "
          "Try running the application as an administrator or closing any programs that might be using the file.")

        change_button = tk.Button(container, text="Change Cursor", command=change_button_action, bg="#444444", fg="white", width=13, cursor="hand2")
        change_button.grid(row=2, column=col, pady=(5, 5))
        change_button.bind("<Enter>", lambda e: change_button.config(bg="#2e2e2e"))
        change_button.bind("<Leave>", lambda e: change_button.config(bg="#444444"))

        # Default button
        def default_button_action():
            """
            Handle the action for restoring the default cursor image.
            Restores the default image from base64 data and updates the cursor image.

            :return: None
            :rtype: None
            """
            try:
                img_data = base64.b64decode(default_cursor_base64[label_text])
                img = Image.open(BytesIO(img_data)).resize((64, 64), Image.Resampling.LANCZOS)
                img.save(filepath)
                self.update_gui_with_new_image(filepath, label_text)
            except Exception as e:
                messagebox.showerror("Error", f"Error restoring default image:\n\n{e}\n\n"
          "• Errno 2: This usually occurs when the Roblox folder or file was moved or deleted during runtime. "
          "Restarting the application should fix this.\n"
          "• Errno 13: This usually occurs when the application doesn't have permission to access the file. "
          "Try running the application as an administrator or closing any programs that might be using the file.")

        default_button = tk.Button(container, text="Restore Default", command=default_button_action, bg="#444444", fg="white", width=13, cursor="hand2")
        default_button.grid(row=3, column=col, pady=(0, 5))
        default_button.bind("<Enter>", lambda e: default_button.config(bg="#2e2e2e"))
        default_button.bind("<Leave>", lambda e: default_button.config(bg="#444444"))

        # Photopea button
        def photopea_button_action():
            """
            Handle the action for opening the cursor image in Photopea.
            Converts the cursor image to base64, constructs a URL for Photopea, and opens it in a browser.

            :return: None
            :rtype: None
            """
            # Convert image to base64 and encode it
            with open(filepath, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            config = {
                "files": [
                    f"data:image/png;base64,{img_base64}"
                ],
                "environment": {
                    "eparams": {
                        "guides": True,
                        "grid": True,
                        "gsize": 32,
                        "paths": True,
                        "pgrid": True
                    }
                }
            }

            # Convert the configuration to a JSON string
            config_str = json.dumps(config)

            # URL-encode the JSON string
            encoded_config = urllib.parse.quote(config_str)

            # Construct the Photopea URL
            photopea_url = f"https://www.photopea.com#{encoded_config}"

            # Uncomment this line as needed to debug the encoded URL
            # print("Encoded URL:", photopea_url)

            # Open Photopea in a new browser tab with the encoded JSON URL
            webbrowser.open(photopea_url)

        photopea_button = tk.Button(container, text="Edit in Photopea", command=photopea_button_action, bg="#444444", fg="white", width=13, cursor="hand2")
        photopea_button.grid(row=4, column=col, pady=(0, 5))
        photopea_button.bind("<Enter>", lambda e: photopea_button.config(bg="#2e2e2e"))
        photopea_button.bind("<Leave>", lambda e: photopea_button.config(bg="#444444"))

    def export_cursors_to_rcur(self):
        try:
            # Find Roblox folder
            folder = find_valid_roblox_version_folder()
            # print(f"[DEBUG] Roblox version folder found: {folder}")
    
            # List of cursor filenames in order
            cursor_filenames = ["ArrowFarCursor.png", "ArrowCursor.png", "IBeamCursor.png"]
            encoded_cursors = []

            for filename in cursor_filenames:
                filepath = os.path.join(folder, "content", "textures", "Cursors", "KeyboardMouse", filename)
                # print(f"[DEBUG] Checking file: {filepath}")
                if not os.path.isfile(filepath):
                    raise FileNotFoundError(f"Cursor file missing: {filename}")
                with open(filepath, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                    encoded_cursors.append(encoded)

            # Ask user where to save the file
            save_path = filedialog.asksaveasfilename(
                defaultextension=".rcur",
                filetypes=[("Roblox Custom Cursor Profile", "*.rcur"), ("All Files", "*.*")],
                initialfile="roblox_custom_cursor_profile",
                title="Save exported cursors as"
            )
            if not save_path:
                # print("[DEBUG] Save cancelled by user.")
                return

            print(f"[DEBUG] Saving exported cursors to: {save_path}")
            print(f"[DEBUG] Total encoded images: {len(encoded_cursors)}")
            # Save base64 strings line by line
            with open(save_path, "w", encoding="utf-8") as out_file:
                out_file.write("\n".join(encoded_cursors))

            messagebox.showinfo("Success", "Cursors exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            # print(f"[DEBUG] Error during export: {e}")

    def import_cursors_from_rcur(self):
        try:
            # Find Roblox folder
            folder = find_valid_roblox_version_folder()
            if not folder:
                raise FileNotFoundError("Could not find a valid Roblox version folder.")

            cursor_filenames = ["ArrowFarCursor.png", "ArrowCursor.png", "IBeamCursor.png"]
            cursor_paths = [os.path.join(folder, "content", "textures", "Cursors", "KeyboardMouse", fn) for fn in cursor_filenames]

            # Ask user to select the .rcur file to import
            import_path = filedialog.askopenfilename(
                filetypes=[("Roblox Custom Cursor Profile", "*.rcur"), ("All Files", "*.*")],
                title="Select .rcur file to import"
            )
            if not import_path:
                return  # User cancelled

            # Read all base64 lines from the .rcur file
            with open(import_path, "r", encoding="utf-8") as f:
                base64_lines = [line.strip() for line in f if line.strip()]

            if len(base64_lines) != len(cursor_filenames):
                raise ValueError(f"The .rcur file should contain exactly {len(cursor_filenames)} cursor images.")

            # For each cursor, decode and save image, then update GUI
            for i, b64data in enumerate(base64_lines):
                decoded = base64.b64decode(b64data)
                # Save to the corresponding cursor file
                with open(cursor_paths[i], "wb") as img_file:
                    img_file.write(decoded)

                # Update GUI image for that cursor label
                filename_to_canvas_label = {
                    "ArrowFarCursor.png": "Arrow Far",
                    "ArrowCursor.png": "Arrow",
                    "IBeamCursor.png": "I-Beam"
                }
                label_text = filename_to_canvas_label[cursor_filenames[i]]
                self.update_gui_with_new_image(cursor_paths[i], label_text)

            messagebox.showinfo("Success", "Cursors imported and applied successfully.")
            # print("[DEBUG] Label text:", label_text)
            # print("[DEBUG] Canvas keys:", list(self.canvas_dict.keys()))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import cursors:\n{e}")

    def show_settings_window(self):
        settings_win = tk.Toplevel(self)
        settings_win.title("Settings")
        settings_win.configure(bg="#1e1e1e")
        settings_win.geometry("300x270")
        settings_win.resizable(False, False)

        tk.Label(settings_win, text="Settings", font=("Segoe UI", 12, "bold"),
                 fg="white", bg="#1e1e1e").pack(pady=15)

        def create_button_with_info(parent, text, command, tooltip_text):
            container = tk.Frame(parent, bg="#1e1e1e")
            container.pack(pady=3)

            btn = tk.Button(container, text=text,
                            command=command,
                            bg="#444444", fg="white", cursor="hand2", width=25)
            btn.pack(side="left")
            btn.bind("<Enter>", lambda e: btn.config(bg="#2e2e2e"))
            btn.bind("<Leave>", lambda e: btn.config(bg="#444444"))
        
            info_label = tk.Label(container, text="🛈", font=("Segoe UI", 12),
                                  fg="white", bg="#1e1e1e", cursor="question_arrow")
            info_label.pack(side="left", padx=3)

            # Attach tooltip to info_label
            ToolTip(info_label, tooltip_text)

            container.pack_configure(anchor="center")

            return btn, info_label

        export_btn, export_info = create_button_with_info(settings_win, "Export Cursors as Profile", self.export_cursors_to_rcur, "Export your currently applied cursors as a Roblox Custom Cursor Profile (.rcur) file.\nThis file can be shared or imported later to restore your full cursor set.")
        import_btn, import_info = create_button_with_info(settings_win, "Import Cursors from Profile", self.import_cursors_from_rcur, "Import cursors from an existing Roblox Custom Cursor Profile (.rcur) file.\nThis will replace your currently applied cursor set with the full set from the profile.")
        register_btn, register_info = create_button_with_info(settings_win, "Associate .rcur File Type", self.registrar.register_rcur_file_type, "Associate the Roblox Custom Cursor Profile (.rcur) file type with Windows.\nThis allows importing .rcur files by opening (double-clicking) them directly.\nThe installation will also include necessary icons and scripts to support core functionalities.\nA UAC prompt will appear to allow registry changes. Requires an internet connection.")
        unregister_btn, unregister_info = create_button_with_info(settings_win, "Unassociate .rcur File Type", self.registrar.unregister_rcur_file_type, "Unassociate the Roblox Custom Cursor Profile (.rcur) file type from Windows.\nRemoves registry entries associated with Roblox Custom Cursor.\nA UAC prompt will appear to allow registry changes.")


        # Report a bug label

        bug_text = "Report a Bug or Request a Feature"

        bug_label = tk.Label(
            settings_win, text=bug_text,
            fg="#A9A9A9", bg="#1e1e1e", font=("Segoe UI", 8), cursor="hand2"
        )
        bug_label.place(relx=0.5, rely=0.98, anchor="s")

        # Make the bug label a clickable link
        bug_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Xelvanta/roblox-custom-cursor/issues/new"))
        
        bug_label.bind("<Enter>", lambda e: bug_label.config(font=("Segoe UI", 8, "underline"), text=bug_text + " ↗"))
        bug_label.bind("<Leave>", lambda e: bug_label.config(font=("Segoe UI", 8), text=bug_text))

        close_btn = tk.Button(settings_win, text="Close", command=settings_win.destroy,
                          bg="#444444", fg="white", cursor="hand2")
        close_btn.pack(pady=20)
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#2e2e2e"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#444444"))

    def update_gui_with_new_image(self, filepath, label_text):
        """
        Reload the image from the specified file path and update the GUI with the new image.

        This method opens the image file at the given path, resizes it to 64x64 pixels, and updates
        the canvas associated with the given label text. It first clears any existing content in
        the canvas and then draws a rounded rectangle with the new image centered within it.

        :param filepath: The path to the image file that will be loaded and displayed.
        :type filepath: str
        :param label_text: The label text that identifies the canvas to be updated.
        :type label_text: str
        :return: None
        :rtype: None
        """
        # Reload the image and update GUI
        pil_image = Image.open(filepath).resize((64, 64), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(pil_image)
        self.image_refs.append(tk_img)

        # Update the canvas associated with the label
        canvas = self.canvas_dict.get(label_text)
        if canvas:
            canvas.delete("all")  # Clear the existing content
            draw_rounded_rect(canvas, 10, 10, 90, 90, radius=20, fill="#2e2e2e", outline="#444444", width=2)
            canvas.create_line(0, 50, 100, 50, fill="#666666", width=1)
            canvas.create_line(50, 0, 50, 100, fill="#666666", width=1)
            canvas.create_image(50, 50, image=tk_img)

    def open_in_explorer(self, filepath):
        """
        Open the file or folder in Windows Explorer, selecting the specified file.

        If the file path exists, this method opens Windows Explorer and selects the file at the
        given path. If the file does not exist, an error message is displayed indicating the issue.

        :param filepath: The path to the file or folder to be opened and selected in Explorer.
        :type filepath: str
        :return: None
        :rtype: None
        """
        if os.path.exists(filepath):
            subprocess.run(['explorer', '/select,', os.path.normpath(filepath)])
        else:
            messagebox.showerror("Error", f"Error showing image in explorer:\n\nFile or folder not found during runtime.\n\n"
          "• This usually occurs when the Roblox folder or file was moved or deleted during runtime. "
          "Restarting the application should fix this.")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#333333", fg="white", relief='solid', borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# 2025-05-22: Added support for importing .rcur file by opening it directly (milestone feature)
# Author: Alina Wan
# 2025-06-05: Switch from embedded base64 to runtime download of dependencies (major change)
# This change applies only to an opt-in feature. Base64 embedding should continue as the default approach elsewhere.
# Author: Alina Wan

class FileTypeRegistrar:
    def register_rcur_file_type(self):
        icon_path = os.path.join(
            os.environ["SystemDrive"],
            r"Program Files\Xelvanta Softworks\Roblox Custom Cursor\data\images\rcur_icon_variable.ico"
        ).replace("\\", "\\\\")

        # Build the contents of the elevated script
        script_content = '''
import winreg
import tkinter as tk
from tkinter import messagebox
import os
import requests

root = tk.Tk()
root.withdraw()

rcur_importer_content = r\'\'\'
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
\'\'\'

icon_url = \'https://raw.githubusercontent.com/Xelvanta/roblox-custom-cursor/refs/heads/main/assets/rcur_icon_variable.ico\'
launcher_url = \'https://raw.githubusercontent.com/Xelvanta/roblox-custom-cursor/main/rcur_importer_launcher/rcur_importer_launcher.exe\'

try:
    launcher_path = os.path.join(
       os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "rcur_importer_launcher.exe"
    )

    rcur_importer_path = os.path.join(
       os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "rcur_importer.pyw"
    )

    icon_path = os.path.join(
        os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "data", "images", "rcur_icon_variable.ico"
    )

    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    with open(icon_path, "wb") as icon_file:
        icon_file.write(requests.get(icon_url, timeout=10).content)

    os.makedirs(os.path.dirname(rcur_importer_path), exist_ok=True)
    with open(rcur_importer_path, "w", encoding="utf-8") as py_file:
        py_file.write(rcur_importer_content)

    os.makedirs(os.path.dirname(launcher_path), exist_ok=True)
    with open(launcher_path, "wb") as f:
        f.write(requests.get(launcher_url, timeout=10).content)

    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, ".rcur") as ext_key:
        winreg.SetValueEx(ext_key, "", 0, winreg.REG_SZ, "rcurfile")

    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"rcurfile") as rcurfile_key:
        winreg.SetValueEx(rcurfile_key, "", 0, winreg.REG_SZ, "Roblox Custom Cursor Profile")

    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"rcurfile\\DefaultIcon") as icon_key:
        winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, icon_path)

    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"rcurfile\\shell\\open\\command") as command_key:
        command = '"{}" "%1"'.format(launcher_path)
        winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)

    messagebox.showinfo("Success", "Successfully registered .rcur file type in Windows Registry.")

except Exception as e:
    messagebox.showerror("Error", "Failed to register .rcur file type in Windows Registry: {}".format(e))

try:
    os.remove(__file__)
except Exception:
    pass
'''

        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(script_content)
            temp_script_path = f.name

        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if not pythonw.lower().endswith("pythonw.exe"):
            pythonw = sys.executable  # fallback

        try:
            # Run the temp script elevated
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", pythonw,
                f'"{temp_script_path}"', None, 1)

            if ret <= 32:
                raise RuntimeError(f"ShellExecuteW failed with code {ret}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to run as administrator:\n{e}")
        finally:
            def delayed_cleanup():  # Ensure the file is deleted if it fails to delete itself
                time.sleep(5)  # wait long enough for messagebox to close
                try:
                    os.remove(temp_script_path)
                except Exception:
                    pass

            threading.Thread(target=delayed_cleanup, daemon=True).start()

    def unregister_rcur_file_type(self):
        script_content = '''
import winreg
import os
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

def delete_key_recursive(root, sub_key):
    try:
        open_key = winreg.OpenKey(root, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except FileNotFoundError:
        return

    # Delete all subkeys first
    try:
        while True:
            subkey_name = winreg.EnumKey(open_key, 0)
            delete_key_recursive(open_key, subkey_name)
    except OSError:
        pass
    finally:
        winreg.CloseKey(open_key)

    try:
        winreg.DeleteKey(root, sub_key)
    except FileNotFoundError:
        pass
    except PermissionError as e:
        messagebox.showerror("Error", "Failed to delete registry key {}: {}".format(sub_key, e))
        raise

keys_to_delete = [
    "rcurfile\\shell\\open\\command",
    "rcurfile\\shell\\open",
    "rcurfile\\shell",
    "rcurfile\\DefaultIcon",
    "rcurfile",
    ".rcur",
]

try:
    for key in keys_to_delete:
        delete_key_recursive(winreg.HKEY_CLASSES_ROOT, key)

    messagebox.showinfo("Success", "Successfully unregistered .rcur file type from Windows Registry.")

except Exception as e:
    messagebox.showerror("Error", "Failed to unregister .rcur file type: {}".format(e))

try:
    os.remove(__file__)
except Exception:
    pass
'''

        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(script_content)
            temp_script_path = f.name

        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if not pythonw.lower().endswith("pythonw.exe"):
            pythonw = sys.executable  # fallback

        try:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", pythonw,
                '"{}"'.format(temp_script_path), None, 1)

            if ret <= 32:
                raise RuntimeError(f"ShellExecuteW failed with code {ret}")

        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to run as administrator:\n{e}")
        finally:
            def delayed_cleanup():  # Ensure the file is deleted if it fails to delete itself
                time.sleep(5)
                try:
                    os.remove(temp_script_path)
                except Exception:
                    pass

            threading.Thread(target=delayed_cleanup, daemon=True).start()

# --- Entry point (definitely not a roblox reference) ---

def main():
    """
    Main entry point for the application.

    This function attempts to find a valid Roblox version folder and load the cursor images 
    from the relevant directory. If a valid version folder is found, the `CursorViewerApp` is 
    initialized and started. If no valid folder is found, an error message is displayed.

    The flow of this function is as follows:
    1. It checks for a valid Roblox version folder using `find_valid_roblox_version_folder()`.
    2. If no valid folder is found, an error message is shown and the function exits.
    3. If a valid folder is found, it loads the cursor images from the `KeyboardMouse` directory.
    4. The `CursorViewerApp` is created and the application starts running.

    :return: None
    :rtype: None
    """
    version_folder = find_valid_roblox_version_folder()
    if not version_folder:
        messagebox.showerror("Error", "Could not find a valid Roblox version folder.")
        return

    cursor_folder = os.path.join(version_folder, "content", "textures", "Cursors", "KeyboardMouse")
    image_data = load_cursor_images(cursor_folder)

    app = CursorViewerApp(image_data)
    app.mainloop()

if __name__ == "__main__":
    main()
