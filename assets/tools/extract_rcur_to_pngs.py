# -*- coding: utf-8 -*-
import os
import sys
import struct

MAGIC_HEADER = b"RCUR\x00"
VERSION = 2
EXPECTED_IMAGES = 3
OUTPUT_NAMES = ["ArrowFar.png", "Arrow.png", "IBeam.png"]

def extract_rcur(file_path, out_dir):
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        if not content.startswith(MAGIC_HEADER):
            raise ValueError("Invalid RCUR magic header.")

        offset = len(MAGIC_HEADER)
        version = struct.unpack("<I", content[offset:offset + 4])[0]
        if version != VERSION:
            print(f"Warning: File version is {version}, but expected {VERSION}. Continuing anyway.", file=sys.stderr)

        offset += 4
        lengths = struct.unpack("<" + "I" * EXPECTED_IMAGES, content[offset:offset + 4 * EXPECTED_IMAGES])
        offset += 4 * EXPECTED_IMAGES

        image_datas = []
        for length in lengths:
            image_data = content[offset:offset + length]
            if len(image_data) != length:
                raise ValueError("Corrupted image data length.")
            image_datas.append(image_data)
            offset += length

        os.makedirs(out_dir, exist_ok=True)
        for name, data in zip(OUTPUT_NAMES, image_datas):
            out_path = os.path.join(out_dir, name)
            with open(out_path, "wb") as out:
                out.write(data)

        print(f"Extracted: {file_path} → {out_dir}")
    except Exception as e:
        print(f"Extraction failed for '{file_path}': {e}", file=sys.stderr)

def print_usage():
    print("Usage:")
    print("  python extract_rcur_to_pngs.py file.rcur")
    print("  python extract_rcur_to_pngs.py --folder path_to_folder")
    print("  python extract_rcur_to_pngs.py file.rcur --folder path_to_folder")
    print()
    print("Extracts .rcur binary files into ArrowFar.png, Arrow.png, and IBeam.png.")
    print("The specified file extracts PNGs into the current directory.")
    print("All files in the folder (non-recursive) extract into subfolders named after each .rcur file.")

def main():
    args = sys.argv[1:]
    file_arg = None
    folder_arg = None

    i = 0
    while i < len(args):
        if args[i] == "--folder":
            if i + 1 >= len(args):
                print("Error: Missing folder path after --folder flag.", file=sys.stderr)
                print_usage()
                input("Press Enter to exit...")
                sys.exit(1)
            folder_arg = args[i + 1]
            i += 2
        else:
            if file_arg:
                print("Error: Only one .rcur file argument is allowed.", file=sys.stderr)
                print_usage()
                input("Press Enter to exit...")
                sys.exit(1)
            file_arg = args[i]
            i += 1

    if not file_arg and not folder_arg:
        print_usage()
        input("Press Enter to exit...")
        sys.exit(0)

    # Handle single file
    if file_arg:
        if not os.path.isfile(file_arg):
            print(f"File not found: {file_arg}", file=sys.stderr)
        else:
            extract_rcur(file_arg, os.getcwd())

    # Handle folder
    if folder_arg:
        if not os.path.isdir(folder_arg):
            print(f"Folder not found: {folder_arg}", file=sys.stderr)
            input("Press Enter to exit...")
            sys.exit(1)

        files = [f for f in os.listdir(folder_arg)
                 if f.lower().endswith(".rcur") and os.path.isfile(os.path.join(folder_arg, f))]
        if not files:
            print(f"No .rcur files found in folder: {folder_arg}")
            input("Press Enter to exit...")
            sys.exit(0)

        for filename in files:
            file_path = os.path.join(folder_arg, filename)
            out_dir = filename  # Use full filename including .rcur as folder name
            extract_rcur(file_path, out_dir)

if __name__ == "__main__":
    main()
