#!/usr/bin/env python3
"""Downloads Galaxy desktop prototype using Tkinter."""

import argparse
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from downloads_core import scan_path


class DownloadsDesktopApp:
    def __init__(self, root, initial_path: Path):
        self.root = root
        self.scan_path = initial_path
        self.scan_data = {}
        self.selected_folder_files = []

        self.root.title("Downloads Galaxy (Desktop Prototype)")
        self.root.geometry("1100x700")
        self.root.configure(bg="#0a0f1f")

        self._build_styles()
        self._build_layout()
        self.reindex()

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Galaxy.TFrame", background="#0a0f1f")
        style.configure("Galaxy.TLabelframe", background="#0a0f1f", foreground="#9cd1ff")
        style.configure("Galaxy.TLabelframe.Label", background="#0a0f1f", foreground="#9cd1ff")
        style.configure("Galaxy.TLabel", background="#0a0f1f", foreground="#dbeaff")
        style.configure("Galaxy.TButton", background="#1f3a6b", foreground="#ffffff")

    def _build_layout(self):
        container = ttk.Frame(self.root, style="Galaxy.TFrame", padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(container, style="Galaxy.TFrame")
        controls.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(controls, text="Indexed folder:", style="Galaxy.TLabel").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=str(self.scan_path))
        path_entry = ttk.Entry(controls, textvariable=self.path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)

        ttk.Button(controls, text="Choose Folder", command=self.choose_folder, style="Galaxy.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(controls, text="Reindex", command=self.reindex, style="Galaxy.TButton").pack(side=tk.LEFT)

        self.stats_var = tk.StringVar(value="Ready")
        ttk.Label(container, textvariable=self.stats_var, style="Galaxy.TLabel").pack(fill=tk.X, pady=(0, 10))

        content = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Labelframe(content, text="Constellations (Folders)", style="Galaxy.TLabelframe", padding=8)
        right = ttk.Labelframe(content, text="Celestial Bodies (Files)", style="Galaxy.TLabelframe", padding=8)
        content.add(left, weight=1)
        content.add(right, weight=3)

        self.folder_list = tk.Listbox(left, bg="#101a33", fg="#dbeaff", selectbackground="#335aa6", borderwidth=0)
        self.folder_list.pack(fill=tk.BOTH, expand=True)
        self.folder_list.bind("<<ListboxSelect>>", self.on_folder_selected)

        columns = ("name", "type", "size", "modified")
        self.file_table = ttk.Treeview(right, columns=columns, show="headings")
        self.file_table.heading("name", text="File")
        self.file_table.heading("type", text="Type")
        self.file_table.heading("size", text="Size")
        self.file_table.heading("modified", text="Modified")

        self.file_table.column("name", width=450)
        self.file_table.column("type", width=120, anchor=tk.CENTER)
        self.file_table.column("size", width=110, anchor=tk.E)
        self.file_table.column("modified", width=190, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.file_table.yview)
        self.file_table.configure(yscrollcommand=scrollbar.set)

        self.file_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def choose_folder(self):
        chosen = filedialog.askdirectory(initialdir=str(self.scan_path))
        if chosen:
            self.scan_path = Path(chosen).expanduser().resolve()
            self.path_var.set(str(self.scan_path))
            self.reindex()

    def reindex(self):
        try:
            candidate = Path(self.path_var.get()).expanduser().resolve()
            if not candidate.exists() or not candidate.is_dir():
                messagebox.showerror("Invalid folder", f"Path is not a folder:\n{candidate}")
                return

            self.scan_path = candidate
            self.scan_data = scan_path(self.scan_path)
            self.populate_folders()
            self.update_stats()
        except Exception as exc:
            messagebox.showerror("Scan failed", str(exc))

    def populate_folders(self):
        self.folder_list.delete(0, tk.END)
        for folder in self.scan_data.get("folders", []):
            label = f"{folder['icon']} {folder['name']} ({folder['total_size_formatted']})"
            self.folder_list.insert(tk.END, label)

        self.selected_folder_files = []
        for row in self.file_table.get_children():
            self.file_table.delete(row)

        if self.scan_data.get("folders"):
            self.folder_list.selection_set(0)
            self.on_folder_selected()

    def on_folder_selected(self, _event=None):
        selection = self.folder_list.curselection()
        if not selection:
            return

        idx = selection[0]
        folder = self.scan_data["folders"][idx]

        for row in self.file_table.get_children():
            self.file_table.delete(row)

        for f in folder.get("files", []):
            modified = f.get("modified", "")
            if modified:
                modified = datetime.fromisoformat(modified).strftime("%Y-%m-%d %H:%M")
            self.file_table.insert(
                "",
                tk.END,
                values=(
                    f"{f['icon']} {f['name']}",
                    f.get("type", "other"),
                    f.get("size", ""),
                    modified,
                ),
            )

    def update_stats(self):
        stats = self.scan_data.get("stats", {})
        stamp = self.scan_data.get("scanned_at", "")
        scanned_at = datetime.fromisoformat(stamp).strftime("%Y-%m-%d %H:%M:%S") if stamp else "-"
        self.stats_var.set(
            f"{stats.get('total_files', 0)} files • "
            f"{stats.get('categories', 0)} constellations • "
            f"{stats.get('total_size_formatted', '0 B')} total • "
            f"Scanned at {scanned_at}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Downloads Galaxy desktop prototype")
    parser.add_argument(
        "folder",
        nargs="?",
        default=str(Path.home() / "Downloads"),
        help="Folder to index (default: ~/Downloads)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    initial = Path(args.folder).expanduser().resolve()

    root = tk.Tk()
    app = DownloadsDesktopApp(root, initial)
    root.mainloop()
