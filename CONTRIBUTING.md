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

| Extension | Description                                                                                                                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `.rcur`   | `Roblox Custom Cursor Profile` file. Contains three cursor images in base64 (Arrow Far, Arrow, I-Beam) assigned to specific rows. Double-clicking directly imports the profile without opening the main app. |
| `.rccapp` | `Roblox Custom Cursor Application File` file. A renamed Python `.pyw` script used to run Roblox Custom Cursor using the official embedded Python 3.x runtime for RCC3.                                       |

These are handled in the following ways:

* `.rcur` is associated with `rcur_importer_launcher.exe`, which launches `rcur_importer.rccapp` with the double-clicked file as an argument, using the embedded Python runtime for RCC3.
* `.rccapp` is a runnable Roblox Custom Cursor Python application. **It is essentially a `.pyw` file** configured to run using the embedded Python runtime for RCC3 located in `app/python/`.

### 🔒 `.rcur` Safety & Format Integrity

The `.rcur` file format is designed to be **simple, transparent, and safe — even when used from external sources**. It contains exactly three lines of base64-encoded PNG image data and **no embedded logic, scripting, or metadata**.

* **All import behavior is strictly controlled by the main application (`Roblox Custom Cursor.rccapp`) and default importer (`rcur_importer.rccapp`)**, not by the `.rcur` file itself.
* **`.rcur` files must never contain code, commands, or runtime instructions.**
* This makes `.rcur` files passive, static containers — similar in risk profile to image or plain text files.

> ✅ Because the import logic does not interpret code or run dynamic input, `.rcur` files are safe to use from untrusted or external sources.

**Contributor expectation:**
If you're modifying or extending the importer, you must ensure it continues to treat `.rcur` strictly as image data — never as a source of logic or executable behavior. Avoid functions like `eval()`, `exec()`, or any pattern that parses or executes arbitrary text.

Maintaining this design guarantees that `.rcur` files remain safe, portable, and interoperable in all environments.

### 🔄 File Execution Pipeline

To ensure consistency, security, and compatibility, `.rcur` and `.rccapp` files follow a **strict and predictable execution pipeline**. All paths in registry key values are expected to be **absolute** and refer to the user installation directory of Roblox Custom Cursor.

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

This ensures that:

* The importing logic is centralized and controlled.
* The `.rcur` file is treated as a **read-only data input**.
* No part of the system executes user-provided logic from the `.rcur` file.

> ✅ `Program Files (x86)` is the default installation location. However, users may choose a different path during installation. All references should the user-installed location.

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
git commit -m "update:a detailed commit message"
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

## 📜 License Notice

By contributing, you agree your code will be released under **GPL-3.0**.  
All contributions must remain open-source under the same license.

---

Thank you for helping make Roblox Custom Cursor better! 🚀  
If you get stuck, feel free to open an issue or reach out via Discussions.
