import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def add_apks():
    apk_paths = filedialog.askopenfilenames(title="Select APKs", filetypes=[("APK files", "*.apk")])
    for apk in apk_paths:
        if apk not in apk_listbox.get(0, tk.END):
            apk_listbox.insert(tk.END, apk)

def move_up():
    selected = apk_listbox.curselection()
    for index in selected:
        if index == 0:
            continue
        apk = apk_listbox.get(index)
        apk_listbox.delete(index)
        apk_listbox.insert(index - 1, apk)
        apk_listbox.selection_set(index - 1)

def move_down():
    selected = reversed(apk_listbox.curselection())
    for index in selected:
        if index == apk_listbox.size() - 1:
            continue
        apk = apk_listbox.get(index)
        apk_listbox.delete(index)
        apk_listbox.insert(index + 1, apk)
        apk_listbox.selection_set(index + 1)

def detect_devices():
    try:
        devices_result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devices = [line.split()[0] for line in devices_result.stdout.splitlines() if "\tdevice" in line]
        devices_listbox.delete(0, tk.END)
        for device in devices:
            devices_listbox.insert(tk.END, device)
    except FileNotFoundError:
        messagebox.showerror("Error", "ADB not found. Make sure ADB is installed and in your PATH.")

def install_apks():
    apk_paths = apk_listbox.get(0, tk.END)
    selected_indices = devices_listbox.curselection()
    devices = [devices_listbox.get(i) for i in selected_indices]

    if not apk_paths:
        messagebox.showwarning("No APKs", "Please add APKs to install.")
        return
    if not devices:
        messagebox.showwarning("No Devices", "Please select at least one device.")
        return

    for device_id in devices:
        for i, apk_path in enumerate(apk_paths, start=1):
            apk_name = apk_path.split("/")[-1]
            status_label.config(text=f"[{device_id}] Installing {i}/{len(apk_paths)}: {apk_name}")
            root.update_idletasks()

            try:
                install_result = subprocess.run(["adb", "-s", device_id, "install", "-r", apk_path],
                                                capture_output=True, text=True)
                if "Success" in install_result.stdout:
                    messagebox.showinfo("Success", f"{apk_name} installed successfully on device {device_id}!")
                else:
                    messagebox.showerror("Error", f"Failed to install {apk_name} on {device_id}:\n"
                                                  f"{install_result.stdout}\n{install_result.stderr}")
            except Exception as e:
                messagebox.showerror("Error", f"Unexpected error installing {apk_name} on {device_id}:\n{e}")

    status_label.config(text="All APKs installed on all selected devices.")

# GUI
root = tk.Tk()
root.title("ADB APK installer")
root.geometry("600x500")

# APK list
apk_frame = tk.Frame(root)
apk_frame.pack(pady=10)

apk_listbox = tk.Listbox(apk_frame, width=70, selectmode=tk.MULTIPLE)
apk_listbox.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(apk_frame, orient=tk.VERTICAL)
scrollbar.config(command=apk_listbox.yview)
apk_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

apk_buttons = tk.Frame(root)
apk_buttons.pack(pady=5)
tk.Button(apk_buttons, text="Add APKs", command=add_apks, width=15).grid(row=0, column=0, padx=5)
tk.Button(apk_buttons, text="Move Up", command=move_up, width=15).grid(row=0, column=1, padx=5)
tk.Button(apk_buttons, text="Move Down", command=move_down, width=15).grid(row=0, column=2, padx=5)

# Device list
device_frame = tk.Frame(root)
device_frame.pack(pady=10)
tk.Label(device_frame, text="Connected Devices:").pack()
devices_listbox = tk.Listbox(device_frame, width=70, selectmode=tk.MULTIPLE)
devices_listbox.pack()
tk.Button(device_frame, text="Detect Devices", command=detect_devices, width=20).pack(pady=5)

# Install button
tk.Button(root, text="Install APKs on Selected Devices", command=install_apks, width=35, height=2).pack(pady=15)

# Status label
status_label = tk.Label(root, text="No APK selected.", fg="blue")
status_label.pack(pady=10)

root.mainloop()
