import base64

path = r"C:\Program Files\Xelvanta Softworks\Roblox Custom Cursor\rcur_importer_launcher.exe"

# Open the file and encode it
with open(path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

# Print the Base64 string
print(encoded_string)

# Uncomment one of the following lines to directly copy the output to the clipboard
# import pyperclip; pyperclip.copy(encoded_string); print("Copied to clipboard!")
# import subprocess; subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True).communicate(encoded_string.encode()); print("Copied to clipboard!")