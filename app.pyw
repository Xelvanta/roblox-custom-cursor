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

default_cursor_base64 = {
    "Arrow Far": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAP3SURBVHgB7Zg7TBRRFIbPzsy+WFYeSwQUCCHEGkNjQkIorChIJKEkamEsjDEx1IaG2hZiDwWFjfYUEI2gFRBjASGQyCNZgUV2dmZ2xv8Ms+tKeIiMAyznS07uvDPnv/89984QCYIgCIIgCIIgCIIgCIIgCIIgCIIgCIIg/Eeqq6sf1tbW/kAsp1Kph3SNCDmOE+LEV1ZWHI6Ojg4HIjzic1TmcIIKQoMAToGCCDj2mMpcBDf51tbWWKkAR4hQfrDt0Sjt7e1RJHnjsADXwQmhnp4erbGxsSKZTKaOEqBUhHKsCZyMhqgEN48ToFQEzBTl4wQeAp2dneG6urpkRUVF40kClKUTvBoQ5vEPAW6dJkA51oSiAHDBXwlQbk5wh8BZHHCECA+wS36hULD885u3tLTQyMgI2bb9KBQKqeSTEzQKEK4BDHqe4ABO5sTrZ2Zm/tifnp4m3F6NTXV4eNhBuI+lq4JXBCMnDYHt7e3idnd3Nxc/N2pqagrteH19fQLP0bznnYtAhwB6j5tje2xiYoIGBweL+729vW6LRL+g+Yx4m8/nXyP4vZWQ98CrRHEWQDG7XeqA8fHxYm/D6kU3tLW1ZXDtfSyI7mL1eIedAxdU4TlR8qEDVQoW91sgm82GkQgn8LKqqorm5uZoaGiIz+8h0js7O5X9/f0Ui8VoY2MjMjs7m7Us66OqqkY8HjegjYlnWKgB9tTU1LlqQKAW8oogfwbHdV2vRIKfcPi2d3oPRfEF2g5FUZ4vLS0Ri8OFsK+vL4PkO2F9FmJ/d3dXx3UmwqJzFsGga4D7skjQSSQSNloe8HM8xpH8M+x/RbzHsb3R0VH3nq6uLmpubk4i+ZRpmno0GjXIh8QLBCqAV7XZBg4StZHQimEYj5H8E5xbgCty6OE0rnk3NjZG8/PzrgNWV1cJApjhcNjY2toyBwYG8riG49wiXMQQUJqamiKZTCaG5BORSCQKATS0Si6X48vgdvUe4g2v+LxCv6ZpWs/m5uZ3bLMDfEmeuYgh4KytrdlI2ERSWbhgH9t7SDaD3v+JxLOIDxDlFY59wz2zaJ+i6O1g/uf/CacuoM70ThQwBRdgU0NCGgRQ+RgHbK4iIrB6HG0MrYZrLS5+SBqmyezTVXYA47nAxji2MMUZDQ0NOuZ5HXN+FlOjDjewK9gFOhzBNcHAton7bAwdB/e5LiKfCHodUGRhYcEVY3Jy0k6n0yyIg562l5eXHf5OgBAOimIePc/TXQ5TZm59fd1aXFxk//smwGVbSir4XFbhDA3Ja+h9t4MwFCyu/nRgfd/sf1lR+Mcp2gj/OqeDJW8YDlH9+Pg5zGX9mAjR73dz1w4lIQiC4Bu/ABsKDEIN5oAYAAAAAElFTkSuQmCC",
    "Arrow": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAARbSURBVHgB7Zm7TytHFMbP7voR27wJwghCLl2EIoEuLQX/ARVUUEQpgkSTIj2UgJIoHdClooyiFOlQ0kdRIhERBVEAhiAeAvzA9u56vfm+tU1uHARXZHdz8Z2fdLT27qw155sz58yMRRQKhUKhUCgUCoVCoVAoFAqFQqFQKBQKhUKhUCgCoqur60V3d/cPPT09LuwXfpe3CB1O/7q6uuoSXikG7mvS4tBBHWZw5F+F32dmZgx81KSFhaBjEVj8PgF4nyJIqwqwvLzM0Y/19/en7hOgr6+vDc+jUouSUIhISDC0gT40NGTk8/mYYRj/amNZVhTPnePj46qERGhK19Fs29Ydx7lXeIhyUCwW/0Q0fCnh9y1wOK9jsDaEerp5CiwuLro3Nzfu4eGh97m3t/dHtLmu21fSAmjpdLoP5e7DZDI50CwAHW9AIZoFQftlec7Aga9HRkbcsbExOpNpFqCZZkEYCVKbFs+vQqDzH83NzXmOkPX1dfcxAZqpl0lOId2trRV8IdAqwI7Ozs7q29vbLzo7O4VGFhYW5CmgfLJKsJxU5JnAkI1i9D7jCG5tbblPhe8PDw93Q4AEfpMrRnnT8VZ97DA2Ou/DgSPmgJ2dHfcpUID29vZ38ZtJqS2WfCHoWqt1dHQYlUqlBB8Wstlsfn5+Xo6OjuQpVKvVCEqor30OfLFxfn6uMReg83/APqXz09PTAjFe+zcabROJhHZxcdFIgL4kwkAFmJiYkMvLyyqSVtU0TV5/gghfoMQJI+F12djYYEIVrBJZURqO+5IEDAkObXJyUnZ3dzUsfPR4PG5wGQx+h0UymcxLNmKbh8BZgaytrQnE+yYWi32PqwUhWAVC2y/8F7wqMDAwkBwcHOxFCL+HRPYByuFLrAh/Hh8ffzDxraysuPUToxMk0qlUKpXmjhGRxST45k8BqYWpc3p6ap+cnJQjkUgJG54yzMT9zx9Lhpubm7ycwj6GHhlOJUSPr/Uv6O1wo7PO6OiojV2gDiF0CMCp8NtjLzP5wfFP4Didr+CdytnZWZUmPhHWuvruKAyhn4AAKXxuY2V46CUmPth4NBrFtC/mkUeKmA7m3t6e5VckhLXnZmc5as719bWFimBibWDCuW/vGtSc/YeB7zhdEDnl29tb8+rqyt7f32ckiF+EvbNizyMYxXfgBI+/2iEEIyKO0yADOULDd8GIw2fHZr5AlBRwr1goFIpob0GYCqaDb3kgtCOxOuy4SwcR0hYdhHMUxYUgBpwVOM6ToSquFu6X8LyM0GfStGGOn86TINcB9zI1NaUjnHk0pkEIRqAnCASw4SwXChac9CoFl9B4ZqL8WblcjrXf9x1Q6OduEKB6cHBQoVMY5SKsUCqVsrAcIiALy+FeHmcHBSx8yriaOCS1l5aWvOgRn/k/Tlcaf3x4VYFX7PN1OO7tGRjizPD1UtcwR+rTR1qEOwEQEcxD0frq7lWLyN9HYG/FX2ZeBDR9VigC5i/opj7Y1mqD/AAAAABJRU5ErkJggg==",
    "I-Beam": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAC5SURBVHgB7djBCcQgEIXh57IFhOSeGlJCqrWOtGIDYgeuIyukgV0h838gmjllHl4cCQAAAAAAAAAcCZpgXdf6PZZa6xVCONt5sULOeco//ZUFYFJKNcZYSyn9+xbMs1mjto7j6I3bPmryZNyEmY2/5BwByDkCkHMEIOcIQM4RgJwjADlHAHLurQnG+3/fd932XnM1ErNRmI3EbDQ2azAy5QaYbdtkGbTj1dbZBqOLAAAAAAAAAAC/9QHAaU/wMJ9VTQAAAABJRU5ErkJggg=="
}

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
        register_btn, register_info = create_button_with_info(settings_win, "Associate .rcur File Type", self.registrar.register_rcur_file_type, "Associate the Roblox Custom Cursor Profile (.rcur) file type with Windows.\nThis allows importing .rcur files by opening (double-clicking) them directly.\nThe installation will also include necessary icons and scripts to support core functionalities.\nA UAC prompt will appear to allow registry changes.")
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
import base64

root = tk.Tk()
root.withdraw()

icon_b64 = "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GgAaGhovGhoa6hoaGv8aGhr4Ghoa4BoaGrMaGhp6GhoaQxoaGhgaGhoDGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoPGhoaqRoaGqQaGhpeGhoaKRoaGgkaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/////gf8AAP////gB/wAA////gAH/AAD///wAAP8AAP//wAAA/wAA//wAAAD/AAD/4AAAAP8AAP4AAAAAfwAA4AAAAAB/AAAAAAAAAH8AAAAAAAAAfwAAAAAAAAA/AAAAAAAAAD8AAAAAAAAAPwAAAAAAAAAfAACAAAAAAB8AAIAAAAAAHwAAgAAAAAAfAACAAAAAAA8AAMAAAAAADwAAwAAAAAAPAADAAAAAAA8AAOAAAAAABwAA4AAAAAAHAADgAAAAAAcAAOAAAAAABwAA8AAAAAADAADwAAAAAAMAAPAAAAAAAwAA8AAAAAABAAD4AAAAAAEAAPgAAAAAAQAA+AAAAAABAAD8AAAAAAAAAPwAAAAAAAAA/AAAAAAAAAD8AAAAAAAAAP4AAAAAAAAA/gAAAAAAAAD+AAAAAAcAAP4AAAAAfwAA/wAAAAf/AAD/AAAAP/8AAP8AAAP//wAA/wAAP///AAD/gAH///8AAP+AH////wAA/4H/////AAAoAAAAQAAAAIAAAAABACAAAAAAAABAAAAjLgAAIy4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaARoaGhIaGho4GhoadhoaGroaGhpmGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGggaGholGhoaVBoaGpAaGhrEGhoa6RoaGvwaGhr/GhoaqRoaGgUaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGgQaGhobGhoaRBoaGn4aGhq3Ghoa4hoaGvkaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGtgaGhodGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgEaGhoRGhoaOBoaGm4aGhqnGhoa1hoaGvUaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr2GhoaRxoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoLGhoaKRoaGlwaGhqWGhoayhoaGu4aGhr+Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGn8aGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoGGhoaHRoaGkoaGhqEGhoauxoaGuUaGhr8Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhq2GhoaCRoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoCGhoaFBoaGjwaGhpyGhoaqxoaGtoaGhr2Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa4xoaGigaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaDBoaGi4aGhphGhoamxoaGs4aGhryGhoa/hoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvsaGhpXGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaBhoaGiEaGhpQGhoaiRoaGr8aGhrpGhoa/BoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoakBoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaAxoaGhgaGhpBGhoadxoaGrAaGhreGhoa+RoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGscaGhoQGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaARoaGg8aGhoyGhoaZhoaGp8aGhrUGhoa8xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrtGhoaNBoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGgkaGhomGhoaVRoaGo4aGhrGGhoa7BoaGv0aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/hoaGmgaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgQaGhobGhoaRRoaGnwaGhq0Ghoa4hoaGvoaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhqiGhoaAxoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGmEaGhqnGhoa1xoaGvUaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa1RoaGhoaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhqyGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvMaGhpDGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoabxoaGvsaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoaeRoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGjQaGhrmGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/yEhIf8bGxv/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGrIaGhoHGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoPGhoawBoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Gxsb/3BwcP/CwsL/gYGB/x8fH/8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrfGhoaIxoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGosaGhr/Ghoa/xoa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Gv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr+Ghoa8hoaGtIaGhqdGhoaYxoaGjAaGhoOGhoaARoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGg0aGhrBGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+BoaGtwaGhquGhoadBoaGj4aGhoXGhoaAxoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaiRoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/BoaGucaGhq9GhoahhoaGk0aGhofGhoaBhoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGlAaGhr5Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/hoaGvEaGhrMGhoamBoaGl4aGhosGhoaCxoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhojGhoa3xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvYaGhrYGhoaqBoaGm8aGho6GhoaExoaGgIaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaBxoaGq8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvsaGhrjGhoauBoaGoEaGhpIGhoaHBoaGgUaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhp3Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv4aGhrsGhoayBoaGpMaGhpZGhoaJxoaGgoaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaQRoaGvMaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr0Ghoa1BoaGqQaGhprGhoaNRoaGhAaGhoBGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGhgaGhrTGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr5Ghoa4BoaGrUaGhp7GhoaQRoaGhkaGhoEGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoDGhoaohoaGv8aGhr7Ghoa6BoaGsIaGhqNGhoaURoaGiMaGhoIGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGl0aGhq2GhoachoaGjYaGhoQGhoaARoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//////+B/////////AD////////AAP///////AAA///////gAAD//////gAAAH/////gAAAAf////wAAAAB////wAAAAAH///wAAAAAAP//wAAAAAAA//4AAAAAAAD/4AAAAAAAAH/AAAAAAAAAf8AAAAAAAAB/wAAAAAAAAH/AAAAAAAAAP8AAAAAAAAA/4AAAAAAAAD/gAAAAAAAAP+AAAAAAAAAf4AAAAAAAAB/wAAAAAAAAH/AAAAAAAAAP8AAAAAAAAA/wAAAAAAAAD/gAAAAAAAAP+AAAAAAAAAf4AAAAAAAAB/wAAAAAAAAH/AAAAAAAAAf8AAAAAAAAA/wAAAAAAAAD/gAAAAAAAAP+AAAAAAAAAf4AAAAAAAAB/gAAAAAAAAH/AAAAAAAAAf8AAAAAAAAA/wAAAAAAAAD/gAAAAAAAAP+AAAAAAAAA/4AAAAAAAAB/gAAAAAAAAH/AAAAAAAAAf8AAAAAAAAB/wAAAAAAAAD/AAAAAAAAAP+AAAAAAAAA/4AAAAAAAAD/gAAAAAAAAP+AAAAAAAAB/8AAAAAAAB//wAAAAAAA///AAAAAAA///+AAAAAA////4AAAAA/////gAAAAf////+AAAAf/////8AAAf//////wAAP///////AAP///////8AP////////4H///////KAAAAIAAAAAAAQAAAQAgAAAAAAAAAAEAIy4AACMuAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGgcaGhogGhoaTRoaGoQaGhp7GhoaCRoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoCGhoaEhoaGjEaGhpfGhoamxoaGssaGhruGhoa/hoaGtkaGhofGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaARoaGgwaGhoqGhoaWRoaGokaGhrAGhoa5hoaGvcaGhr/Ghoa/xoaGv8aGhr/Ghoa9BoaGk4aGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoFGhoaGxoaGkMaGhp1GhoasBoaGtwaGhr2Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoahxoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaAhoaGhIaGho3GhoabRoaGp0aGhrTGhoa8BoaGvwaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhq3GhoaDhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgEaGhoNGhoaLBoaGlcaGhqKGhoaxBoaGuoaGhr8Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGuAaGhovGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoBGhoaChoaGh4aGhpKGhoaghoaGrEaGhreGhoa9xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+RoaGl8aGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgQaGhoVGhoaPBoaGnAaGhqqGhoa1hoaGvEaGhr+Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoakBoaGgMaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoCGhoaEBoaGioaGhpfGhoalhoaGsQaGhrpGhoa/BoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrGGhoaFRoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaARoaGgkaGhoeGhoaTRoaGoUaGhq/Ghoa5RoaGvgaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGuoaGho2GhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoFGhoaGxoaGj0aGhp0GhoaqhoaGtgaGhr0Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+hoaGmgaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaAxoaGhEaGhotGhoaYhoaGpoaGhrQGhoa7RoaGvwaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoaohoaGggaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoKGhoaJhoaGlEaGhqJGhoavhoaGuMaGhr5Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrSGhoaIRoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaBhoaGhoaGhpIGhoafBoaGq8aGhrgGhoa9RoaGv4aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvIaGhpLGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgMaGhoVGhoaORoaGmYaGhqdGhoa0xoaGvIaGhr+Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGnsaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaDBoaGikaGhpdGhoakBoaGsAaGhrpGhoa+xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoatRoaGg0aGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGgcaGhofGhoaTBoaGnoaGhqyGhoa4BoaGvgaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrgGhoaJBoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoDGhoaFBoaGjgaGhpxGhoaphoaGtEaGhryGhoa/hoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvUaGhpTGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaAhoaGg4aGhopGhoaYBoaGpAaGhrGGhoa7BoaGvwaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGo0aGhoBGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhoKGhoaJBoaGk0aGhqGGhoauhoaGuIaGhr5Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoaxRoaGhMaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaBhoaGhgaGho7GhoadBoaGqwaGhrcGhoa8xoaGv4aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrrGhoaNhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgIaGhoRGhoaMxoaGmEaGhqbGhoazBoaGusaGhr8Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvoaGhpmGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaCxoaGiEaGhpOGhoaiRoaGsEaGhrpGhoa+RoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGqAaGhoHGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGgYaGhoeGhoaRxoaGncaGhqwGhoa3hoaGvQaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoazxoaGhkaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoCGhoaExoaGjMaGhpjGhoanRoaGs8aGhrxGhoa/RoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhrtGhoaPxoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaARoaGgwaGhorGhoaWxoaGosaGhrCGhoa6BoaGvgaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv4aGhp4GhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoIGhoaHBoaGkoaGhqDGhoatBoaGt0aGhr3Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGrEaGhoMGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGnAaGhrWGhoa8xoaGv4aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa3xoaGicaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaeRoaGvsaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr0GhoaURoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhpFGhoa6hoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhqLGhoaAhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGhoaGhrDGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGr4aGhoPGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaBBoaGpEaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa5BoaGi0aGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaVRoaGvUaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr7GhoaZBoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoqGhoa4hoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GBgY/xoaGv8bGxv/GBgY/xkZGf8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhqUGhoaAhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGg4aGhq2Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/x0dHf9YWFj/lpaW/5ycnP9ra2v/JiYm/xkZGf8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGsoaGhoWGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGoAaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8ZGRn/YWFh/+bm5v////////////X19f+JiYn/Hh4e/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa7hoaGjwaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaUBoaGvMaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GBgY/zIyMv/Kysr//////////////////////+Pj4/9BQUH/GBgY/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GhoadhoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoiGhoa1RoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8YGBj/FxcX/xgYGP8ZGRn/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoa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Gv8aGhr/GRkZ/yQkJP+5ubn///////////////////////////+JiYn/GBgY/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/3Jycv/y8vL//////////////////////////////////////////////////////////////////////////////////////////////////v7+//v7+//4+Pj/9PT0/+/v7//r6+v/5ubm/93d3f/V1dX/ysrK/56env8/Pz//GRkZ/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa0xoaGh0aGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaexoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8ZGRn/Kysr/8/Pz///////////////////////+/v7/3R0dP8XFxf/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8ZGRn/JSUl/6ampv///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////7+/v/8vLy//GRkZ/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhruGhoaQRoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhpDGhoa8BoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xgYGP80NDT/4uLi///////////////////////y8vL/V1dX/xcXF/8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8YGBj/QEBA/9bW1v//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////9fX1/2JiYv8XFxf/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv0aGhp4GhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGhkaGhrQGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/GBgY/0pKSv/u7u7//////////////////////+fn5/9BQUH/GBgY/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/bW1t/+zs7P/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////5+fn/bm5u/xcXF/8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoa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Gv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvkaGhpkGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGiIaGhrbGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8WFhb/cHBw//r6+v//////////////////////////////////////9PT0/5+fn/80NDT/GBgY/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGp8aGhoIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaDBoaGrIaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoa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Gv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvcaGhrlGhoavRoaGoYaGhpWGhoaJxoaGgsaGhoBGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhozGhoa5hoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr8Ghoa7hoaGsoaGhqYGhoaXhoaGi8aGhoRGhoaAhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGhQaGhrFGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/hoaGvIaGhraGhoaqhoaGnEaGhpCGhoaGxoaGgUaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaBBoaGpAaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr4Ghoa5xoaGrsaGhqDGhoaSRoaGh4aGhoJGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoAGhoaWBoaGvYaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/BoaGugaGhrIGhoalRoaGlwaGhovGhoaDxoaGgEaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhosGhoa5RoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv0aGhrxGhoa2BoaGqYaGhpuGhoaNhoaGhUaGhoFGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGg0aGhq2Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+BoaGt4aGhq2GhoagBoaGkgaGhohGhoaCRoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGn8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvsaGhrpGhoawBoaGosaGhpbGhoaJRoaGgwaGhoCGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaRBoaGvEaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr9Ghoa7xoaGs0aGhqhGhoaaxoaGjMaGhoRGhoaAhoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhocGhoa1xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvYaGhrcGhoarBoaGnUaGhpHGhoaHBoaGgYaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGggaGhqmGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr6Ghoa5hoaGrsaGhqMGhoaVxoaGiUaGhoKGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGm0aGhr9Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/hoaGvAaGhrOGhoalxoaGmEaGho1GhoaEhoaGgIaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaPxoaGuwaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv4aGhrzGhoa3BoaGqkaGhp4GhoaQhoaGhcaGhoFGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoYGhoaxhoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+BoaGuAaGhq6GhoagxoaGkwaGhoiGhoaCRoaGgAaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgQaGhqTGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvsaGhrrGhoazBoaGpQaGhpdGhoaKRoaGg8aGhoDGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGlkaGhr2Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr+Ghoa8hoaGtQaGhqlGhoabhoaGjkaGhoYGhoaBBoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaLBoaGuMaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvcaGhrjGhoauRoaGoAaGhpIGhoaGxoaGggaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoPGhoauRoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr7Ghoa5hoaGsAaGhqRGhoaWBoaGicaGhoOGhoaARoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhqCGhoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/hoaGu8aGhrSGhoapRoaGmsaGho3GhoaEhoaGgMaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaABoaGlIaGhr0Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr1Ghoa2xoaGqwaGhp9GhoaRRoaGhwaGhoJGhoaABoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaJBoaGtYaGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa+xoaGugaGhq+GhoahBoaGlMaGhooGhoaCxoaGgEaGhoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoJGhoaqxoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGvwaGhrvGhoazhoaGpgaGhpoGhoaMhoaGhAaGhoBGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGgAaGhp5Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa/xoaGv8aGhr/Ghoa9RoaGtgaGhqqGhoacBoaGj4aGhoYGhoaBBoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGhoaABoaGkAaGhrvGhoa/xoaGv8aGhr/Ghoa/xoaGvYaGhrkGhoauxoaGoQaGhpUGhoaJRoaGgoaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaGhoAGhoaFxoaGswaGhr+Ghoa7BoaGscaGhqVGhoaWhoaGi0aGhoQGhoaARoaGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABoaGgAaGhoGGhoabBoaGn8aGhpIGhoaHBoaGgUaGhoAGhoaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////////////8D///////////////////wA///////////////////AAP/////////////////+AAD/////////////////4AAAf////////////////gAAAH///////////////+AAAAB///////////////8AAAAAP//////////////wAAAAAD//////////////AAAAAAA/////////////+AAAAAAAP////////////4AAAAAAAB////////////wAAAAAAAAf///////////AAAAAAAAAH//////////8AAAAAAAAAB//////////4AAAAAAAAAAP/////////gAAAAAAAAAAD////////+AAAAAAAAAAAA////////4AAAAAAAAAAAAH///////wAAAAAAAAAAAAB///////AAAAAAAAAAAAAAf/////8AAAAAAAAAAAAAAH/////4AAAAAAAAAAAAAAA/////gAAAAAAAAAAAAAAAP///+AAAAAAAAAAAAAAAAD///4AAAAAAAAAAAAAAAAA///wAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAAAAAA///AAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAAf//gAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAAf//gAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAP//wAAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAB//+AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAP//wAAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAH//4AAAAAAAAAAAAAAAAAB//+AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAA///AAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAH//4AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAAAAAA///AAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAAf//gAAAAAAAAAAAAAAAAAH//4AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAAf//gAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAP//wAAAAAAAAAAAAAAAAAD//8AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAB//+AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAP//wAAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAH//4AAAAAAAAAAAAAAAAAB///AAAAAAAAAAAAAAAAAAf//wAAAAAAAAAAAAAAAAAH//8AAAAAAAAAAAAAAAAAA///AAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD//+AAAAAAAAAAAAAAAAAA///gAAAAAAAAAAAAAAAAAP//4AAAAAAAAAAAAAAAAAD///AAAAAAAAAAAAAAAAAH///wAAAAAAAAAAAAAAAAf///8AAAAAAAAAAAAAAAB/////AAAAAAAAAAAAAAAH/////4AAAAAAAAAAAAAAP/////+AAAAAAAAAAAAAA///////gAAAAAAAAAAAAD///////8AAAAAAAAAAAAH////////AAAAAAAAAAAAf////////wAAAAAAAAAAB/////////8AAAAAAAAAAH//////////gAAAAAAAAAP//////////4AAAAAAAAA///////////+AAAAAAAAD////////////gAAAAAAAH////////////8AAAAAAAf/////////////AAAAAAB//////////////wAAAAAD//////////////+AAAAAP///////////////gAAAA////////////////4AAAB////////////////+AAAH/////////////////wAAf/////////////////8AB///////////////////AD///////////////////wP///////////////4lQTkcNChoKAAAADUlIRFIAAAEAAAABAAgEAAAA9ntg7QAAHBhJREFUeNrtnXl8FdXZx7/3hhAgiYDsh30REIWCGMKq1K2KggvYYtW+4tYqvupbP+7WvvZlqXVrq61ba60bRXEDXBC0BQIkYVVQA8giwrCHAAlbtvePJGS7Z+bMvXNm5ubO9/OxJXdmzpwz93fPnOec53kOuIg4VYwSyW7eMcCKRq7ebQyvs0usJJtl5LGHYsPr9ic8IfduJeANrq38o5h15JLDCr7nsFHu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"

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

rcur_batch_content = r\'\'\'
@echo off
REM %1 is the file path passed by the shell

REM Call Python with the script and pass the file argument
pythonw "%SystemDrive%\\Program Files\\Xelvanta Softworks\\Roblox Custom Cursor\\rcur_importer.pyw" "%~1"
\'\'\'

try:
    launcher_path = os.path.join(
       os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "rcur_importer_launcher.bat"
    )

    rcur_importer_path = os.path.join(
       os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "rcur_importer.pyw"
    )

    icon_data = base64.b64decode(icon_b64)

    icon_path = os.path.join(
        os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor", "data", "images", "rcur_icon_variable.ico"
    )

    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    with open(icon_path, "wb") as icon_file:
        icon_file.write(icon_data)

    os.makedirs(os.path.dirname(rcur_importer_path), exist_ok=True)
    with open(rcur_importer_path, "w", encoding="utf-8") as py_file:
        py_file.write(rcur_importer_content)

    os.makedirs(os.path.dirname(launcher_path), exist_ok=True)
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(rcur_batch_content)

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
