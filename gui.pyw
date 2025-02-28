import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
import os, json

def parse_ips_patch():
    file_path = filedialog.askopenfilename(title="Select Patch Files", filetypes=(("IPS Patch Files", "*.ips"), ("All Files", "*.*")))
    if not file_path:
        status_label.configure(text="Operation Aborted.")
        return
    
    with open(file_path, "rb") as f:
        data = f.read()

    if not data.startswith(b"PATCH"):
        status_label.configure(text="Invalid IPS Patch.")
        return

    index = 5
    patches = []
    while index < len(data) - 3: 
        offset = int.from_bytes(data[index:index+3], byteorder='big')
        index += 3
        size = int.from_bytes(data[index:index+2], byteorder='big')
        index += 2
        if size == 0:
            rle_size = int.from_bytes(data[index:index+2], byteorder='big')
            index += 2
            rle_value = data[index]
            index += 1

            patches.append({
                "offset": offset,
                "size": rle_size,
                "values": [rle_value] * rle_size, 
                "rle": True
            })
        else:
            patch_values = list(data[index:index+size])
            index += size

            patches.append({
                "offset": offset,
                "size": size,
                "values": patch_values,
                "rle": False
            })

    if data[-3:] != b"EOF":
        status_label.configure(text="Invalid IPS Patch.")
        return

    jsonFile = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Text JSON Files", "*.json"), ("All Files", "*.*")], title="Save JSON As")
    if not jsonFile:
        status_label.configure(text="Operation Aborted.")
        return

    with open(jsonFile, "w", encoding="utf-8") as json_out:
        json.dump(patches, json_out, indent=4)

    status_label.configure(text=f"Text JSON File created: {jsonFile}")
    return patches

patchList = []

def combinePatches(patchList: list):
    outputFilePath = filedialog.asksaveasfilename(defaultextension=".ips", filetypes=[("IPS Patch Files", "*.ips"), ("All Files", "*.*")], title="Save IPS Patch As")
    with open(outputFilePath, 'wb') as outF:
        outF.write(b'PATCH')
        for patch in patchList:
            with open(patch, 'rb') as f:
                data = f.read()
                data = data[5:len(data)-3]
                outF.write(data)
        outF.write(b"EOF")
    status_label.configure(text="Patches Combined Successfully!")

def addPatchFile():
    files = filedialog.askopenfilenames(title="Select Patch Files", filetypes=(("IPS Patch Files", "*.ips"), ("All Files", "*.*")))
    for file in files:
        patchList.append(file)

    patch_names = [os.path.basename(file) for file in patchList]
    combineButtonClick()

def combineButtonClick():
    if len(patchList) > 1:
        combinePatches(patchList)
    else:
        status_label.configure(text="Please select more than one IPS Patch.")

def create_ips_patch(original_file, modified_file, patch_file):
    """Creates an IPS patch comparing an original and modified ROM."""
    with open(original_file, "rb") as f:
        original_data = f.read()
    
    with open(modified_file, "rb") as f:
        modified_data = f.read()
    
    max_length = max(len(original_data), len(modified_data))
    original_data = original_data.ljust(max_length, b'\x00')
    modified_data = modified_data.ljust(max_length, b'\x00')

    patch = bytearray(b"PATCH")

    i = 0
    while i < max_length:
        if original_data[i] != modified_data[i]:
            start = i
            patch_data = []

            while i < max_length and original_data[i] != modified_data[i]:
                patch_data.append(modified_data[i])
                i += 1

            patch += start.to_bytes(3, "big")
            patch += len(patch_data).to_bytes(2, "big")
            patch += bytes(patch_data)
        else:
            i += 1

    patch += b"EOF"

    with open(patch_file, "wb") as f:
        f.write(patch)

    status_label.configure(text=f"IPS Patch created: {patch_file}")

def apply_ips_patch(rom_file, patch_file, output_file):
    """Applies an IPS patch to a ROM without external modules."""
    with open(rom_file, "rb") as f:
        rom_data = bytearray(f.read())

    with open(patch_file, "rb") as f:
        patch_data = f.read()

    if not patch_data.startswith(b"PATCH") or not patch_data.endswith(b"EOF"):
        status_label.configure(text="Invalid IPS patch.")
        return

    index = 5
    while index < len(patch_data) - 3:
        offset = int.from_bytes(patch_data[index:index + 3], "big")
        index += 3
        length = int.from_bytes(patch_data[index:index + 2], "big")
        index += 2

        if length == 0:
            status_label.configure(text="RLE encoding not supported.")
            return

        patch_bytes = patch_data[index:index + length]
        index += length

        rom_data[offset:offset + length] = patch_bytes

    with open(output_file, "wb") as f:
        f.write(rom_data)

    status_label.configure(text=f"IPS patch applied: {output_file}")

def select_files_for_patch_creation():
    """Opens a single file dialog to select original, modified, and save location for IPS patch."""
    original_file = filedialog.askopenfilename(title="Select The Original UNMODIFIED ROM", filetypes=[("BIN files", "*.bin")])
    if not original_file:
        status_label.configure(text="Operation Aborted.")
        return

    modified_file = filedialog.askopenfilename(title="Select The MODIFIED ROM", filetypes=[("BIN files", "*.bin")])
    if not modified_file:
        status_label.configure(text="Operation Aborted.")
        return

    patch_file = filedialog.asksaveasfilename(title="Save IPS Patch As", defaultextension=".ips", filetypes=[("IPS Patch", "*.ips")])
    if not patch_file:
        status_label.configure(text="No Save-Location Selected.")
        return

    create_ips_patch(original_file, modified_file, patch_file)

def select_files_for_patch_application():
    """Selects a ROM and IPS patch, then asks where to save the modified ROM."""
    rom_file = filedialog.askopenfilename(title="Select ROM to Patch", filetypes=[("BIN files", "*.bin")])
    if not rom_file:
        status_label.configure(text="No ROM File Selected.")
        return

    patch_file = filedialog.askopenfilename(title="Select IPS Patch", filetypes=[("IPS Patch", "*.ips")])
    if not patch_file:
        status_label.configure(text="No IPS Patch Selected.")
        return

    output_file = filedialog.asksaveasfilename(title="Save Patched ROM File As", defaultextension=".bin", filetypes=[("BIN files", "*.bin")])
    if not output_file:
        status_label.configure(text="No Output ROM Selected.")
        return

    apply_ips_patch(rom_file, patch_file, output_file)

def about_app():
    messagebox.showinfo("About - IPS Patch Tool", "Developers:\n- Cracko298\n- Pizzaleader\n- MC3DS Community\n\nGitHub:\nhttps://github.com/Minecraft-3DS-Community")


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("MC3DS Community | IPS Patching Tool")
app.geometry("500x300")
app.resizable(False, False)

title_label = ctk.CTkLabel(app, text="IPS Patching Tool", font=("Arial", 18, "bold"))
title_label.pack(pady=(10, 5))

create_patch_button = ctk.CTkButton(app, text="Create IPS Patch", command=select_files_for_patch_creation)
create_patch_button.pack(pady=5)

apply_patch_button = ctk.CTkButton(app, text="Apply IPS Patch", command=select_files_for_patch_application)
apply_patch_button.pack(pady=5)

combine_button = ctk.CTkButton(app, text="Combine IPS Patches", command=addPatchFile)
combine_button.pack(pady=5)

parse_button = ctk.CTkButton(app, text="Parse IPS Patches", command=parse_ips_patch)
parse_button.pack(pady=5)

about_button = ctk.CTkButton(app, text="About", command=about_app)
about_button.pack(pady=5)


status_label = ctk.CTkLabel(app, text="", text_color="lightgray")
status_label.pack(pady=10)

app.mainloop()
