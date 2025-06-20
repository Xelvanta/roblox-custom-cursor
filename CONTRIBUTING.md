# 🖱️ Contributing to Roblox Custom Cursor

Thank you for your interest in contributing to **Roblox Custom Cursor**! 🎉
This project is licensed under the **GPL-3.0 License**, so all contributions must also remain open-source under the same license.

We welcome contributions of all types:

* 🔧 Bug reports & fixes
* 🌟 New features or enhancements
* 🎨 Image/icon updates
* 📝 Documentation improvements
* 💻 Code contributions (Python, C++, Inno Setup)

---

## 🏷️ Versioning Scheme

We use a **4-part version number** in this format:

```

G.M.m.p

```

- **G — Generation**  
  This is the *biggest* version number representing a major generation of the app — think major rewrites, big architecture changes, or fundamental shifts. It changes rarely, signaling significant milestones.

- **M.m.p — Semantic Versioning (SemVer) equivalent**  
  The last three numbers follow the familiar SemVer pattern:  
  - **M** = Major (breaking changes within the current generation)  
  - **m** = Minor (new features, backward compatible)  
  - **p** = Patch (bug fixes and minor tweaks)

> **Note:**  
> Older versions used the standard 3-part SemVer (e.g. 1.2.3) without a Generation number.  
> Due to migration challenges, the 4-part versioning scheme was introduced starting at version 3.4.0.2 for all intents and purposes.

### Example

Version `3.4.5.1` means:  
- Generation 3 (big architectural era)  
- SemVer 4.5.1 (major=4, minor=5, patch=1)

This lets us clearly mark big leaps with Generation while keeping familiar SemVer for everyday releases.

Please use this format when updating versions in project files and release notes!

---

## 🧰 Development Environment

To contribute efficiently, we recommend the following tools:

| Component          | Recommendation                              |
| ------------------ | ------------------------------------------- |
| OS                 | Windows 11                                  |
| Python Interpreter | Python 3.x Runtime for RCC3 (`app/python/`) |
| IDE (Python)       | VS Code, PyCharm, or any modern editor      |
| C++ Compiler       | MSVC (Visual Studio 2022)                   |
| IDE (C++)          | Visual Studio 2022 (Community or higher)    |
| Terminal           | PowerShell 5.1+ or Windows Terminal         |
| Build Environment  | Developer Command Prompt for VS 2022        |
| Inno Setup Compiler| Inno Setup Compiler 6.4+                    |

> ⚠️ For C++ builds, only **MSVC (cl.exe)** via **Visual Studio 2022 Developer Command Prompt** is supported. Do not use MinGW or other toolchains.

---

## 📁 Roblox Custom Cursor File Extensions

Roblox Custom Cursor defines and uses several custom file extensions to structure its runtime and launcher behavior:

| Extension | Description                                                                                                                                                                     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.rcur`   | `Roblox Custom Cursor Profile` file. A lightweight binary format with a fixed header and embedded image data. Double-clicking imports the profile without opening the main app. |
| `.rccapp` | `Roblox Custom Cursor Application File` file. A renamed Python `.pyw` script used to run Roblox Custom Cursor using the official embedded Python 3.x runtime for RCC3.          |

These are handled in the following ways:

* `.rcur` is associated with `rcur_importer.rccapp`, which takes the double-clicked file as an argument and uses the RCC3 embedded Python runtime to process it.
* `.rccapp` is a runnable Roblox Custom Cursor Python application. **It is essentially a `.pyw` file** configured to run using the embedded Python runtime for RCC3 located in `app/python/`.

### 🧬 `.rcur` Format & Binary Header

The `.rcur` file format begins with a **5-byte ASCII magic header**: `RCUR\x00`. This header allows the importer to confirm that the file is a valid Roblox Custom Cursor Profile before processing. It is followed by a 4-byte version number (currently `2`) and three image length values that describe how many bytes to read for each cursor image.

The file’s contents are processed **only if all of the following validations pass**:

* The magic header matches `RCUR\x00`.
* The version number is exactly `2`.
* Three consecutive image lengths are present and valid.
* The declared number of bytes for each image is actually present in the file.

> ✅ If any of these conditions fail, the importer immediately exits with an error — the file is ignored.

However, **even if a malicious `.rcur` file is carefully constructed to pass all validations**, it does not result in any code execution or data interpretation. The importer:

* Simply reads the indicated number of bytes for each image,
* And **writes them directly to disk** as `.png` files — without attempting to decode or interpret the content.

There is **no parsing logic beyond basic validation**, no execution of embedded metadata, and no attempt to "understand" the images. If the written output is not a valid PNG, it will simply not render correctly — but **no harmful behavior is triggered**.

> 🔒 This design ensures that even a well-crafted but malicious `.rcur` file cannot cause damage — the worst it can do is replace cursor files with garbage data, which is easily reversible.

**Contributor expectation:**
If you're modifying or extending the importer, continue to treat `.rcur` strictly as a source of **opaque binary blobs**. Do not introduce dynamic parsing, and never include logic that evaluates or interprets content from the file. Always reject files that do not strictly match the expected format, and avoid using unsafe functions like `eval()`, `exec()`, or anything that reads beyond defined image blocks.

By maintaining this behavior, `.rcur` remains a safe, inert format — secure for external use and resilient against tampering.

### 🔄 File Execution Pipeline

To ensure consistency and compatibility, `.rcur` and `.rccapp` files follow a **strict and predictable execution pipeline**. All paths in registry key values are expected to be **absolute** and refer to the user installation directory of Roblox Custom Cursor.

#### `.rccapp` Execution (Roblox Custom Cursor Application File)

When a `.rccapp` file is run (e.g. `Roblox Custom Cursor.rccapp`), the expected execution pipeline looks something like:

```cmd
"C:\Program Files (x86)\Xelvanta Softworks\Roblox Custom Cursor\python\pythonw.exe" "%1"
```

This runs the `.rccapp` Python script silently using the embedded Python interpreter installed with RCC3.

#### `.rcur` Execution (Roblox Custom Cursor Profile)

When a `.rcur` file is double-clicked or opened, the expected execution pipeline looks something like:

```cmd
"C:\Program Files (x86)\Xelvanta Softworks\Roblox Custom Cursor\python\pythonw.exe" "C:\Program Files (x86)\Xelvanta Softworks\Roblox Custom Cursor\rcur_importer.rccapp" "%1"
```

This ensures that the importing logic is centralized and controlled.

> ✅ `Program Files (x86)` is the default installation location. However, users may choose a different path during installation. All references should the user-installed location.

---

## 🚀 How to Run `.rccapp` Files for Development

Roblox Custom Cursor uses `.rccapp` files, which are Python scripts renamed to run with the embedded Python interpreter bundled inside the project (`app/python/python.exe`).

To run these scripts and test your changes, you have two simple options:

### 1. Using a Terminal from the Project Root

Open a command prompt window **in the root directory** of the Roblox Custom Cursor project, then run:

```cmd
app\python\python.exe "app\Roblox Custom Cursor.rccapp"
```

or to import a `.rcur` file:

```cmd
app\python\python.exe app\rcur_importer.rccapp "path\to\yourfile.rcur"
```

This method is quick and convenient if you work frequently in the project folder.

### 2. Using Absolute Paths (Copy as Path)

If you prefer, you can also run the scripts from **anywhere** by pasting the full absolute path into your command prompt:

```cmd
"C:\Program Files (x86)\Xelvanta Softworks\Roblox Custom Cursor\app\python\python.exe" "C:\Program Files (x86)\Xelvanta Softworks\Roblox Custom Cursor\app\rcur_importer.rccapp" "C:\path\to\yourfile.rcur"
```

> Use these commands to test imports, run the app, or debug scripts during development.

---

## 🛠️ How to Contribute

### 1. Fork and Clone

```bash
gh repo fork Xelvanta/roblox-custom-cursor --clone
cd roblox-custom-cursor
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

You can contribute to:

* Main application logic at `app/Roblox Custom Cursor.rccapp`
* Launcher logic at `app/rcur_importer.rccapp`
* Inno Setup script at `app/RCC3_Installer.iss`
* Documentation or metadata at `README.md`, `CONTRIBUTING.md`, `assets/preview/`, etc.

---

## ⚙️ Build Requirements

### 📦 Installing Python Libraries for the Embedded Interpreter

If you want to add Python packages like `Pillow` to the official embedded Python runtime for RCC3, **you must install them into the `app/python/Lib/site-packages` folder** manually.

Use the following `pip` command to do this:

```bash
pip install --target=app/python/Lib/site-packages pillow==11.1.0
```

You can replace `pillow==11.1.0` with any package and version your changes require.

> ⚠️ Do not install packages globally — all dependencies must live inside the embedded Python folder so the installer works out-of-the-box without requiring users to install anything separately.

**Requirements:**

* All Python dependencies **must be installed** into `app/python/Lib/site-packages` using `pip install --target=...`.
* The embedded Python environment **must remain fully self-contained** — no global Python or pip dependencies should be required. Confirm that **no manual user installation** is needed post-setup.
* If you add new packages, ensure the app continues to run **error-free** using only the embedded interpreter.
* You **are expected to commit** the `Lib/` folder (this directory is **not excluded** by `.gitignore`).

### 📦 Inno Setup Installer (`RCC3_Installer.iss`)

The main installer for the project is written in Inno Setup 6.4+ and:

* Must be located at: `app/RCC3_Installer.iss`
* Uses `rcur_importer_launcher.exe` and other local assets during packaging
* Should be tested with the official **Inno Setup Compiler v6.4 or newer**

**Requirements:**

* The installer **must compile without errors** and behave correctly during the setup wizard.
* The installer output directory **must be set to the same directory as the script** (i.e., `OutputDir=.`) so the compiled installer `.exe` is created inside `app/`.
* The resulting `.exe` installer **must not be committed** to the repository (it's excluded via `.gitignore`)
* CI will handle building and hashing automatically during deployment

---

## 🧽 Code Style Guidelines

### 🐍 Python

* Follow **PEP 8** + **PEP 257** (docstrings)
* Use **Black** for formatting:

```bash
black .
```

* Prefer `f"{}"` for formatting
* Use `os.path.join()` for paths

---

## ✅ Final Steps

### 1. Stage and Commit

```bash
git add .
git commit -m "update: a detailed commit message"
```

### 2. Push and Open a PR

```bash
git push origin feature/your-feature-name
```

Then go to GitHub and open a pull request.
Include:

* A short summary of what you changed
* Related issues (e.g., `Fixes #12`)

---

## 🎯 Not Sure Where to Start? Creating and Adding `.rcur` Example Files.

> 🤔 Not sure where to start? Try fixing a typo in `README.md` or adding an `.rcur` test file to `examples/`!

If you want to contribute `.rcur` cursor profiles for testing or examples, here’s how you can easily export your current cursor setup:

1. **Open the Roblox Custom Cursor application.**
2. Navigate to **Settings > Export Cursors as Profile**.
3. Choose a location to save the `.rcur` file. This file will contain the currently applied cursors exported as a profile.
4. Add your exported `.rcur` file to the `examples/` directory for others to test and review.

### 📝 Editing ATTRIBUTION.txt

When adding new cursor profiles or assets, please update the `ATTRIBUTION.txt` file accordingly.  
- Add new entries **in alphabetical order** by the filename.  
- Ensure all license information and source links are accurate and complete.

This helps keep the project organized and easy to maintain.

> ⚖️ `.rcur` profile files under `examples/` are data files and **may be licensed independently** of the repository’s GPLv3 license. They are **not required** to use a GPL-compatible license.

---

## ⚙️ Other Notes

> Contributors extending or debugging certain features might find some of these notes useful.

- **IPC**: The importer script communicates with the main application over a local socket on port `57623` to notify it to refresh cursor images after import. This internal inter-process communication (IPC) mechanism helps keep the GUI updated automatically without requiring manual refreshes.
- **App GUID**: The application’s GUID is `c1004246-945e-4b7c-863e-e6c0184d4086`. In the Windows registry, it may appear as `{c1004246-945e-4b7c-863e-e6c0184d4086}_rcc3_is1`.

---

## 📜 License Notice

By contributing, you agree your code will be released under **GPL-3.0**.  
All contributions must remain open-source under the same license.

---

Thank you for helping make Roblox Custom Cursor better! 🚀  
If you get stuck, feel free to open an issue or reach out via Discussions.
