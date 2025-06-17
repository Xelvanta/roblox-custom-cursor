---
name: Bug report
about: Create a report to help us improve
title: "[BUG]"
labels: ''
assignees: Xelvanta

---

## 🐞 Bug Report

### Describe the bug
A clear and concise description of what the bug is or what is not working as expected.

---

### ✅ To Reproduce
Steps to reproduce the behavior:
1. Open the app via [...]
2. Click on [...]
3. Observe that [...]

If the bug appears during startup or silently fails, see the "Debugging Help" section below.

---

### 🧠 Expected Behavior
What you expected to happen instead of the bug.

---

### 📸 Screenshots / Video (if applicable)
Include screenshots or a screen recording to help illustrate the issue, if possible.

---

### 🧪 Debugging Help (Advanced)
If the app launches silently or crashes with no visible error, try manually launching it with `python.exe` instead of `pythonw.exe`:

```cmd
cd roblox-custom-cursor
"app\python\python.exe" "Roblox Custom Cursor.rccapp"
````

or:

```cmd
cd roblox-custom-cursor
"app\python\python.exe" "rcur_importer.rccapp" "Roblox Custom Cursor Profile.rcur"
````

This will show error messages in the console, which can help pinpoint the issue. Paste any error output below if you're able to:

```
<insert traceback or console output here>
```

---

### 💻 System Info

Please complete the following:

* **OS Version:** (e.g., Windows 11 24H2)
* **RCC Version:** (e.g., 3.4.0.2)
* **How you launched it:** (e.g., double-clicked `.rccapp`, ran via command line, used start menu shortcut, etc.)
* **Admin privileges:** \[Yes/No]
* **Multiple monitors:** \[Yes/No]

---

### 📝 Additional Context

Add any other info here, such as:

* Whether you're using custom themes or files
* If this occurred after an update
* Whether `.rcur` or `.rccapp` file types were modified or reassociated
