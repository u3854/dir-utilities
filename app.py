import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core import Directory
from pathlib import Path
import sv_ttk

class DirectoryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Patch Manager UI")
        self.root.geometry("600x500")

        sv_ttk.set_theme("dark")

        self.dir_manager = None
        self.base_path = None
        self.target_path = None

        # --- Top Section: Selection ---
        frame_top = ttk.LabelFrame(root, text="Configuration", padding=10)
        frame_top.pack(fill="x", padx=10, pady=5)

        # Base Dir Selection
        self.btn_base = ttk.Button(frame_top, text="Select Base Folder", command=self.select_base)
        self.btn_base.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.lbl_base = ttk.Label(frame_top, text="No folder selected", foreground="gray")
        self.lbl_base.grid(row=0, column=1, sticky="w", padx=5)

        # Target Dir Selection
        self.btn_target = ttk.Button(frame_top, text="Select Target (Optional)", command=self.select_target)
        self.btn_target.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.lbl_target = ttk.Label(frame_top, text="Default: [Base]__patch", foreground="gray")
        self.lbl_target.grid(row=1, column=1, sticky="w", padx=5)

        # --- Middle Section: Tree View ---
        frame_mid = ttk.Frame(root)
        frame_mid.pack(expand=True, fill="both", padx=10, pady=5)

        self.tree_scroll = ttk.Scrollbar(frame_mid)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(frame_mid, selectmode="browse", yscrollcommand=self.tree_scroll.set)
        self.tree.heading("#0", text="File System", anchor="w")
        self.tree.pack(expand=True, fill="both")
        
        self.tree_scroll.config(command=self.tree.yview)

        # --- Bottom Section: Actions ---
        frame_bot = ttk.Frame(root, padding=10)
        frame_bot.pack(fill="x")

        self.btn_copy = ttk.Button(frame_bot, text="Copy Selected", command=self.action_copy, state="disabled")
        self.btn_copy.pack(side="left", padx=5)

        self.btn_move = ttk.Button(frame_bot, text="Move Selected", command=self.action_move, state="disabled")
        self.btn_move.pack(side="left", padx=5)

        self.lbl_status = ttk.Label(frame_bot, text="Ready", relief="sunken", anchor="w")
        self.lbl_status.pack(side="right", fill="x", expand=True, padx=10)

    def select_base(self):
        path = filedialog.askdirectory(title="Select Base Directory")
        if path:
            self.base_path = path
            self.lbl_base.config(text=path, foreground="black")
            self.init_manager()
            self.refresh_tree()
            self.btn_copy.config(state="normal")
            self.btn_move.config(state="normal")

    def select_target(self):
        path = filedialog.askdirectory(title="Select Target Directory")
        if path:
            self.target_path = path
            self.lbl_target.config(text=path, foreground="black")
            self.init_manager() # Re-init to update target
        else:
            # If user cancels or clears, reset to None (default logic)
            self.target_path = None
            self.lbl_target.config(text="Default: [Base]__patch", foreground="gray")
            self.init_manager()

    def init_manager(self):
        if self.base_path:
            try:
                self.dir_manager = Directory(self.base_path, self.target_path)
                target_disp = self.dir_manager.base_patch
                self.lbl_status.config(text=f"Target set to: {target_disp}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def refresh_tree(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.base_path:
            return

        # Populate tree
        root_node = self.tree.insert("", "end", text=self.base_path, open=True, values=[self.base_path])
        self.process_directory(root_node, self.base_path)

    def process_directory(self, parent, path):
        try:
            # Sort: Directories first, then files
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                abspath = os.path.abspath(entry.path)
                # We store the full path in the 'data' (values) so we can retrieve it later
                # We add a dummy 'folder' icon visually using text if needed, or just rely on structure
                display_text = f"📁 {entry.name}" if entry.is_dir() else f"📄 {entry.name}"
                
                oid = self.tree.insert(parent, "end", text=display_text, values=[abspath])
                
                if entry.is_dir():
                    # Recursive call
                    self.process_directory(oid, entry.path)
        except PermissionError:
            pass 

    def get_selected_path(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a file or folder first.")
            return None
        
        # Value[0] contains the absolute path we stored
        full_path = self.tree.item(selected_item[0])['values'][0]
        
        # Edge case: If they selected the root folder itself
        if Path(full_path) == Path(self.base_path):
             messagebox.showwarning("Warning", "Cannot move/copy the entire base root itself.")
             return None
             
        return full_path

    def action_copy(self):
        path = self.get_selected_path()
        if path:
            try:
                dst = self.dir_manager.copy_item(path)
                self.lbl_status.config(text=f"Copied to: {dst}")
                messagebox.showinfo("Success", "Item Copied Successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy: {e}")

    def action_move(self):
        path = self.get_selected_path()
        if path:
            # if messagebox.askyesno("Confirm Move", "This will delete the original file/folder. Proceed?"):
            try:
                dst = self.dir_manager.move_item(path)
                self.lbl_status.config(text=f"Moved to: {dst}")
                self.refresh_tree() # MUST refresh because file is gone
                messagebox.showinfo("Success", "Item Moved Successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Optional: styling
    style = ttk.Style()
    style.theme_use('clam') 
    app = DirectoryApp(root)
    root.mainloop()