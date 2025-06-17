# 🔐 Security Policy

## Supported Versions

The following table shows which versions of Roblox Custom Cursor are currently receiving security updates:


| Version            | Supported?    |
| ------------------ | ------------- |
| Latest minor version series  | Yes |
| All previous minor versions  | No  |

> Only the latest minor version series of the current major release and generation receives security updates and support. Older minor versions and their patch releases do not receive updates and are no longer supported.

---

## Installer Permissions

The Windows `RCC3_Installer.exe` for Roblox Custom Cursor may request administrator privileges to:
- Register file extensions (`.rccapp`, `.rcur`) in the Windows Registry
- Install files to protected system directories such as `C:\Program Files (x86)\Roblox Custom Cursor\`

The installer performs no network access or background service installation.

---

## Reporting a Vulnerability

If you discover a potential vulnerability — including:
- Unsafe file extension registration or registry key handling
- Arbitrary code execution via `.rcur` or `.rccapp` files
- Privilege escalation or path/dll hijacking

Please report it privately by emailing [Xelvanta@proton.me](mailto:Xelvanta@proton.me) or opening a private security advisory via GitHub.

We take even local-only security issues seriously.

---

## What This App Does **Not** Do

- ❌ No telemetry or remote connections  
- ❌ No background processes or startup registration  
- ❌ No automatic updates  
- ❌ No use of external APIs or cloud services  
