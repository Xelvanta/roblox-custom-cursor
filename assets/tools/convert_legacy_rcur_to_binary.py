# -*- coding: utf-8 -*-
import os
import sys
import base64
import struct

MAGIC_HEADER = b"RCUR\x00"
VERSION = 2
EXPECTED_IMAGES = 3

def convert_rcur_in_place(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) != EXPECTED_IMAGES:
            raise ValueError(f"Expected {EXPECTED_IMAGES} base64-encoded lines, found {len(lines)}.")

        image_datas = []
        for index, b64 in enumerate(lines):
            try:
                decoded = base64.b64decode(b64)
                image_datas.append(decoded)
            except base64.binascii.Error:
                raise ValueError(f"Line {index + 1} is not valid base64.")

        with open(file_path, "wb") as out:
            out.write(MAGIC_HEADER)
            out.write(struct.pack("<I", VERSION))
            for data in image_datas:
                out.write(struct.pack("<I", len(data)))
            for data in image_datas:
                out.write(data)

        print(f"Converted: {file_path}")
    except Exception as e:
        print(f"Conversion failed for '{file_path}': {e}", file=sys.stderr)

def print_usage():
    print("Usage:")
    print("  python convert_rcur_to_binary.py file1.rcur [file2.rcur ...]")
    print("  python convert_rcur_to_binary.py --folder path_to_folder")
    print()
    print("Converts legacy base64-encoded .rcur files to binary .rcur format in-place.")
    print("If --folder is specified, converts all .rcur files in the folder (no recursion).")

def main():
    args = sys.argv[1:]
    if not args:
        print_usage()
        input("Press Enter to exit...")
        sys.exit(0)

    if args[0] == "--folder":
        if len(args) < 2:
            print("Error: Missing folder path after --folder flag.", file=sys.stderr)
            print_usage()
            input("Press Enter to exit...")
            sys.exit(1)
        folder = args[1]
        if not os.path.isdir(folder):
            print(f"Folder not found: {folder}", file=sys.stderr)
            input("Press Enter to exit...")
            sys.exit(1)
        # Process all .rcur files (non-recursive)
        files = [f for f in os.listdir(folder) if f.lower().endswith(".rcur") and os.path.isfile(os.path.join(folder, f))]
        if not files:
            print(f"No .rcur files found in folder: {folder}")
            input("Press Enter to exit...")
            sys.exit(0)
        for filename in files:
            file_path = os.path.join(folder, filename)
            convert_rcur_in_place(file_path)
    else:
        # Treat all args as individual files
        for file_path in args:
            if not os.path.isfile(file_path):
                print(f"File not found: {file_path}", file=sys.stderr)
                continue
            convert_rcur_in_place(file_path)

if __name__ == "__main__":
    main()
