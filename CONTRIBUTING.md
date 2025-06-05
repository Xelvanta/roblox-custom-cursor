# 🖱️ Contributing to Roblox Custom Cursor

Thank you for your interest in contributing to **[Roblox Custom Cursor](https://github.com/Xelvanta/roblox-custom-cursor)**! 🎉 This project is licensed under the **GPL 3.0** license, so all contributions must also be open-source under the same license.

We welcome all kinds of contributions, including **bug reports, feature additions, image enhancements, documentation improvements, and code contributions**. Please follow the steps below to ensure a smooth contribution process.

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

### 📦 External File Dependencies Not Allowed

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

> 📁 **Important**: Although the file is embedded within the code, please also include the original file in the `assets/` folder. This facilitates development, testing, and future modifications. This rule does not apply to optional dependencies.

### 🖥️ Launcher Requirements (rcur_importer_launcher)

The .rcur importer launcher, written in C#, plays a critical role and must follow these requirements:

* **Compile with Ahead-Of-Time (AOT) compilation enabled.** This improves startup performance and portability.
* **Do NOT use top-level statements.** Instead, implement a classic `Program` class with a `static void Main(string[] args)` entry point for clarity and compatibility.
* **Prioritize minimalism and efficiency.** The code must introduce minimal overhead and remain as concise as possible without sacrificing readability.
* **Use .NET 8 LTS for building the launcher** to ensure the publish folder is net8.0-windows as expected; building with other versions (like .NET 9) will create different folders and break path assumptions.
* **The executable file must be located at** `rcur_importer_launcher/bin/Release/net8.0-windows/win-x64/publish/rcur_importer_launcher.exe` and MUST be committed to the repository.

Example:

```csharp
class Program
{
    static void Main(string[] args)
    {
        // Launcher code here
    }
}
```

Build command:
```ps1
dotnet publish -c Release -r win-x64 --self-contained true /p:PublishAot=true
```

---

### 5️⃣ Format Your Code (Style Guidelines)

Ensure your code follows standard Python formatting conventions:

#### 🐍 Python Formatting

* Use **4 spaces** for indentation (no tabs).
* Follow **PEP 8** for general style.
* Use **f-strings** for formatting text.
* Use .format() for string formatting inside inline scripts to avoid syntax errors, especially when embedding multiline strings in code.
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
