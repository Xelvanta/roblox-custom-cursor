# 🖱️ Roblox Custom Cursor

![GitHub License](https://img.shields.io/github/license/Xelvanta/roblox-custom-cursor?label=License\&color=orange)
![GitHub Release](https://img.shields.io/github/v/release/Xelvanta/roblox-custom-cursor?include_prereleases\&label=Release\&color=green)

<p align="left">
  <img src="assets/RobloxCustomCursorIcon.png" width="128" style="margin-right: 10px;">
  <strong>Roblox Custom Cursor</strong> is a <strong>100% self-contained Windows-based Python application</strong> designed for easy cursor customization on Roblox.  
  The entire functionality is bundled into a single <code>app.pyw</code> file.  
  The only external requirements are <strong>Python 3.x</strong> and the <strong>Pillow</strong> library for image handling.
</p>

---

## Features

* 🗂️ **One-File Simplicity**: Entire app is packed into a single `app.pyw` file—no installation or clutter.
* 🐍 **Self-Contained**: Only requires Python 3.x and Pillow—no extra dependencies.
* 📁 **Smart Directory Detection**: Automatically finds the correct Roblox version folder—no digging through nested paths.
* 💾 **.rcur File Support**: Import/export cursor setups using the `.rcur` format for backups or sharing.
* ⚡ **Double-Click Imports**: Associate `.rcur` files for instant import directly from Windows Explorer.
* 🪟 **Windows Registry Integration**: Registers `.rcur` files in Windows so they open with the app by default.
* 📐 **Auto-Resize on Upload**: Upload any PNG and it’s automatically resized to fit Roblox’s cursor specs.
* 🎯 **Image Alignment Helper**: Use the "Edit in Photopea" button to fine-tune alignment with built-in center guidelines.
* 🖼️ **Custom Image Support**: Use any PNG file as a cursor—with full transparency support.
* 🛟 **Safe and Reversible**: Original Roblox cursors are backed up for easy restoration.
* ♻️ **Reset to Default**: One-click reset brings back standard Roblox cursors.
* 🧼 **Clean UI**: Simple, intuitive interface designed for speed and clarity.
* 🪶 **Lightweight**: Runs smoothly even on low-end Windows machines.

---

## 📋 Requirements

Before running the application, ensure you have:

* **Python 3.x**

  * [Download Python](https://www.python.org/downloads/)
* **Pillow** (Python package for handling images)

  * Install it by running:

    ```bash
    pip install pillow==11.1.0
    ```

---

## ⚙️ Installation

You can either **clone the repository** or **download the `app.pyw` file directly from the root directory**

### 1.
#### Clone the Repository:

```bash
git clone https://github.com/Xelvanta/roblox-custom-cursor
cd roblox-custom-cursor
```

### OR

#### Download the `app.pyw` File Directly:

Download the latest `app.pyw` file from [Roblox Custom Cursor](https://github.com/Xelvanta/roblox-custom-cursor) and save it to a folder of your choice.

### 2. Install Dependencies:

Make sure Pillow is installed:

```bash
pip install pillow==11.1.0
```

---

## ▶️ Running the Application

To run the **Roblox Custom Cursor** app:

1. Open a terminal and navigate to the folder containing `app.pyw`
2. Run the script:

```bash
python app.pyw
```

**Or simply double-click `app.pyw` in your file explorer to launch the app directly — no terminal needed!**

---

## 🗂️ `.rcur` File Type Support

The `.rcur` file is a custom plaintext format that holds the three cursor images used by **Roblox**. You can:

* **Export** your current cursor setup as a `.rcur` file for backup or sharing.
* **Import** a `.rcur` file to quickly apply a saved cursor configuration.

If you **associate the `.rcur` file type with windows** via the Settings menu (top-right), you can simply **double-click any `.rcur` file** in Windows Explorer to import it directly — no need to open the main application first.

---


## 📸 Preview

<table>
  <tr>
    <td align="center">
      <img src="assets/preview/RCC_Main_GUI_v1.3.1.png" width="200"/><br>Main GUI
    </td>
    <td align="center">
      <img src="assets/preview/RCC_Settings_v1.6.0.png" width="200"/><br>Settings
    </td>
    <td align="center">
      <img src="assets/preview/Export_RCUR_v1.6.6.png" width="200"/><br>Export .rcur
    </td>
    <td align="center">
      <img src="assets/preview/Import_RCUR_v1.6.6.png" width="200"/><br>Import .rcur
    </td>
  </tr>
</table>

---

## 💡 Contributing

Feel free to fork the project and submit pull requests to improve **Roblox Custom Cursor**. Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

---

## 📝 License

**Roblox Custom Cursor** is open source and available under the GPL-3.0 license. See the [LICENSE](LICENSE) for details.

---

By **Xelvanta**
For support or inquiries: [Xelvanta@proton.me](mailto:Xelvanta@proton.me)  
GitHub: [https://github.com/Xelvanta](https://github.com/Xelvanta)