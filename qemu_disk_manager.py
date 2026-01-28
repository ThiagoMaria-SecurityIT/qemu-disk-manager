import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import glob
import csv
from datetime import datetime

class QEMUDiskCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("QEMU Virtual Disk Manager")
        self.root.geometry("900x800")  # Wider for the table
        
        # Configure grid weights for responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        
        # Variables
        self.disk_path = tk.StringVar()
        self.disk_format = tk.StringVar(value="qcow2")
        self.disk_size = tk.StringVar(value="20G")
        self.created_disks = []  # Store created disk info
        
        # Title
        title_label = ttk.Label(root, text="QEMU Virtual Disk Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Folder Selection Section
        folder_frame = ttk.LabelFrame(root, text="1. Select Disk Location", padding=10)
        folder_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(0, weight=1)
        
        # Path entry and browse button
        path_frame = ttk.Frame(folder_frame)
        path_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        path_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.disk_path, 
                 font=("Courier", 10)).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(path_frame, text="Browse Folder", 
                  command=self.browse_folder).grid(row=0, column=1)
        
        # Scan Folder button
        button_frame = ttk.Frame(folder_frame)
        button_frame.grid(row=1, column=0, sticky="w")
        ttk.Button(button_frame, text="Scan Folder for Virtual Disks", 
                  command=self.scan_folder, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Label(button_frame, text="(Scans for .qcow2 and .raw files)").pack(side=tk.LEFT, padx=(10, 0))
        
        # Disk Creation Section
        create_frame = ttk.LabelFrame(root, text="2. Create Virtual Disk", padding=10)
        create_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Format selection (qcow2 vs raw)
        ttk.Label(create_frame, text="Disk Format:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        format_frame = ttk.Frame(create_frame)
        format_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Radiobutton(format_frame, text="QCOW2 (Recommended)", 
                       variable=self.disk_format, value="qcow2").pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(format_frame, text="RAW", 
                       variable=self.disk_format, value="raw").pack(side=tk.LEFT)
        
        # Size selection
        ttk.Label(create_frame, text="Disk Size:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky="w")
        
        size_frame = ttk.Frame(create_frame)
        size_frame.grid(row=1, column=1, sticky="w", pady=5)
        
        size_entry = ttk.Entry(size_frame, textvariable=self.disk_size, width=10)
        size_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(size_frame, text="(e.g., 20G, 50G, 100G)").pack(side=tk.LEFT)
        
        # Create button
        ttk.Button(create_frame, text="Create Virtual Disk", 
                  command=self.create_disk, style="Accent.TButton").grid(row=2, column=0, columnspan=2, pady=(15, 5))
        
        # Disk Management Section
        manage_frame = ttk.LabelFrame(root, text="3. Created Virtual Disks", padding=10)
        manage_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        manage_frame.grid_columnconfigure(0, weight=1)
        manage_frame.grid_rowconfigure(1, weight=1)
        
        # Treeview for table display
        tree_frame = ttk.Frame(manage_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Create vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        # Create Treeview with columns
        columns = ("filename", "size", "format", "path")
        self.disk_tree = ttk.Treeview(tree_frame, columns=columns, 
                                     show="headings", height=8,
                                     yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.disk_tree.yview)
        h_scrollbar.config(command=self.disk_tree.xview)
        
        # Define column headings and widths
        column_config = [
            ("filename", "Filename", 150),
            ("size", "Size", 100),
            ("format", "Format", 80),
            ("path", "Path", 400)
        ]
        
        for col_id, col_text, col_width in column_config:
            self.disk_tree.heading(col_id, text=col_text)
            self.disk_tree.column(col_id, width=col_width, minwidth=50)
        
        self.disk_tree.grid(row=0, column=0, sticky="nsew")
        
        # Add a tag for alternate row colors
        self.disk_tree.tag_configure('oddrow', background='#f0f0f0')
        self.disk_tree.tag_configure('evenrow', background='white')
        
        # Bind double-click event to show full path
        self.disk_tree.bind("<Double-1>", self.on_double_click)
        
        # Buttons for disk management
        button_frame = ttk.Frame(manage_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(button_frame, text="Show Full Path", 
                  command=self.show_full_path).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Copy Path to Clipboard", 
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Get Disk Info", 
                  command=self.get_disk_info).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv, style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove from List", 
                  command=self.remove_from_list, style="Danger.TButton").pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to create virtual disks")
        status_bar = ttk.Label(root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 5))
        
        # Configure styles
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        style.configure("Secondary.TButton", font=("Arial", 10))
        style.configure("Danger.TButton", font=("Arial", 10, "bold"), foreground="red")
        style.configure("Treeview", font=("Courier", 9))
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))

    def browse_folder(self):
        """Open folder browser dialog"""
        folder_selected = filedialog.askdirectory(title="Select Folder for Virtual Disk")
        if folder_selected:
            self.disk_path.set(folder_selected)
            self.status_var.set(f"Selected folder: {folder_selected}")

    def scan_folder(self):
        """Scan selected folder for QEMU virtual disk files"""
        folder = self.disk_path.get()
        
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Error", "Please select a valid folder first!")
            return
        
        # Show scanning status
        self.status_var.set(f"Scanning folder: {folder}...")
        self.root.update()
        
        try:
            # Find all .qcow2 and .raw files in the folder and subdirectories
            qcow2_files = glob.glob(os.path.join(folder, "**", "*.qcow2"), recursive=True)
            raw_files = glob.glob(os.path.join(folder, "**", "*.raw"), recursive=True)
            
            all_files = qcow2_files + raw_files
            
            if not all_files:
                messagebox.showinfo("Scan Results", f"No virtual disk files (.qcow2 or .raw) found in:\n{folder}")
                self.status_var.set("No virtual disks found")
                return
            
            added_count = 0
            duplicate_count = 0
            
            for file_path in all_files:
                try:
                    # Get disk information using qemu-img
                    cmd = ["qemu-img", "info", file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    # Parse the output to get virtual size
                    virtual_size = None
                    disk_format = None
                    
                    for line in result.stdout.split('\n'):
                        if 'virtual size' in line.lower():
                            # Extract size value (e.g., "20G (21474836480 bytes)")
                            parts = line.split('(')[0].strip().split()
                            if len(parts) >= 3:
                                virtual_size = parts[2]  # Gets "20G"
                        elif 'file format' in line.lower():
                            disk_format = line.split(':')[-1].strip()
                    
                    if not virtual_size:
                        virtual_size = "Unknown"
                    if not disk_format:
                        # Fallback: determine from file extension
                        disk_format = "qcow2" if file_path.lower().endswith('.qcow2') else "raw"
                    
                    # Get filename without path
                    filename = os.path.basename(file_path)
                    
                    # Create disk info dictionary
                    disk_info = {
                        "filename": filename,
                        "full_path": file_path,
                        "format": disk_format,
                        "size": virtual_size
                    }
                    
                    # Check for duplicates using all 4 values
                    is_duplicate = False
                    for existing_disk in self.created_disks:
                        if (existing_disk["filename"] == disk_info["filename"] and
                            existing_disk["size"] == disk_info["size"] and
                            existing_disk["format"] == disk_info["format"] and
                            os.path.normpath(existing_disk["full_path"]) == os.path.normpath(disk_info["full_path"])):
                            is_duplicate = True
                            duplicate_count += 1
                            break
                    
                    # Add to list if not a duplicate
                    if not is_duplicate:
                        # Check if we already have this disk in list (by full path only)
                        existing_paths = [d["full_path"] for d in self.created_disks]
                        if file_path not in existing_paths:
                            self.add_disk_to_tree(disk_info)
                            self.created_disks.append(disk_info)
                            added_count += 1
                            
                except subprocess.CalledProcessError as e:
                    # Skip files that aren't valid QEMU disk images
                    continue
                except Exception as e:
                    # Skip files with other errors
                    continue
            
            # Update status
            self.status_var.set(f"Scan complete: Added {added_count} disks, skipped {duplicate_count} duplicates")
            
            if added_count > 0:
                messagebox.showinfo("Scan Complete", 
                                  f"Found {len(all_files)} virtual disk file(s).\n"
                                  f"Added {added_count} to the list.\n"
                                  f"Skipped {duplicate_count} duplicate(s).")
            else:
                messagebox.showinfo("Scan Complete", 
                                  f"No new virtual disks found.\n"
                                  f"All {len(all_files)} file(s) were already in the list or were duplicates.")
                
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning folder:\n{str(e)}")
            self.status_var.set("Scan failed")

    def add_disk_to_tree(self, disk_info):
        """Add a disk to the Treeview table"""
        # Prepare values for each column
        filename = disk_info.get("filename", "N/A")
        size = disk_info.get("size", "Unknown")
        format_ = disk_info.get("format", "Unknown")
        path = disk_info.get("full_path", "")
        
        # Insert into tree
        item_id = self.disk_tree.insert("", tk.END, values=(filename, size, format_, path))
        
        # Apply alternating row colors
        if len(self.disk_tree.get_children()) % 2 == 0:
            self.disk_tree.item(item_id, tags=('evenrow',))
        else:
            self.disk_tree.item(item_id, tags=('oddrow',))

    def create_disk(self):
        """Create virtual disk using qemu-img command"""
        # Validate inputs
        folder = self.disk_path.get()
        disk_format = self.disk_format.get()
        size = self.disk_size.get().strip().upper()
        
        if not folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
        
        # Validate size format (e.g., 20G, 100M)
        if not (size[:-1].isdigit() and size[-1] in ['K', 'M', 'G', 'T']):
            messagebox.showerror("Error", "Invalid size format! Use format like: 20G, 100M, 1T")
            return
        
        # Ask for disk filename
        disk_name = filedialog.asksaveasfilename(
            initialdir=folder,
            title="Save Virtual Disk As",
            defaultextension=f".{disk_format}",
            filetypes=[(f"{disk_format.upper()} files", f"*.{disk_format}"), ("All files", "*.*")]
        )
        
        if not disk_name:
            return  # User cancelled
        
        try:
            # Build qemu-img command
            cmd = ["qemu-img", "create", "-f", disk_format, disk_name, size]
            
            # Execute command
            self.status_var.set(f"Creating {size} {disk_format} disk...")
            self.root.update()
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Add to list
            disk_info = {
                "filename": os.path.basename(disk_name),
                "full_path": disk_name,
                "format": disk_format,
                "size": size
            }
            
            self.add_disk_to_tree(disk_info)
            self.created_disks.append(disk_info)
            
            self.status_var.set(f"Successfully created: {os.path.basename(disk_name)}")
            messagebox.showinfo("Success", f"Virtual disk created successfully!\n\n"
                                          f"Path: {disk_name}\n"
                                          f"Format: {disk_format}\n"
                                          f"Size: {size}")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to create disk:\n{e.stderr}")
            self.status_var.set("Disk creation failed")
        except FileNotFoundError:
            messagebox.showerror("Error", "qemu-img not found! Make sure QEMU is installed and in your PATH.")
            self.status_var.set("QEMU not found")

    def on_double_click(self, event):
        """Handle double-click on treeview item"""
        self.show_full_path()

    def get_selected_disk(self):
        """Get the currently selected disk info"""
        selection = self.disk_tree.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        item_values = self.disk_tree.item(item_id, 'values')
        
        if not item_values:
            return None
        
        # Find the corresponding disk info in created_disks
        filename = item_values[0]
        path = item_values[3] if len(item_values) > 3 else ""
        
        for disk in self.created_disks:
            if disk["filename"] == filename and disk.get("full_path", "") == path:
                return disk
        
        return None

    def show_full_path(self):
        """Show full path of selected disk"""
        disk_info = self.get_selected_disk()
        if not disk_info:
            messagebox.showwarning("Warning", "Please select a disk from the list first!")
            return
        
        path = disk_info.get("full_path", "")
        if not path:
            messagebox.showinfo("Disk Path", "No path information available for this disk.")
            self.status_var.set("No path information available")
            return
        
        messagebox.showinfo("Disk Path", f"Full path:\n{path}")
        self.status_var.set(f"Showing path for: {disk_info['filename']}")

    def copy_to_clipboard(self):
        """Copy selected disk path to clipboard"""
        disk_info = self.get_selected_disk()
        if not disk_info:
            messagebox.showwarning("Warning", "Please select a disk from the list first!")
            return
        
        path = disk_info.get("full_path", "")
        if not path:
            messagebox.showwarning("Warning", "No path available to copy!")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self.status_var.set(f"Copied to clipboard: {disk_info['filename']}")
        messagebox.showinfo("Copied", "Path copied to clipboard!")

    def get_disk_info(self):
        """Get detailed information about selected disk using qemu-img info"""
        disk_info = self.get_selected_disk()
        if not disk_info:
            messagebox.showwarning("Warning", "Please select a disk from the list first!")
            return
        
        path = disk_info.get("full_path", "")
        if not path:
            messagebox.showwarning("Warning", "No path information available for this disk!")
            return
        
        try:
            # Run qemu-img info command
            cmd = ["qemu-img", "info", path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Show info in message box
            info_text = f"Disk: {disk_info['filename']}\n"
            info_text += f"Path: {path}\n"
            info_text += f"Format: {disk_info.get('format', 'Unknown')}\n"
            info_text += f"Virtual Size: {disk_info.get('size', 'Unknown')}\n\n"
            info_text += "Detailed Information:\n"
            info_text += "-" * 40 + "\n"
            info_text += result.stdout
            
            # Create a scrolled text window for better viewing
            info_window = tk.Toplevel(self.root)
            info_window.title(f"Disk Information: {disk_info['filename']}")
            info_window.geometry("600x400")
            
            text_frame = ttk.Frame(info_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                 font=("Courier", 9))
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
            
            self.status_var.set(f"Retrieved info for: {disk_info['filename']}")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to get disk info:\n{e.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Error", "qemu-img not found!")

    def export_to_csv(self):
        """Export the disk list to a CSV file"""
        if not self.created_disks:
            messagebox.showwarning("Warning", "No disks in the list to export!")
            return
        
        # Ask for save location
        default_filename = f"qemu_disks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV field names
                fieldnames = ['Filename', 'Size', 'Format', 'Path', 'Scan_Date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write each disk
                for disk in self.created_disks:
                    writer.writerow({
                        'Filename': disk.get('filename', ''),
                        'Size': disk.get('size', ''),
                        'Format': disk.get('format', ''),
                        'Path': disk.get('full_path', ''),  # Empty string if path not available
                        'Scan_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            # Show success message
            messagebox.showinfo("Export Successful", 
                              f"Exported {len(self.created_disks)} disk(s) to:\n{file_path}")
            self.status_var.set(f"Exported to CSV: {os.path.basename(file_path)}")
            
            # Offer to open the CSV file
            if messagebox.askyesno("Open File", "Would you like to open the CSV file now?"):
                os.startfile(file_path)
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
            self.status_var.set("CSV export failed")

    def remove_from_list(self):
        """Remove selected disk from the list (does not delete the file)"""
        disk_info = self.get_selected_disk()
        if not disk_info:
            messagebox.showwarning("Warning", "Please select a disk from the list first!")
            return
        
        # Confirm removal
        filename = disk_info.get('filename', 'Unknown')
        if messagebox.askyesno("Confirm", f"Remove '{filename}' from the list?\n\nNote: This does NOT delete the actual file."):
            # Remove from tree
            selection = self.disk_tree.selection()
            if selection:
                self.disk_tree.delete(selection[0])
            
            # Remove from created_disks list
            path = disk_info.get('full_path', '')
            self.created_disks = [d for d in self.created_disks 
                                 if not (d.get('filename') == filename and 
                                        d.get('full_path', '') == path)]
            
            self.status_var.set(f"Removed from list: {filename}")

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = QEMUDiskCreator(root)
    root.mainloop()