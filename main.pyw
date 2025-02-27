import os
import sys
import customtkinter as ctk
from tkinter import filedialog

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
    result_label.configure(text="Patches Combined Successfully!", text_color="green")

def addPatchFile():
    files = filedialog.askopenfilenames(title="Select Patch Files", filetypes=(("IPS Patch Files", "*.ips"), ("All Files", "*.*")))
    for file in files:
        patchList.append(file)
    
    patch_textbox.delete("1.0", ctk.END)
    patch_names = [os.path.basename(file) for file in patchList]
    patch_textbox.insert(ctk.END, "\n".join(patch_names))

def combineButtonClick():
    if len(patchList) > 1:
        combinePatches(patchList)
    else:
        result_label.configure(text="Please select more than one patch file.", text_color="red")

app = ctk.CTk()
app.title("Patch Combiner")
app.geometry("500x400")  # Set initial window size

frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill="both", expand=True)

patch_textbox = ctk.CTkTextbox(frame, height=200, width=400)
patch_textbox.pack(padx=10, pady=10)

add_button = ctk.CTkButton(frame, text="Add Patch File", command=addPatchFile)
add_button.pack(pady=10)

combine_button = ctk.CTkButton(frame, text="Combine Patches", command=combineButtonClick)
combine_button.pack(pady=10)

result_label = ctk.CTkLabel(frame, text="")
result_label.pack(pady=10)

app.mainloop()
