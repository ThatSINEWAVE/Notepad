import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class ModernNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Notepad")
        self.root.geometry("1000x700")
        self.style = ttk.Style()

        # Configure dark theme colors
        self.bg_color = "#2d2d2d"
        self.text_bg = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#3e3e3e"
        self.tab_bg = "#252526"
        self.scroll_color = "#5a5a5a"

        self.configure_styles()
        self.create_widgets()
        self.bind_shortcuts()
        self.create_first_tab()

    def configure_styles(self):
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab",
                             background=self.tab_bg,
                             foreground=self.fg_color,
                             padding=[10, 4],
                             borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.accent_color)],
                       expand=[("selected", [1, 1, 1, 0])])

        self.style.configure("Custom.Vertical.TScrollbar",
                             gripcount=0,
                             background=self.scroll_color,
                             troughcolor=self.bg_color,
                             bordercolor=self.bg_color,
                             arrowcolor=self.fg_color,
                             lightcolor=self.bg_color,
                             darkcolor=self.bg_color)

        self.style.configure("Custom.Horizontal.TScrollbar",
                             gripcount=0,
                             background=self.scroll_color,
                             troughcolor=self.bg_color,
                             bordercolor=self.bg_color,
                             arrowcolor=self.fg_color,
                             lightcolor=self.bg_color,
                             darkcolor=self.bg_color)

    def create_widgets(self):
        # Custom title bar
        self.title_bar = tk.Frame(self.root, bg=self.accent_color, height=40)
        self.title_bar.pack(fill='x', side='top')

        # Title bar buttons
        self.btn_frame = tk.Frame(self.title_bar, bg=self.accent_color)
        self.btn_frame.pack(side='left', padx=10)

        buttons = [
            ("New", self.new_tab),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("+", self.new_tab)
        ]

        for text, cmd in buttons[:-1]:
            btn = tk.Button(self.btn_frame, text=text, command=cmd,
                            bg=self.accent_color, fg=self.fg_color,
                            activebackground=self.fg_color,
                            activeforeground=self.accent_color,
                            borderwidth=0, padx=10)
            btn.pack(side='left')

        # New tab button on right
        new_tab_btn = tk.Button(self.title_bar, text=buttons[-1][0], command=buttons[-1][1],
                                bg=self.accent_color, fg=self.fg_color,
                                activebackground=self.fg_color,
                                activeforeground=self.accent_color,
                                borderwidth=0, font=("Arial", 14))
        new_tab_btn.pack(side='right', padx=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill='both', expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def create_first_tab(self):
        self.new_tab()

    def new_tab(self, content="", title="Untitled", file_path=None):
        tab_frame = tk.Frame(self.notebook, bg=self.bg_color)

        # Text area with custom scrollbars
        text_area = ScrolledText(tab_frame,
                                 wrap=tk.WORD,
                                 bg=self.text_bg,
                                 fg=self.fg_color,
                                 insertbackground=self.fg_color,
                                 font=("Segoe UI", 12),
                                 padx=10,
                                 pady=10)
        text_area.pack(fill='both', expand=True)

        text_area.bind("<<Modified>>", self.on_text_modified)
        text_area.bind("<Button-3>", self.show_context_menu)

        # Tab header with close button
        tab_header = tk.Frame(self.notebook, bg=self.tab_bg)
        close_btn = tk.Label(tab_header, text="×",
                             bg=self.tab_bg, fg=self.fg_color,
                             font=("Arial", 14), cursor="hand2")
        close_btn.pack(side='right', padx=(0, 5))
        tk.Label(tab_header, text=title, bg=self.tab_bg, fg=self.fg_color).pack(side='left')

        close_btn.bind("<Button-1>", lambda e: self.close_tab(tab_frame))

        self.notebook.add(tab_frame, text=title, sticky='nsew')
        self.notebook.select(tab_frame)

        # Store tab data
        tab_data = {
            "text_area": text_area,
            "file_path": file_path,
            "modified": False,
            "title": title,
            "tab_header": tab_header
        }
        tab_frame.tab_data = tab_data

        return tab_frame

    def get_current_tab_data(self):
        current_tab = self.notebook.select()
        if not current_tab:
            return None
        return self.notebook.nametowidget(current_tab).tab_data

    def on_text_modified(self, event):
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab["modified"] = True
            event.widget.edit_modified(False)

    def on_tab_changed(self, event):
        current_tab = self.get_current_tab_data()
        if current_tab:
            title = current_tab["title"]
            if current_tab["modified"]:
                title += " *"
            self.root.title(f"{title} - Modern Notepad")

    def close_tab(self, tab):
        if self.notebook.index("end") <= 1:
            self.root.destroy()
            return

        tab_data = tab.tab_data
        content = tab_data["text_area"].get("1.0", "end-1c")

        if tab_data["modified"] and content.strip():
            if not self.confirm_unsaved_changes(tab):
                return

        self.notebook.forget(tab)

    def confirm_unsaved_changes(self, tab):
        response = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Do you want to save changes before closing this tab?"
        )
        if response is None:
            return False
        if response:
            self.save_file(tab)
        return True

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                tab = self.new_tab(content=content, title=file_path.split("/")[-1], file_path=file_path)
                tab.tab_data["modified"] = False
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self, tab=None):
        tab_data = tab.tab_data if tab else self.get_current_tab_data()
        if not tab_data:
            return

        if tab_data["file_path"]:
            try:
                content = tab_data["text_area"].get("1.0", tk.END)
                with open(tab_data["file_path"], 'w', encoding='utf-8') as file:
                    file.write(content)
                tab_data["modified"] = False
                self.update_tab_title(tab_data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        else:
            self.save_as_file(tab_data)

    def save_as_file(self, tab_data=None):
        tab_data = tab_data or self.get_current_tab_data()
        if not tab_data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            tab_data["file_path"] = file_path
            tab_data["title"] = file_path.split("/")[-1]
            self.save_file(tab_data)
            self.update_tab_title(tab_data)

    def update_tab_title(self, tab_data):
        tab_data["tab_header"].children["!label"].config(text=tab_data["title"])
        self.on_tab_changed(None)

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0,
                               bg=self.accent_color, fg=self.fg_color)
        context_menu.add_command(label="Cut", command=self.cut_text)
        context_menu.add_command(label="Copy", command=self.copy_text)
        context_menu.add_command(label="Paste", command=self.paste_text)
        context_menu.tk_popup(event.x_root, event.y_root)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_tab())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-w>", lambda e: self.close_tab(self.notebook.select()))
        self.root.bind("<Control-t>", lambda e: self.new_tab())

        text_commands = {
            "<Control-x>": self.cut_text,
            "<Control-c>": self.copy_text,
            "<Control-v>": self.paste_text,
            "<Control-a>": self.select_all
        }

        for key, cmd in text_commands.items():
            self.root.bind(key, lambda e, c=cmd: c())

    def cut_text(self):
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab["text_area"].event_generate("<<Cut>>")

    def copy_text(self):
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab["text_area"].event_generate("<<Copy>>")

    def paste_text(self):
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab["text_area"].event_generate("<<Paste>>")

    def select_all(self):
        current_tab = self.get_current_tab_data()
        if current_tab:
            text_area = current_tab["text_area"]
            text_area.tag_add(tk.SEL, "1.0", tk.END)
            text_area.mark_set(tk.INSERT, "1.0")
            text_area.see(tk.INSERT)
            return "break"


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernNotepad(root)
    root.mainloop()