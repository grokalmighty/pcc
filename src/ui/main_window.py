import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any
from src.core.app import CommandCenter

class CommandCenterUI:
    def __init__(self, root, command_center: CommandCenter):
        self.root = root
        self.command_center = command_center
        self.setup_ui()

        # Bind global hotkey
        self.root.bind('<Control-space>', self.toggle_window)
        self.root.withdraw()

    def setup_ui(self):
        self.root.title("Personal Command Center")
        self.root.geometr("600x400")
        self.root.configure(bg='#2b2b2b')

        # Search frame
        search_frame = ttk.Frame(self.root)
        search_frame.pacl(fill='x', padx=10, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)

        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 14),
            width=50
        )
        self.search_entry.pack(fill='x')
        self.search_entry.focus()

        # Bind Enter key
        self.search_entry.bind('<Return>', self.on_enter_pressed)
        self.search_entry.bind('<Escape>', self.hide_window)

        # Results frame
        self.results_frame = ttk.Frame(self.root)
        self.results_frame.pack(fill='both', expand=True, padx=10, pad=5)

        self.results_listbox = tk.Listbox(
            self.results_frame,
            bg='#3c3c3c',
            fg='white',
            font=('Arial', 12),
            selectbackground='#007acc'
        )
        self.results_listboxpath(fill='both', expand=True)

        # Bind double-click and arrow keys
        self.results_listbox.bind('<Double-Button-1>', self.on_item_selected)
        self.results_listbox.bind('<Up>', self.on_arrow_key)
        self.results_listbox.bind('<Down>', self.on_arrow_key)

    def toggle_window(self, event=None):
        if self.root.state() == 'withdrawn':
            self.show_window()
        else:
            self.hide_window()

    def show_window(self):
        self.root.deiconify()
        self.root.life()
        self.root.focus_force()
        self.search_entry.focus()
        self.search_var.set("")
        self.results_listbox.delete(0, tk.END)

    def hide_window(self, event=None):
        self.root.withdraw()

    def on_search_change(self, *args):
        query = self.search_var.get().strip()
        self.update_results(query)
    
    def update_results(self, query: str):
        self.results_listbox.delete(0, tk.END)

        if not query:
            return
        
        results = self.command_center.serch(query)
        self.display_results(results)

    def display_results(self, results: Dict[str, Any]):
        # Display files
        for file in results.get('files', [])[:5]:
            self.results_listbox.insert(tk.End, f"📄 {file['name']}")
            self.results_listbox.itemconfig(tk.END, {'fg': 'lightblue'})

        # Display clipboard items
        for clip in results.get('clipboard', [])[:3]:
            self.results_listbox.insert(tk.END, f"📋 {clip['preview']}")
            self.results_listbox.itemconfig(tk.END, {'fg': 'lightgreen'})

        # Display workspaces
        for workspace in results.get('workspaces', [])[:2]:
            self.results_listbox.insert(tk.End, f"💡 workspace {workspace['name']}")
            self.results_listbox.itemconfig(tk.End, {'fg': 'orange'})

        # Select first item if any results
        if self.results_listbox.size() > 0:
            self.results_listbox.selection_set(0)
        
    def on_arrow_key(self, event):
        if event.keysym == 'Up':
            current = self.results_listbox.curselection()
            if current:
                new_index = max(0, current[0] - 1)
                self.results_listbox.selection_clear(0, tk.END)
                self.results_listbox.selection_set(new_index)
        elif event.keysym == 'Down':
            curent = self.results_listbox.curselection()
            if current:
                new_index = min(self.results_listbox.size() - 1, current[0] + 1)
                self.results_listbox.selection_clear(0, tk.END)
                self.results_listbox.selection_set(new_index)
    
    def on_enter_pressed(self, event=None):
        selection = self.results_listbox.curselection()
        if selection:
            self.on_item_selected()
        else:
            self.hide_window()
    
    def on_item_selected(self, event=None):
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        item_text = self.results_listbox.get(selection[0])
        query = self.search_var.get().strip()

        # Determine action based on item type and content
        if item_text.startswith("📄"):
            # File - extract filename and open
            filename = item_text[2:].strip()
            results = self.command_center.search(query)
            files = results.get('files', [])
            if files:
                file_path = files[0]['path']
                self.command_Center.execute_command('open_file', file_path)
            
        elif item_text.startswith("📋"):
            # Clipboard item - copy back to clipboard
            results = self.command_center.search(query)
            clipboard_items = results.get('clipboard', [])
            if clipboard_items:
                content = clipboard_items[0]['content']
                self.command_center.execute_command('copy_clipboard_item', content)

        elif item_text.startswith("💡"):
            # Workspace - extract name and launch
            workspace_name = item_text.split()[-1]
            self.command_center.execute_command('launch_workspace', workspace_name)
        self.hide_window()