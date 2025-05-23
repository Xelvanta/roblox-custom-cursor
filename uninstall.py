import os
import ctypes
import shutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    target_folder = os.path.join(
        os.environ["SystemDrive"] + "\\\\",
        "Program Files", "Xelvanta Softworks", "Roblox Custom Cursor"
    )

    if not is_admin():
        print("This script must be run with administrator privileges.")
        print("You can run the following command in PowerShell:")
        print('cd roblox-custom-cursor; Start-Process -FilePath "python.exe" -ArgumentList "uninstall.py" -Verb RunAs')
        print("Press Enter to exit...")
        input()
        return

    if not os.path.exists(target_folder):
        print("Target folder does not exist:")
        print(target_folder)
        print("Press Enter to exit...")
        input()
        return

    print("Are you sure you want to delete the following folder and all its contents?")
    print(target_folder)
    confirm = input("Type 'y' to confirm: ").strip().lower()

    if confirm == 'y':
        try:
            shutil.rmtree(target_folder)
            print("Roblox Custom Cursor folder deleted successfully.")

            print("\n=== Additional Step Required to Remove Roblox Custom Cursor Registry Entries ===")
            print("To fully remove the .rcur file type association from Windows,")
            print("open the main app, go to Settings (top-right), and click 'Unassociate .rcur File Type'.")

        except Exception as e:
            print("An error occurred while deleting the folder:")
            print(e)
    else:
        print("Operation cancelled.")

    print("Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()
