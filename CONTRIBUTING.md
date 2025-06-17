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
> Because of migration challenges, the 4-part versioning scheme was introduced starting at version 3.4.0.2 for all intents and purposes.

### Example

Version `3.4.5.1` means:  
- Generation 3 (big architectural era)  
- SemVer 4.5.1 (major=4, minor=5, patch=1)

This lets us clearly mark big leaps with Generation while keeping familiar SemVer for everyday releases.

Please use this format when updating versions in project files and release notes!

---

## 🧰 Development Environment

To contribute efficiently, we recommend the following tools:

| Component          | Recommendation                           |
| ------------------ | ---------------------------------------- |
| OS                 | Windows 11                               |
| Python Interpreter | Python 3.x (latest)                      |
| IDE (Python)       | VS Code, PyCharm, or any modern editor   |
| C++ Compiler       | MSVC (Visual Studio 2022)                |
| IDE (C++)          | Visual Studio 2022 (Community or higher) |
| Terminal           | PowerShell 5.1+ or Windows Terminal      |
| Build Environment  | Developer Command Prompt for VS 2022     |
| Inno Setup Compiler| Inno Setup Compiler 6.4+                 |

> ⚠️ For C++ builds, only **MSVC (cl.exe)** via **Visual Studio 2022 Developer Command Prompt** is supported. Do not use MinGW or other toolchains.

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

* Python logic at `app/Roblox Custom Cursor.pyw`
* Launcher logic at `app/rcur_importer_launcher.cpp` and `app/rcur_importer.pyw`
* Inno Setup script at `app/RCC3_Installer.iss`
* Documentation or metadata at `README.md`, `CONTRIBUTING.md`, `assets/preview/`, etc.

---

## ⚙️ Build Requirements

### 🧱 C++ Launcher (`rcur_importer_launcher`)

The `.rcur` importer launcher is written in minimal C++ and:

* Must be located at: `app/rcur_importer_launcher.cpp`
* Should use only Win32 APIs and relative paths (no hardcoding)
* Must be compiled using MSVC with the following command:

```cmd
cl rcur_importer_launcher.cpp /O2 /link shell32.lib /SUBSYSTEM:WINDOWS /INCREMENTAL:NO
```

> ✅ This will generate `rcur_importer_launcher.exe` in the same folder.

**Requirements:**

* The launcher must compile **error-free** and behave correctly when launched automatically by Windows through a .rcur file association (i.e., when a user double-clicks a .rcur file).
* The resulting `.exe` **must not be committed** to the repository (it's excluded via `.gitignore`)
* CI will handle building and hashing automatically during deployment

---

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

### 💻 C++

* Keep it minimal and Windows-native
* Use only standard Win32 APIs (no third-party dependencies)
* Avoid bloating the executable
* Must compile **error-free**

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