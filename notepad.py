import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk


def update_tab_title(tab_data):
    title = tab_data["title"]
    if tab_data["modified"]:
        title += " *"
    tab_data["tab_title"].config(text=title)


class ModernNotepad:
    def __init__(self, root):
        self.status_label = None
        self.status_bar = None
        self.notebook = None
        self.tab_bar = None
        self.drag_area = None
        self.title_bar = None
        self.style = None
        self.new_tab_btn = None
        self.root = root
        self.root.title("Modern Notepad")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        try:
            self.root.iconbitmap('icon.ico')
        except Exception as e:
            print(f"Error loading icon: {e}")
        self.root.overrideredirect(True)

        # Modern color scheme
        self.bg_color = "#252526"
        self.title_bar_color = "#333333"
        self.text_bg = "#1e1e1e"
        self.fg_color = "#e8e8e8"
        self.accent_color = "#007acc"
        self.tab_bg = "#2d2d2d"
        self.scroll_color = "#454545"
        self.close_hover = "#e81123"
        self.button_hover = "#404040"
        self.new_tab_color = "#333333"
        self.tab_border = "#3c3c3c"
        self.selected_tab_color = "#37373d"

        self.is_maximized = False
        self.prev_geometry = ""
        self.x = 0
        self.y = 0
        self.tabs = []
        self.current_tab = None

        try:
            self.app_icon = ImageTk.PhotoImage(Image.open('icon.ico').resize((20, 20)))
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.app_icon = None

        self.configure_styles()
        self.create_widgets()
        self.bind_shortcuts()
        self.create_first_tab()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Completely hide native notebook tabs
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0, padding=0)
        self.style.configure("TNotebook.Tab", background=self.bg_color, borderwidth=0, padding=0, width=0)
        self.style.layout("TNotebook.Tab", [])

        # Scrollbar styling
        self.style.configure("Modern.Vertical.TScrollbar",
                             gripcount=0,
                             width=12,
                             arrowsize=0,
                             troughcolor=self.bg_color,
                             bordercolor=self.bg_color,
                             relief="flat",
                             darkcolor=self.scroll_color,
                             lightcolor=self.scroll_color)
        self.style.map("Modern.Vertical.TScrollbar",
                       darkcolor=[("active", "#606060")],
                       lightcolor=[("active", "#606060")])

    def create_widgets(self):
        # Title Bar
        self.title_bar = tk.Frame(self.root, bg=self.title_bar_color, height=40)
        self.title_bar.pack(fill='x', side='top')

        # Drag Area
        self.drag_area = tk.Frame(self.title_bar, bg=self.title_bar_color)
        self.drag_area.pack(side='left', expand=True, fill='both')

        if self.app_icon:
            icon_label = tk.Label(self.drag_area, image=self.app_icon, bg=self.title_bar_color)
            icon_label.pack(side='left', padx=(10, 5))

        title_label = tk.Label(self.drag_area, text="Modern Notepad", bg=self.title_bar_color,
                               fg=self.fg_color, font=("Segoe UI Semibold", 10))
        title_label.pack(side='left')

        # Window Controls
        control_frame = tk.Frame(self.title_bar, bg=self.title_bar_color)
        control_frame.pack(side='right', padx=0)

        # Control Buttons
        controls = [
            ("─", self.root.iconify, 14, "min_btn"),
            ("◻", self.toggle_maximize, 12, "max_btn"),
            ("✕", self.root.destroy, 14, "close_btn")
        ]

        for text, cmd, font_size, name in controls:
            btn = tk.Label(control_frame, text=text, bg=self.title_bar_color, fg=self.fg_color,
                           font=("Segoe UI", font_size), cursor="hand2", padx=12, pady=2)
            btn.pack(side='left')
            if name == "close_btn":
                btn.bind("<Enter>", lambda e: e.widget.config(bg=self.close_hover, fg="white"))
                btn.bind("<Leave>", lambda e: e.widget.config(bg=self.title_bar_color, fg=self.fg_color))
            else:
                btn.bind("<Enter>", lambda e: e.widget.config(bg=self.button_hover))
                btn.bind("<Leave>", lambda e: e.widget.config(bg=self.title_bar_color))
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            setattr(self, name, btn)

        # Drag Functionality
        self.drag_area.bind("<ButtonPress-1>", self.start_move)
        self.drag_area.bind("<B1-Motion>", self.on_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)

        # Action Buttons
        btn_frame = tk.Frame(self.title_bar, bg=self.title_bar_color)
        btn_frame.pack(side='left', padx=15)

        actions = [
            ("New", self.new_tab),
            ("Open", self.open_file),
            ("Save", self.save_file)
        ]

        for text, cmd in actions:
            btn = tk.Label(btn_frame, text=text, bg=self.title_bar_color, fg=self.fg_color,
                           font=("Segoe UI", 10), cursor="hand2", padx=10)
            btn.pack(side='left')
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.button_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.title_bar_color))

        # Custom Tab Bar
        self.tab_bar = tk.Frame(self.root, bg=self.bg_color)
        self.tab_bar.pack(fill='x', side='top')

        # Notebook (hidden native tabs)
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill='both', expand=True, padx=0, pady=0)

        # New Tab Button
        self.new_tab_btn = tk.Label(self.tab_bar, text="+", bg=self.tab_bg, fg=self.fg_color,
                                    font=("Segoe UI", 14), padx=15, cursor="hand2")
        self.new_tab_btn.pack(side='left', padx=(0, 5))
        self.new_tab_btn.bind("<Button-1>", lambda e: self.new_tab())
        self.new_tab_btn.bind("<Enter>", lambda e: e.widget.config(bg=self.button_hover))
        self.new_tab_btn.bind("<Leave>", lambda e: e.widget.config(bg=self.tab_bg))

        # Status Bar
        self.status_bar = tk.Frame(self.root, bg=self.bg_color, height=24)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_label = tk.Label(self.status_bar, text="Ready", bg=self.bg_color, fg=self.fg_color,
                                     font=("Segoe UI", 9))
        self.status_label.pack(side='left', padx=15)

    def create_first_tab(self):
        self.new_tab()

    def new_tab(self, content="", title="Untitled", file_path=None):
        tab_frame = tk.Frame(self.notebook, bg=self.bg_color)
        text_area = ScrolledText(tab_frame, wrap=tk.WORD, bg=self.text_bg, fg=self.fg_color,
                                 insertbackground=self.fg_color, font=("Cascadia Code", 12),
                                 padx=15, pady=15, highlightthickness=0, insertwidth=2,
                                 selectbackground=self.accent_color, yscrollcommand=lambda *args: self.update_status())
        text_area.pack(fill='both', expand=True)
        text_area.insert("1.0", content)
        text_area.bind("<<Modified>>", self.on_text_modified)
        text_area.bind("<Button-3>", self.show_context_menu)
        text_area.bind("<KeyRelease>", self.update_status)
        text_area.bind("<ButtonRelease>", self.update_status)

        # Tab Button Container
        tab_btn_frame = tk.Frame(self.tab_bar, bg=self.tab_bg, padx=0, pady=0)
        tab_btn_frame.pack(side='left', before=self.new_tab_btn)

        # Tab Title
        tab_title = tk.Label(tab_btn_frame, text=title, bg=self.tab_bg, fg=self.fg_color,
                             font=("Segoe UI", 10), padx=0, pady=5, cursor="hand2")
        tab_title.pack(side='left')

        # Close Button
        close_btn = tk.Label(tab_btn_frame, text="×", bg=self.tab_bg, fg=self.fg_color,
                             font=("Segoe UI", 12), padx=8, pady=0, cursor="hand2")
        close_btn.pack(side='left')

        # Bindings
        tab_btn_frame.bind("<Button-1>", lambda e: self.select_tab(tab_frame))
        tab_title.bind("<Button-1>", lambda e: self.select_tab(tab_frame))
        close_btn.bind("<Button-1>", lambda e: self.close_tab(tab_frame))
        close_btn.bind("<Enter>", lambda e: e.widget.config(bg=self.close_hover, fg="white"))
        close_btn.bind("<Leave>", lambda e: e.widget.config(bg=tab_btn_frame.cget("bg"), fg=self.fg_color))

        self.notebook.add(tab_frame, text=title)
        self.notebook.hide(tab_frame)

        tab_data = {
            "text_area": text_area,
            "file_path": file_path,
            "modified": False,
            "title": title,
            "tab_btn_frame": tab_btn_frame,
            "tab_title": tab_title,
            "close_btn": close_btn
        }
        tab_frame.tab_data = tab_data
        self.tabs.append(tab_frame)
        self.select_tab(tab_frame)
        return tab_frame

    def select_tab(self, tab):
        for t in self.tabs:
            tab_data = t.tab_data
            if t == tab:
                # Selected tab styling
                tab_data["tab_btn_frame"].config(bg=self.selected_tab_color)
                tab_data["tab_title"].config(bg=self.selected_tab_color)
                tab_data["close_btn"].config(bg=self.selected_tab_color)
                self.notebook.select(t)
            else:
                # Unselected tab styling
                tab_data["tab_btn_frame"].config(bg=self.tab_bg)
                tab_data["tab_title"].config(bg=self.tab_bg)
                tab_data["close_btn"].config(bg=self.tab_bg)
        self.current_tab = tab
        self.update_status()

    def close_tab(self, tab):
        if isinstance(tab, str):
            tab = self.notebook.nametowidget(tab)
        if len(self.tabs) == 1:
            self.root.destroy()
            return

        tab_data = tab.tab_data
        content = tab_data["text_area"].get("1.0", "end-1c")

        if tab_data["modified"] and content.strip():
            if not self.confirm_unsaved_changes(tab):
                return

        self.tabs.remove(tab)
        tab_data["tab_btn_frame"].destroy()
        self.notebook.forget(tab)
        if self.tabs:
            self.select_tab(self.tabs[-1])
        else:
            self.root.destroy()

    def get_current_tab_data(self):
        return self.current_tab.tab_data if self.current_tab else None

    def update_status(self, event=None):
        current_tab = self.get_current_tab_data()
        if current_tab:
            text_area = current_tab["text_area"]
            line, column = text_area.index(tk.INSERT).split('.')
            self.status_label.config(text=f"Line {line}, Column {column} • UTF-8")

    def on_text_modified(self, event):
        current_tab = self.get_current_tab_data()
        if current_tab:
            current_tab["modified"] = True
            event.widget.edit_modified(False)
            update_tab_title(current_tab)

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
                update_tab_title(tab.tab_data)
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
                update_tab_title(tab_data)
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
            update_tab_title(tab_data)

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0, bg=self.accent_color, fg=self.fg_color)
        context_menu.add_command(label="Cut", command=self.cut_text)
        context_menu.add_command(label="Copy", command=self.copy_text)
        context_menu.add_command(label="Paste", command=self.paste_text)
        context_menu.tk_popup(event.x_root, event.y_root)

    def bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_tab())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-w>", lambda e: self.close_tab(self.current_tab))
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

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_maximize(self):
        if self.is_maximized:
            self.root.geometry(self.prev_geometry)
            self.max_btn.config(text="◻")
        else:
            self.prev_geometry = self.root.geometry()
            self.root.state('zoomed')
            self.max_btn.config(text="🗖")
        self.is_maximized = not self.is_maximized


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernNotepad(root)
    root.mainloop()