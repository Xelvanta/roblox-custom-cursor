# 🖱️ Contributing to Roblox Custom Cursor

Thank you for your interest in contributing to **[Roblox Custom Cursor](https://github.com/Xelvanta/roblox-custom-cursor)**! 🎉 This project is licensed under the **GPL 3.0** license, so all contributions must also be open-source under the same license.

We welcome all kinds of contributions, including **bug reports, feature additions, image enhancements, documentation improvements, and code contributions**. Please follow the steps below to ensure a smooth contribution process.

---

## 🧰 Recommended Development Environment

To ensure seamless compatibility and optimal performance during development, the following setup is recommended:

* **Operating System:** Windows 11
* **Python Interpreter:** Python 3.x
* **C++ Compiler:** Microsoft Visual C++ (MSVC) version 14.3 or later
* **IDE:** Visual Studio 2022 (Community Edition or higher)
* **Developer Command Prompt:** Visual Studio 2022 Developer Command Prompt (x64 Native Tools Command Prompt for VS 2022) v17.12 or newer
* **PowerShell:** Version 5.1.19041.1 or newer (bundled with Windows 10/11)

> ℹ️ Visual Studio 2022 is the preferred IDE for full compatibility across the entire project. However, contributions using other IDEs or editors are welcome, especially for non-C++ components.

### ❗ Mandatory for C++ Development

C++ components **must** be compiled using **MSVC** from within the **Visual Studio 2022 Developer Command Prompt (v17.12 or newer)**. Other compilers or environments are unsupported and may result in build errors.

---

## 🛠 How to Contribute

### 1️⃣ Fork the Repository

Click the **"Fork"** button on the top-right of the repository page to create your own copy.

### 2️⃣ Clone Your Fork

```bash
git clone https://github.com/your-username/roblox-custom-cursor.git
cd roblox-custom-cursor
```

### 3️⃣ Create a New Branch

Make a new branch for your feature or fix:

```bash
git checkout -b feature/your-feature-name
```

### 4️⃣ Make Your Changes

Update the code, fix bugs, or improve the interface! All contributions are welcome.

### 📦 Embed External Files (No Runtime Dependencies)

To maintain **portability** and reduce external file dependencies, please embed assets (such as icons, executables, or other files) directly in the code using base64 encoding

Use the following code snippet to convert a file to a base64 string:

```python
import base64

path = r"C:\your\file\here"

# Open the file and encode it
with open(path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

# Print the Base64 string
print(encoded_string)

# Uncomment one of the following lines to directly copy the output to the clipboard
# import pyperclip; pyperclip.copy(encoded_string); print("Copied to clipboard!")
# import subprocess; subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True).communicate(encoded_string.encode()); print("Copied to clipboard!")
```

Then, paste the resulting string into the code and decode it at runtime using `base64.b64decode()`. This script is also found under the `assets/scripts/` folder.

> 📁 **Important**: Although the file is embedded within the code, please also include the original file in the `assets/` folder. This facilitates development, testing, and future modifications. **This rule does not apply to dependencies used by opt-in features, which should prefer runtime download over the internet instead of base64 embedding.**

### 🖥️ Launcher Requirements (`rcur_importer_launcher`)

The `.rcur` importer launcher, written in C++, plays a critical role and must follow these requirements:

* **Prioritize minimalism and efficiency.** The code must introduce minimal overhead and remain as concise as possible without sacrificing readability.
* **The C++ source file must be located at**: `rcur_importer_launcher/rcur_importer_launcher.cpp`
* **The executable is not tracked by Git and should not be committed.** It is automatically excluded by `.gitignore` and rebuilt by CI during deployment.

#### 🛠️ Build Instructions (for Local Testing)

Use **MSVC (`cl.exe`)** to build the launcher before submitting changes. The executable **must compile cleanly with no warnings** and behave correctly under this command:

```cmd
cl rcur_importer_launcher.cpp /O2 /link shell32.lib /SUBSYSTEM:WINDOWS /INCREMENTAL:NO
```

* This command must be run and succeed from the Visual Studio 2022 Developer Command Prompt (version 17.12 or newer), specifically the x64 Native Tools Command Prompt for VS 2022.
* This ensures compatibility with the CI build system and prevents platform-specific deviations.
* You are expected to test your changes using this build locally before opening a pull request.

> ℹ️ The resulting `.exe` will be placed in the same folder and is ignored by Git.  
> ✅ CI will handle building and hashing the executable as part of the release pipeline.

---

### 5️⃣ Format Your Code (Style Guidelines)

Ensure your code follows standard Python formatting conventions:

#### 🐍 Python Formatting

* Use **4 spaces** for indentation (no tabs).
* Follow **PEP 8** for general style.
* Use **f-strings** for formatting text.
* When writing Python scripts as string values (e.g., for embedding or runtime execution), use `.format()` for string formatting to avoid syntax errors.
* Avoid hardcoding paths—use `os.path.join()` for file operations.
* Run **Black** to format your code before committing:

  ```bash
  black .
  ```
* Add docstrings to your functions using Sphinx/reStructuredText (reST) style. Follow PEP 257 for structure and consistency.
* Avoid referencing external files. Instead, embed them as base64 strings and decode them during runtime. The .pyw file should be able to run independently without relying on any external resource files.
* Ensure all tests pass before committing, especially after reformatting/changing base64 strings.

---

### 6️⃣ Commit Your Changes

Use descriptive and clear commit messages:

```bash
git commit -m "Add support for base64 cursor embedding"
```

### 7️⃣ Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 8️⃣ Open a Pull Request

* Go to your fork on GitHub.
* Click **"Compare & pull request"**.
* Provide a **summary of your changes**.
* Link to any relevant issues if applicable (e.g., `Fixes #7`).

---

## 📜 License

By contributing, you agree that your code will be **licensed under GPL-3.0**.

📌 **Your modifications must remain open-source and follow the terms of the GPL-3.0 license.**

---

Thank you for helping make Roblox Custom Cursor better! 🚀
