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

### 📦 Embed Images as Base64 (For Portability)

To maintain **portability** and reduce external file dependencies, please embed image assets (such as icons or cursors) directly in the code using base64 encoding.

Use the following code snippet to convert an image to a base64 string:

```python
import base64

image_path = r"path\to\your\image\here.png"

with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
print(encoded_string)
```

Then, paste the resulting string into the code and decode it at runtime using `base64.b64decode()`.

> 📁 **Important**: Even though the image is embedded in the code, still include the original image file in the `assets/` folder. This helps with development, testing, and future edits.

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
