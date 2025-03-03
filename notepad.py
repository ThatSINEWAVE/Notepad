import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import os
import re
import sys
import json
import shutil
from datetime import datetime


def update_tab_title(tab_data):
    """Update the tab title to show modified status"""
    title = tab_data["title"]
    if tab_data["modified"]:
        title += " *"
    tab_data["tab_title"].config(text=title)


class EnhancedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Notepad")
        self.root.geometry("1200x800")

        # Load user settings or use defaults
        self.settings = self.load_settings()

        # Modern color schemes
        self.color_schemes = {
            "dark": {
                "bg_color": "#252526",
                "title_bar_color": "#333333",
                "text_bg": "#1e1e1e",
                "fg_color": "#e8e8e8",
                "accent_color": "#007acc",
                "tab_bg": "#2d2d2d",
                "scroll_color": "#454545",
                "close_hover": "#e81123",
                "button_hover": "#404040",
                "new_tab_color": "#333333",
                "tab_border": "#3c3c3c",
                "selected_tab_color": "#37373d",
                "line_highlight": "#2a2d2e",
                "line_number_bg": "#1e1e1e",
                "line_number_fg": "#858585",
                "status_bar_color": "#007acc",
                "menu_hover": "#505050",
            },
            "light": {
                "bg_color": "#f5f5f5",
                "title_bar_color": "#e1e1e1",
                "text_bg": "#ffffff",
                "fg_color": "#333333",
                "accent_color": "#0078d7",
                "tab_bg": "#e1e1e1",
                "scroll_color": "#c1c1c1",
                "close_hover": "#e81123",
                "button_hover": "#d1d1d1",
                "new_tab_color": "#e1e1e1",
                "tab_border": "#cccccc",
                "selected_tab_color": "#ffffff",
                "line_highlight": "#f0f0f0",
                "line_number_bg": "#f0f0f0",
                "line_number_fg": "#767676",
                "status_bar_color": "#0078d7",
                "menu_hover": "#e5e5e5",
            },
        }

        # Set current theme from settings
        self.current_theme = self.settings.get("theme", "dark")
        self.colors = self.color_schemes[self.current_theme]

        # UI initialization
        self.root.configure(bg=self.colors["bg_color"])
        self.root.overrideredirect(True)

        # Track window state
        self.is_maximized = False
        self.prev_geometry = ""
        self.x = 0
        self.y = 0

        # Initialize UI elements
        self.search_frame = None
        self.search_entry = None
        self.replace_entry = None
        self.status_label = None
        self.status_bar = None
        self.notebook = None
        self.tab_bar = None
        self.drag_area = None
        self.title_bar = None
        self.style = None
        self.new_tab_btn = None

        # Initialize available fonts
        self.available_fonts = self.get_monospace_fonts()
        self.current_font = self.settings.get("font", "Consolas")
        self.current_font_size = self.settings.get("font_size", 12)
        self.tab_size = self.settings.get("tab_size", 4)
        self.show_line_numbers = self.settings.get("show_line_numbers", True)

        # Tab management
        self.tabs = []
        self.current_tab = None
        self.last_saved_count = {}

        # Try to load app icon
        try:
            icon_path = self.get_resource_path("icon.ico")
            self.app_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((20, 20)))
            self.root.iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.app_icon = None

        # Initialize the UI
        self.configure_styles()
        self.create_widgets()
        self.bind_shortcuts()
        self.create_first_tab()

        # Auto-save timer (every 2 minutes)
        if self.settings.get("auto_save", True):
            self.root.after(120000, self.auto_save)

    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_settings(self):
        """Load user settings from config file"""
        default_settings = {
            "theme": "dark",
            "font": "Consolas",
            "font_size": 12,
            "auto_save": True,
            "word_wrap": True,
            "tab_size": 4,
            "show_line_numbers": True,
            "recent_files": [],
            "auto_indent": True,
            "highlight_current_line": True,
            "custom_settings_path": None  # New setting for custom location
        }

        try:
            # First check default location
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            default_path = os.path.join(base_path, "settings.json")

            if os.path.exists(default_path):
                with open(default_path, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    settings = {**default_settings, **loaded}

                    # Check if custom path exists
                    if settings["custom_settings_path"] and os.path.exists(settings["custom_settings_path"]):
                        custom_path = os.path.join(settings["custom_settings_path"], "settings.json")
                        if os.path.exists(custom_path):
                            with open(custom_path, "r") as cf:
                                custom_settings = json.load(cf)
                                settings.update(custom_settings)
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")

        return default_settings

    def save_settings(self):
        """Save user settings to config file"""
        try:
            # Create a safe copy of settings without Tkinter objects
            saveable_settings = {
                "theme": self.current_theme,
                "font": self.current_font,
                "font_size": self.current_font_size,
                "tab_size": self.tab_size,
                "word_wrap": self.settings.get("word_wrap", True),
                "show_line_numbers": self.show_line_numbers,
                "recent_files": self.get_recent_files(),
                "highlight_current_line": self.settings.get("highlight_current_line", True),
                "custom_settings_path": self.settings.get("custom_settings_path")
            }

            # Determine save path
            if self.settings.get("custom_settings_path"):
                save_dir = self.settings["custom_settings_path"]
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                save_path = os.path.join(save_dir, "settings.json")
            else:
                if getattr(sys, 'frozen', False):
                    save_dir = os.path.dirname(sys.executable)
                else:
                    save_dir = os.path.dirname(os.path.abspath(__file__))
                save_path = os.path.join(save_dir, "settings.json")

            # Save to determined path
            with open(save_path, "w") as f:
                json.dump(saveable_settings, f, indent=4)

        except Exception as e:
            print(f"Error saving settings: {e}")

    def choose_settings_location(self):
        """Let user choose where to store settings"""
        path = filedialog.askdirectory(
            title="Select Settings Directory",
            initialdir=os.path.expanduser("~")
        )
        if path:
            try:
                # Save new location to default settings
                self.settings["custom_settings_path"] = path
                default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
                with open(default_path, "w") as f:
                    json.dump({"custom_settings_path": path}, f)

                # Migrate existing settings
                if os.path.exists(default_path):
                    shutil.copy(default_path, os.path.join(path, "settings.json"))

                messagebox.showinfo(
                    "Settings Location",
                    f"Settings will now be stored in:\n{path}\nRestart the application to apply changes."
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not change settings location: {str(e)}")

    def get_settings_path(self):
        """Determine correct settings path"""
        if "custom_settings_path" in self.settings:
            custom_path = os.path.join(self.settings["custom_settings_path"], "settings.json")
            if os.path.exists(os.path.dirname(custom_path)):
                return custom_path
        # Fallback to default location
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), "settings.json")
        return os.path.join(os.path.dirname(__file__), "settings.json")

    def get_recent_files(self):
        """Get list of recent files from open tabs"""
        recent_files = []
        for tab in self.tabs:
            if tab["file_path"]:  # Changed from tab.tab_data["file_path"]
                recent_files.append(tab["file_path"])

        # Add existing recent files that aren't currently open
        for file_path in self.settings.get("recent_files", []):
            if file_path not in recent_files and os.path.exists(file_path):
                recent_files.append(file_path)

        # Limit to last 10 files
        return recent_files[-10:]

    def get_monospace_fonts(self):
        """Get a list of available monospace fonts"""
        monospace_fonts = [
            "Consolas",
            "Cascadia Code",
            "Courier New",
            "Lucida Console",
            "Roboto Mono",
            "DejaVu Sans Mono",
            "Source Code Pro",
            "Fira Code",
            "Menlo",
            "Monaco",
            "Inconsolata",
        ]

        available = []
        for font_name in monospace_fonts:
            if font_name.lower() in [f.lower() for f in font.families()]:
                available.append(font_name)

        # Always include a fallback
        if not available:
            available = ["TkFixedFont"]

        return available

    def configure_styles(self):
        """Set up ttk styles for the application"""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Hide native notebook tabs
        self.style.configure(
            "TNotebook", background=self.colors["bg_color"], borderwidth=0, padding=0
        )
        self.style.configure(
            "TNotebook.Tab",
            background=self.colors["bg_color"],
            borderwidth=0,
            padding=0,
            width=0,
        )
        self.style.layout("TNotebook.Tab", [])

        # Modern scrollbar styling
        self.style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            width=12,
            arrowsize=0,
            troughcolor=self.colors["bg_color"],
            bordercolor=self.colors["bg_color"],
            relief="flat",
            darkcolor=self.colors["scroll_color"],
            lightcolor=self.colors["scroll_color"],
        )
        self.style.map(
            "Modern.Vertical.TScrollbar",
            darkcolor=[("active", "#606060")],
            lightcolor=[("active", "#606060")],
        )

        # Horizontal scrollbar
        self.style.configure(
            "Modern.Horizontal.TScrollbar",
            gripcount=0,
            height=12,
            arrowsize=0,
            troughcolor=self.colors["bg_color"],
            bordercolor=self.colors["bg_color"],
            relief="flat",
            darkcolor=self.colors["scroll_color"],
            lightcolor=self.colors["scroll_color"],
        )
        self.style.map(
            "Modern.Horizontal.TScrollbar",
            darkcolor=[("active", "#606060")],
            lightcolor=[("active", "#606060")],
        )

    def create_widgets(self):
        """Create all UI elements"""
        # Title Bar
        self.title_bar = tk.Frame(
            self.root, bg=self.colors["title_bar_color"], height=40
        )
        self.title_bar.pack(fill="x", side="top")

        # Drag Area
        self.drag_area = tk.Frame(self.title_bar, bg=self.colors["title_bar_color"])
        self.drag_area.pack(side="left", expand=True, fill="both")

        if self.app_icon:
            icon_label = tk.Label(
                self.drag_area, image=self.app_icon, bg=self.colors["title_bar_color"]
            )
            icon_label.pack(side="left", padx=(10, 5))

        title_label = tk.Label(
            self.drag_area,
            text="Enhanced Notepad (because fuck Microsoft)",
            bg=self.colors["title_bar_color"],
            fg=self.colors["fg_color"],
            font=("Segoe UI Semibold", 10),
        )
        title_label.pack(side="left")

        # Window Controls
        control_frame = tk.Frame(self.title_bar, bg=self.colors["title_bar_color"])
        control_frame.pack(side="right", padx=0)

        # Control Buttons
        controls = [
            ("─", self.root.iconify, 14, "min_btn"),
            ("◻", self.toggle_maximize, 12, "max_btn"),
            ("✕", self.on_close, 14, "close_btn"),
        ]

        for text, cmd, font_size, name in controls:
            btn = tk.Label(
                control_frame,
                text=text,
                bg=self.colors["title_bar_color"],
                fg=self.colors["fg_color"],
                font=("Segoe UI", font_size),
                cursor="hand2",
                padx=12,
                pady=2,
            )
            btn.pack(side="left")
            if name == "close_btn":
                btn.bind(
                    "<Enter>",
                    lambda e: e.widget.config(
                        bg=self.colors["close_hover"], fg="white"
                    ),
                )
                btn.bind(
                    "<Leave>",
                    lambda e: e.widget.config(
                        bg=self.colors["title_bar_color"], fg=self.colors["fg_color"]
                    ),
                )
            else:
                btn.bind(
                    "<Enter>", lambda e: e.widget.config(bg=self.colors["button_hover"])
                )
                btn.bind(
                    "<Leave>",
                    lambda e: e.widget.config(bg=self.colors["title_bar_color"]),
                )
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            setattr(self, name, btn)

        # Drag Functionality
        self.drag_area.bind("<ButtonPress-1>", self.start_move)
        self.drag_area.bind("<B1-Motion>", self.on_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)
        self.title_bar.bind("<Double-Button-1>", lambda e: self.toggle_maximize())

        # Main menu bar
        self.create_main_menu()

        # Custom Tab Bar
        self.tab_bar = tk.Frame(self.root, bg=self.colors["bg_color"])
        self.tab_bar.pack(fill="x", side="top")

        # Notebook (hidden native tabs)
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # New Tab Button
        self.new_tab_btn = tk.Label(
            self.tab_bar,
            text="+",
            bg=self.colors["tab_bg"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 14),
            padx=15,
            cursor="hand2",
        )
        self.new_tab_btn.pack(side="left", padx=(0, 5))
        self.new_tab_btn.bind("<Button-1>", lambda e: self.new_tab())
        self.new_tab_btn.bind(
            "<Enter>", lambda e: e.widget.config(bg=self.colors["button_hover"])
        )
        self.new_tab_btn.bind(
            "<Leave>", lambda e: e.widget.config(bg=self.colors["tab_bg"])
        )

        # Status Bar with multiple sections
        self.create_status_bar()

    def create_main_menu(self):
        """Create the main menu bar with dropdown buttons"""
        menu_frame = tk.Frame(self.title_bar, bg=self.colors["title_bar_color"])
        menu_frame.pack(side="left", padx=15)

        menu_items = [
            {
                "name": "File",
                "items": [
                    {"label": "New", "command": self.new_tab, "accelerator": "Ctrl+N"},
                    {
                        "label": "Open",
                        "command": self.open_file,
                        "accelerator": "Ctrl+O",
                    },
                    {
                        "label": "Save",
                        "command": self.save_file,
                        "accelerator": "Ctrl+S",
                    },
                    {
                        "label": "Save As",
                        "command": self.save_as_file,
                        "accelerator": "Ctrl+Shift+S",
                    },
                    {"separator": True},
                    {"label": "Recent Files", "submenu": self.create_recent_files_menu},
                    {"separator": True},
                    {
                        "label": "Exit",
                        "command": self.on_close,
                        "accelerator": "Alt+F4",
                    },
                ],
            },
            {
                "name": "Edit",
                "items": [
                    {"label": "Undo", "command": self.undo, "accelerator": "Ctrl+Z"},
                    {"label": "Redo", "command": self.redo, "accelerator": "Ctrl+Y"},
                    {"separator": True},
                    {"label": "Cut", "command": self.cut_text, "accelerator": "Ctrl+X"},
                    {
                        "label": "Copy",
                        "command": self.copy_text,
                        "accelerator": "Ctrl+C",
                    },
                    {
                        "label": "Paste",
                        "command": self.paste_text,
                        "accelerator": "Ctrl+V",
                    },
                    {"separator": True},
                    {
                        "label": "Find",
                        "command": self.show_search,
                        "accelerator": "Ctrl+F",
                    },
                    {
                        "label": "Replace",
                        "command": lambda: self.show_search(with_replace=True),
                        "accelerator": "Ctrl+H",
                    },
                    {"separator": True},
                    {
                        "label": "Select All",
                        "command": self.select_all,
                        "accelerator": "Ctrl+A",
                    },
                ],
            },
            {
                "name": "View",
                "items": [
                    {
                        "label": "Word Wrap",
                        "command": self.toggle_word_wrap,
                        "checkable": True,
                        "checked": self.settings.get("word_wrap", True),
                    },
                    {
                        "label": "Line Numbers",
                        "command": self.toggle_line_numbers,
                        "checkable": True,
                        "checked": self.settings.get("show_line_numbers", True),
                    },
                    {
                        "label": "Highlight Current Line",
                        "command": self.toggle_line_highlight,
                        "checkable": True,
                        "checked": self.settings.get("highlight_current_line", True),
                    },
                    {"separator": True},
                    {"label": "Theme", "submenu": self.create_theme_menu},
                    {"label": "Font", "submenu": self.create_font_menu},
                    {"label": "Font Size", "submenu": self.create_font_size_menu},
                ],
            },
        ]

        # Create menu buttons
        for menu_item in menu_items:
            menu_btn = tk.Label(
                menu_frame,
                text=menu_item["name"],
                bg=self.colors["title_bar_color"],
                fg=self.colors["fg_color"],
                font=("Segoe UI", 10),
                cursor="hand2",
                padx=10,
            )
            menu_btn.pack(side="left", padx=(0, 5))

            # Create dropdown popup for each menu button
            self.create_dropdown_menu(menu_btn, menu_item["items"])

            menu_btn.bind(
                "<Enter>", lambda e: e.widget.config(bg=self.colors["button_hover"])
            )
            menu_btn.bind(
                "<Leave>", lambda e: e.widget.config(bg=self.colors["title_bar_color"])
            )

    def create_dropdown_menu(self, parent, items):
        """Create a dropdown menu for a menu button"""
        menu = tk.Menu(
            parent,
            tearoff=0,
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            activebackground=self.colors["accent_color"],
            activeforeground="white",
            borderwidth=1,
            relief="solid",
        )

        # Store menu reference to prevent garbage collection
        parent.menu = menu

        for item in items:
            if "separator" in item and item["separator"]:
                menu.add_separator()
            elif "submenu" in item:
                submenu = tk.Menu(
                    menu,
                    tearoff=0,
                    bg=self.colors["bg_color"],
                    fg=self.colors["fg_color"],
                    activebackground=self.colors["accent_color"],
                    activeforeground="white",
                    borderwidth=1,
                    relief="solid",
                )
                # Call the function that creates the submenu contents
                item["submenu"](submenu)
                menu.add_cascade(label=item["label"], menu=submenu)
            else:
                if "checkable" in item and item["checkable"]:
                    var = tk.BooleanVar(value=item.get("checked", False))
                    menu.add_checkbutton(
                        label=item["label"],
                        variable=var,
                        command=lambda cmd=item[
                            "command"
                        ], v=var: self.run_checkable_command(cmd, v),
                        accelerator=item.get("accelerator", ""),
                    )
                else:
                    menu.add_command(
                        label=item["label"],
                        command=item["command"],
                        accelerator=item.get("accelerator", ""),
                    )

        # Bind click event to show menu
        parent.bind("<Button-1>", lambda e: self.show_menu(e, menu))

    def show_menu(self, event, menu):
        """Show a dropdown menu at the correct position"""
        widget = event.widget
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        menu.post(x, y)

    def run_checkable_command(self, command, var):
        """Run a command for a checkable menu item"""
        command()
        # Toggle checked state if needed

    def create_recent_files_menu(self, menu):
        """Create submenu with recent files"""
        recent_files = self.settings.get("recent_files", [])

        if not recent_files:
            menu.add_command(label="No recent files", state="disabled")
        else:
            for file_path in recent_files:
                if os.path.exists(file_path):
                    # Get filename for display
                    filename = os.path.basename(file_path)
                    # Add ellipsis for long filenames
                    if len(filename) > 30:
                        display_name = filename[:27] + "..."
                    else:
                        display_name = filename
                    menu.add_command(
                        label=display_name,
                        command=lambda fp=file_path: self.open_specific_file(fp),
                    )

        menu.add_separator()
        menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)

    def clear_recent_files(self):
        """Clear the list of recent files"""
        self.settings["recent_files"] = []
        self.save_settings()

    def create_theme_menu(self, menu):
        """Create submenu for theme selection"""
        for theme_name in self.color_schemes.keys():
            menu.add_command(
                label=theme_name.capitalize(),
                command=lambda t=theme_name: self.change_theme(t),
            )

    def create_font_menu(self, menu):
        """Create submenu for font selection"""
        for font_name in self.available_fonts:
            menu.add_command(
                label=font_name, command=lambda f=font_name: self.change_font(f)
            )

    def create_font_size_menu(self, menu):
        """Create submenu for font size selection"""
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20]:
            menu.add_command(
                label=str(size), command=lambda s=size: self.change_font_size(s)
            )

    def change_theme(self, theme_name):
        """Change the application theme"""
        self.current_theme = theme_name
        self.colors = self.color_schemes[theme_name]

        # Update settings
        self.settings["theme"] = theme_name

        # Show theme change message
        messagebox.showinfo(
            "Theme Changed",
            f"Theme changed to {theme_name.capitalize()}. Please restart the application for changes to take effect.",
        )
        self.save_settings()

    def change_font(self, font_name):
        """Change the editor font"""
        self.current_font = font_name
        self.settings["font"] = font_name

        # Update font for all text areas
        for tab in self.tabs:
            text_widget = tab["text_area"]  # Changed from tab.tab_data["text_area"]
            current_size = text_widget.cget("font").split()[-1]
            text_widget.configure(font=(font_name, self.current_font_size))

            # Also update line numbers if enabled
            if hasattr(tab["text_area"], "line_numbers") and tab["text_area"].line_numbers:
                tab["text_area"].line_numbers.configure(font=(font_name, self.current_font_size))

        self.save_settings()

    def change_font_size(self, size):
        """Change the editor font size"""
        self.current_font_size = size
        self.settings["font_size"] = size

        # Update font size for all text areas
        for tab in self.tabs:
            text_widget = tab["text_area"]  # Changed from tab.tab_data["text_area"]
            text_widget.configure(font=(self.current_font, size))

            # Also update line numbers if enabled
            if hasattr(tab["text_area"], "line_numbers") and tab["text_area"].line_numbers:
                tab["text_area"].line_numbers.configure(font=(self.current_font, size))

        self.save_settings()

    def toggle_word_wrap(self):
        """Toggle word wrap setting"""
        current_setting = self.settings.get("word_wrap", True)
        self.settings["word_wrap"] = not current_setting

        # Update all text widgets
        for tab in self.tabs:
            text_widget = tab.tab_data["text_area"]
            text_widget.configure(wrap=tk.WORD if not current_setting else tk.NONE)

        self.save_settings()

    def toggle_line_numbers(self):
        """Toggle line numbers display"""
        current_setting = self.settings.get("show_line_numbers", True)
        self.settings["show_line_numbers"] = not current_setting
        self.show_line_numbers = not current_setting

        # Update all tabs
        for tab in self.tabs:
            if not current_setting:
                self.add_line_numbers_to_tab(tab)
            else:
                if hasattr(tab, "line_numbers_frame"):
                    tab.line_numbers_frame.pack_forget()

        self.save_settings()

    def toggle_line_highlight(self):
        """Toggle highlighting of current line"""
        current_setting = self.settings.get("highlight_current_line", True)
        self.settings["highlight_current_line"] = not current_setting

        # Update all text widgets
        for tab in self.tabs:
            text_widget = tab.tab_data["text_area"]
            if not current_setting:
                self.setup_line_highlighting(text_widget)
            else:
                # Remove current line highlighting
                text_widget.tag_remove("current_line", "1.0", "end")

                # Unbind cursor movement events for line highlighting
                text_widget.unbind("<<CursorPosition>>")
                text_widget.unbind("<KeyRelease>")

        self.save_settings()

    def create_status_bar(self):
        """Create an enhanced status bar with multiple sections"""
        self.status_bar = tk.Frame(self.root, bg=self.colors["bg_color"], height=28)
        self.status_bar.pack(fill="x", side="bottom")

        # Position indicator (line, column)
        self.status_label = tk.Label(
            self.status_bar,
            text="Line 1, Column 0",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.status_label.pack(side="left", padx=15)

        # File encoding
        self.encoding_label = tk.Label(
            self.status_bar,
            text="UTF-8",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 9),
        )
        self.encoding_label.pack(side="right", padx=15)

        # Word count
        self.word_count_label = tk.Label(
            self.status_bar,
            text="Words: 0",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 9),
        )
        self.word_count_label.pack(side="right", padx=15)

        # Modified status
        self.modified_label = tk.Label(
            self.status_bar,
            text="",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 9),
        )
        self.modified_label.pack(side="right", padx=15)

        # Mode indicator (INSERT/REPLACE)
        self.mode_label = tk.Label(
            self.status_bar,
            text="INSERT",
            bg=self.colors["status_bar_color"],
            fg="white",
            font=("Segoe UI", 9),
            width=8,
        )
        self.mode_label.pack(side="right", padx=3)

    def create_first_tab(self):
        """Create the first tab with welcome content"""
        welcome_text = """# Welcome to Enhanced Notepad by ThatSINEWAVE

## Features:
- Modern dark/light themes
- Multiple tabs
- Customizable fonts
- Line numbers and syntax highlighting
- Find and replace
- Auto-save
- Word count and status info

Press Ctrl+N for a new tab
Press Ctrl+O to open a file
Press Ctrl+S to save

Enjoy writing!
"""
        self.new_tab(content=welcome_text, title="Welcome")

    def new_tab(self, content="", title="Untitled", file_path=None):
        """Create a new editor tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors["bg_color"])

        # Text editor container with optional line numbers
        editor_frame = tk.Frame(tab_frame, bg=self.colors["bg_color"])
        editor_frame.pack(fill="both", expand=True)

        # Set up text area with proper scrollbars
        text_frame = tk.Frame(editor_frame, bg=self.colors["bg_color"])
        text_frame.pack(fill="both", expand=True, side="right")

        # Create scrolled text widget with modern scrollbars
        wrap_mode = tk.WORD if self.settings.get("word_wrap", True) else tk.NONE
        text_area = ScrolledText(
            text_frame,
            wrap=wrap_mode,
            bg=self.colors["text_bg"],
            fg=self.colors["fg_color"],
            insertbackground=self.colors["fg_color"],
            font=(self.current_font, self.current_font_size),
            padx=15,
            pady=15,
            highlightthickness=0,
            insertwidth=2,
            selectbackground=self.colors["accent_color"],
        )
        text_area.pack(fill="both", expand=True)

        # Configure custom scrollbars
        scrollbar_v = ttk.Scrollbar(
            text_frame, orient="vertical", style="Modern.Vertical.TScrollbar"
        )
        scrollbar_h = ttk.Scrollbar(
            text_frame, orient="horizontal", style="Modern.Horizontal.TScrollbar"
        )
        text_area.configure(
            yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set
        )
        scrollbar_v.configure(command=text_area.yview)
        scrollbar_h.configure(command=text_area.xview)

        # Remove default scrollbar and add custom one
        default_scrollbar = text_area.vbar
        default_scrollbar.pack_forget()
        scrollbar_v.pack(side="right", fill="y")

        # Add horizontal scrollbar if word wrap is disabled
        if not self.settings.get("word_wrap", True):
            scrollbar_h.pack(side="bottom", fill="x")

        # Insert initial content
        text_area.insert("1.0", content)

        # Set up event bindings
        text_area.bind(
            "<<Modified>>",
            lambda e, tab_idx=len(self.tabs): self.on_text_modified(e, tab_idx),
        )
        text_area.bind(
            "<KeyRelease>",
            lambda e, tab_idx=len(self.tabs): self.update_status(e, tab_idx),
        )
        text_area.bind(
            "<Button-1>",
            lambda e, tab_idx=len(self.tabs): self.update_status(e, tab_idx),
        )

        # Set up tab indent with spaces
        text_area.bind(
            "<Tab>", lambda e, tab_idx=len(self.tabs): self.handle_tab(e, tab_idx)
        )
        text_area.bind(
            "<BackSpace>",
            lambda e, tab_idx=len(self.tabs): self.handle_backspace(e, tab_idx),
        )

        # Add tab to the notebook
        self.notebook.add(tab_frame, text=title)
        tab_idx = len(self.tabs)

        # Line numbers
        if self.show_line_numbers:
            self.add_line_numbers_to_tab(tab_frame, text_area)

        # Apply line highlighting if enabled
        if self.settings.get("highlight_current_line", True):
            self.setup_line_highlighting(text_area)

        # Create custom tab label
        tab_label = self.create_tab_label(title, tab_idx)

        # Tab data dictionary for tracking state
        tab_data = {
            "frame": tab_frame,
            "text_area": text_area,
            "title": title,
            "file_path": file_path,
            "modified": False,
            "tab_title": tab_label["title"],
            "tab_label": tab_label["frame"],
        }

        # Add to tabs list
        self.tabs.append(tab_data)
        self.last_saved_count[tab_idx] = 0

        # Switch to the new tab
        self.notebook.select(tab_idx)
        self.current_tab = tab_idx

        # Set focus to the text area
        text_area.focus_set()

        # Update tab bar
        self.update_tab_bar()

        return tab_data

    def add_line_numbers_to_tab(self, tab_frame, text_area=None):
        """Add line numbers to a tab's text editor"""
        if text_area is None:
            text_area = tab_frame.tab_data["text_area"]

        # Create line numbers frame if it doesn't exist
        if not hasattr(tab_frame, "line_numbers_frame"):
            tab_frame.line_numbers_frame = tk.Frame(
                tab_frame.master, bg=self.colors["line_number_bg"], width=50
            )
            tab_frame.line_numbers_frame.pack(side="left", fill="y", before=text_area)

            # Create text widget for line numbers
            tab_frame.line_numbers = tk.Text(
                tab_frame.line_numbers_frame,
                width=4,
                bg=self.colors["line_number_bg"],
                fg=self.colors["line_number_fg"],
                font=(self.current_font, self.current_font_size),
                padx=5,
                pady=15,
                highlightthickness=0,
                takefocus=0,
                cursor="arrow",
            )
            tab_frame.line_numbers.pack(fill="both", expand=True)

            # Make line numbers read-only
            tab_frame.line_numbers.configure(state="disabled")

            # Sync scrolling
            def sync_scroll(*args):
                tab_frame.line_numbers.yview_moveto(args[0])
                return True

            # Get the scrollbar from the text area
            text_area.vbar["command"] = lambda *args: sync_scroll(
                *args
            ) and text_area.yview(*args)

            # Update line numbers when text changes
            def update_line_numbers(event=None):
                lines = text_area.get("1.0", "end-1c").count("\n") + 1
                line_num_content = "\n".join(str(i) for i in range(1, lines + 1))
                tab_frame.line_numbers.configure(state="normal")
                tab_frame.line_numbers.delete("1.0", "end")
                tab_frame.line_numbers.insert("1.0", line_num_content)
                tab_frame.line_numbers.configure(state="disabled")

                # Set width based on number of digits
                if lines > 999:
                    tab_frame.line_numbers.configure(width=5)
                elif lines > 99:
                    tab_frame.line_numbers.configure(width=4)
                else:
                    tab_frame.line_numbers.configure(width=3)

            # Update line numbers initially
            update_line_numbers()

            # Bind events to update line numbers
            text_area.bind("<KeyRelease>", update_line_numbers)
            text_area.bind("<ButtonRelease-1>", update_line_numbers)

    def setup_line_highlighting(self, text_area):
        """Set up highlighting of the current line"""
        # Configure tag for current line
        text_area.tag_configure(
            "current_line", background=self.colors["line_highlight"]
        )

        # Function to highlight current line
        def highlight_current_line(event=None):
            text_area.tag_remove("current_line", "1.0", "end")
            text_area.tag_add("current_line", "insert linestart", "insert lineend+1c")

        # Call initially
        highlight_current_line()

        # Bind to cursor movement
        text_area.bind("<KeyRelease>", highlight_current_line, add="+")
        text_area.bind("<Button-1>", highlight_current_line, add="+")

    def create_tab_label(self, title, tab_idx):
        """Create a custom tab label with close button"""
        tab_frame = tk.Frame(self.tab_bar, bg=self.colors["tab_bg"], padx=10, pady=5)

        # Title label
        title_label = tk.Label(
            tab_frame,
            text=title,
            bg=self.colors["tab_bg"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 9),
        )
        title_label.pack(side="left", padx=(0, 5))

        # Close button
        close_btn = tk.Label(
            tab_frame,
            text="×",
            bg=self.colors["tab_bg"],
            fg=self.colors["fg_color"],
            font=("Segoe UI", 12),
            cursor="hand2",
            padx=5,
        )
        close_btn.pack(side="right")

        # Event bindings
        tab_frame.bind("<Button-1>", lambda e, idx=tab_idx: self.select_tab(idx))
        title_label.bind("<Button-1>", lambda e, idx=tab_idx: self.select_tab(idx))
        close_btn.bind("<Button-1>", lambda e, idx=tab_idx: self.close_tab(idx))

        # Hover effects
        close_btn.bind(
            "<Enter>",
            lambda e: e.widget.config(bg=self.colors["close_hover"], fg="white"),
        )
        close_btn.bind(
            "<Leave>",
            lambda e: e.widget.config(
                bg=self.colors["tab_bg"], fg=self.colors["fg_color"]
            ),
        )

        tab_frame.pack(side="left", padx=(0, 2), fill="y")

        return {"frame": tab_frame, "title": title_label}

    def update_tab_bar(self):
        """Update the tab bar with correct positioning and colors"""
        # First, hide all tab labels
        for tab in self.tabs:
            tab["tab_label"].pack_forget()

        # Then show them in order
        for i, tab in enumerate(self.tabs):
            tab["tab_label"].pack(side="left", padx=(0, 2), fill="y")

            # Update styling based on selection
            if i == self.current_tab:
                tab["tab_label"].config(bg=self.colors["selected_tab_color"])
                tab["tab_title"].config(bg=self.colors["selected_tab_color"])
                # Update style for all children
                for child in tab["tab_label"].winfo_children():
                    if child is not tab["tab_title"]:  # Skip title label
                        child.config(bg=self.colors["selected_tab_color"])
            else:
                tab["tab_label"].config(bg=self.colors["tab_bg"])
                tab["tab_title"].config(bg=self.colors["tab_bg"])
                # Update style for all children
                for child in tab["tab_label"].winfo_children():
                    if child is not tab["tab_title"]:  # Skip title label
                        child.config(bg=self.colors["tab_bg"])

    def select_tab(self, tab_idx):
        """Select a tab by index"""
        if 0 <= tab_idx < len(self.tabs):
            self.notebook.select(tab_idx)
            self.current_tab = tab_idx
            self.update_tab_bar()

            # Focus on text area
            self.tabs[tab_idx]["text_area"].focus_set()

            # Update status bar
            self.update_status(None, tab_idx)

    def close_tab(self, tab_idx):
        """Close a tab by index with save prompt if modified"""
        if 0 <= tab_idx < len(self.tabs):
            tab_data = self.tabs[tab_idx]

            # Check if file needs saving
            if tab_data["modified"]:
                result = messagebox.askyesnocancel(
                    "Save Changes", f"Save changes to {tab_data['title']}?"
                )
                if result is None:  # Cancel
                    return
                elif result:  # Yes, save
                    saved = self.save_file(tab_idx)
                    if not saved:  # If save was cancelled or failed
                        return

            # Remove the tab
            self.notebook.forget(tab_idx)

            # Remove tab label
            tab_data["tab_label"].destroy()

            # Remove tab data
            self.tabs.pop(tab_idx)

            # Update tab indices for remaining tabs
            self.update_tab_indices()

            # If no tabs remain, create a new empty one
            if not self.tabs:
                self.new_tab()
            # Otherwise, select an appropriate tab
            elif tab_idx < len(self.tabs):
                self.select_tab(tab_idx)
            else:
                self.select_tab(len(self.tabs) - 1)

    def update_tab_indices(self):
        """Update tab indices after closing a tab"""
        # Rebind events with updated indices
        for i, tab_data in enumerate(self.tabs):
            text_area = tab_data["text_area"]
            text_area.bind(
                "<<Modified>>", lambda e, idx=i: self.on_text_modified(e, idx)
            )
            text_area.bind("<KeyRelease>", lambda e, idx=i: self.update_status(e, idx))
            text_area.bind("<Button-1>", lambda e, idx=i: self.update_status(e, idx))

            # Update tab label bindings
            tab_data["tab_label"].bind(
                "<Button-1>", lambda e, idx=i: self.select_tab(idx)
            )
            for child in tab_data["tab_label"].winfo_children():
                if isinstance(child, tk.Label) and child.cget("text") == "×":
                    child.bind("<Button-1>", lambda e, idx=i: self.close_tab(idx))
                else:
                    child.bind("<Button-1>", lambda e, idx=i: self.select_tab(idx))

    def on_text_modified(self, event, tab_idx):
        """Handle text modification events"""
        if 0 <= tab_idx < len(self.tabs):
            text_area = self.tabs[tab_idx]["text_area"]

            # Reset modified flag
            text_area.edit_modified(False)

            # Get current character count
            current_count = len(text_area.get("1.0", "end-1c"))
            last_count = self.last_saved_count.get(tab_idx, 0)

            # Set modified status only if content has changed
            if current_count != last_count:
                if not self.tabs[tab_idx]["modified"]:
                    self.tabs[tab_idx]["modified"] = True
                    update_tab_title(self.tabs[tab_idx])

                # Update word count
                self.update_word_count(tab_idx)

                # Update status (modified indicator)
                self.update_modified_status(tab_idx)

    def update_status(self, event, tab_idx):
        """Update the status bar information"""
        if 0 <= tab_idx < len(self.tabs):
            text_area = self.tabs[tab_idx]["text_area"]

            # Get cursor position
            try:
                cursor_pos = text_area.index(tk.INSERT)
                line, column = cursor_pos.split(".")

                # Update status label
                self.status_label.config(text=f"Line {line}, Column {column}")

                # Update word count
                self.update_word_count(tab_idx)

                # Update modified status
                self.update_modified_status(tab_idx)
            except Exception as e:
                print(f"Error updating status: {e}")

    def update_word_count(self, tab_idx):
        """Update the word count in the status bar"""
        if 0 <= tab_idx < len(self.tabs):
            text_area = self.tabs[tab_idx]["text_area"]
            text = text_area.get("1.0", "end-1c")

            # Count words (non-empty sequences of characters)
            words = len(re.findall(r"\S+", text))

            # Update label
            self.word_count_label.config(text=f"Words: {words}")

    def update_modified_status(self, tab_idx):
        """Update the modified status indicator in the status bar"""
        if 0 <= tab_idx < len(self.tabs):
            is_modified = self.tabs[tab_idx]["modified"]

            if is_modified:
                self.modified_label.config(text="Modified")
            else:
                self.modified_label.config(text="Saved")

    def handle_tab(self, event, tab_idx):
        """Handle tab key presses to insert spaces instead of tabs"""
        if 0 <= tab_idx < len(self.tabs):
            text_area = self.tabs[tab_idx]["text_area"]

            # Insert spaces instead of tab character
            text_area.insert(tk.INSERT, " " * self.tab_size)

            # Prevent default tab behavior
            return "break"

    def handle_backspace(self, event, tab_idx):
        """Handle smart backspace for tab-sized spaces"""
        if 0 <= tab_idx < len(self.tabs):
            text_area = self.tabs[tab_idx]["text_area"]

            # Get current cursor position
            cursor_pos = text_area.index(tk.INSERT)
            line, column = map(int, cursor_pos.split("."))

            # Check if we're at the beginning of a tab block
            if int(column) > 0 and int(column) % self.tab_size == 0:
                # Get the characters before the cursor
                text_before = text_area.get(
                    f"{line}.{int(column) - self.tab_size}", cursor_pos
                )

                # If they're all spaces, delete the whole tab block
                if text_before == " " * self.tab_size:
                    text_area.delete(
                        f"{line}.{int(column) - self.tab_size}", cursor_pos
                    )
                    return "break"

    def open_file(self, event=None):
        """Open a file in the editor"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt"),
                ("Python files", "*.py"),
                ("All files", "*.*"),
            ],
            initialdir=os.path.expanduser("~"),
        )

        if file_path:
            self.open_specific_file(file_path)

    def open_specific_file(self, file_path):
        """Open a specific file by path"""
        if not os.path.exists(file_path):
            messagebox.showerror(
                "File Not Found", f"The file {file_path} does not exist."
            )
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Check if the file is already open
            for i, tab in enumerate(self.tabs):
                if tab["file_path"] == file_path:
                    self.select_tab(i)
                    return

            # Create a new tab with the file content
            filename = os.path.basename(file_path)
            tab_data = self.new_tab(
                content=content, title=filename, file_path=file_path
            )

            # Reset modified flag
            tab_idx = len(self.tabs) - 1
            tab_data["modified"] = False
            update_tab_title(tab_data)

            # Update last saved count
            self.last_saved_count[tab_idx] = len(content)

            # Update recent files
            if file_path not in self.settings.get("recent_files", []):
                recent_files = self.settings.get("recent_files", [])
                recent_files.append(file_path)
                self.settings["recent_files"] = recent_files[
                    -10:
                ]  # Keep only the last 10
                self.save_settings()

            # Update status
            self.update_status(None, tab_idx)

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self, tab_idx=None):
        """Save the current file"""
        if tab_idx is None:
            tab_idx = self.current_tab

        if 0 <= tab_idx < len(self.tabs):
            tab_data = self.tabs[tab_idx]

            # If file doesn't have a path, do "Save As"
            if not tab_data["file_path"]:
                return self.save_as_file(tab_idx)

            try:
                content = tab_data["text_area"].get("1.0", "end-1c")
                with open(tab_data["file_path"], "w", encoding="utf-8") as file:
                    file.write(content)

                # Update state
                tab_data["modified"] = False
                update_tab_title(tab_data)

                # Update last saved count
                self.last_saved_count[tab_idx] = len(content)

                # Update status bar
                self.update_modified_status(tab_idx)

                return True

            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
                return False

        return False

    def save_as_file(self, tab_idx=None):
        """Save file with a new name/location"""
        if tab_idx is None:
            tab_idx = self.current_tab

        if 0 <= tab_idx < len(self.tabs):
            tab_data = self.tabs[tab_idx]

            # Default save directory
            initial_dir = (
                os.path.dirname(tab_data["file_path"])
                if tab_data["file_path"]
                else os.path.expanduser("~")
            )

            # Get new file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("Python files", "*.py"),
                    ("All files", "*.*"),
                ],
                initialdir=initial_dir,
                initialfile=tab_data["title"]
                if not tab_data["file_path"]
                else os.path.basename(tab_data["file_path"]),
            )

            if file_path:
                # Save content
                try:
                    content = tab_data["text_area"].get("1.0", "end-1c")
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(content)

                    # Update tab data
                    filename = os.path.basename(file_path)
                    tab_data["title"] = filename
                    tab_data["file_path"] = file_path
                    tab_data["modified"] = False
                    update_tab_title(tab_data)

                    # Update last saved count
                    self.last_saved_count[tab_idx] = len(content)

                    # Update recent files
                    if file_path not in self.settings.get("recent_files", []):
                        recent_files = self.settings.get("recent_files", [])
                        recent_files.append(file_path)
                        self.settings["recent_files"] = recent_files[
                            -10:
                        ]  # Keep only the last 10
                        self.save_settings()

                    # Update status bar
                    self.update_modified_status(tab_idx)

                    return True

                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {str(e)}")
                    return False

            # User cancelled save
            return False

        return False

    def auto_save(self):
        """Automatically save modified files"""
        for i, tab in enumerate(self.tabs):
            if tab["modified"] and tab["file_path"]:
                self.save_file(i)

        # Schedule next auto-save
        self.root.after(120000, self.auto_save)  # 2 minutes

    def show_search(self, event=None, with_replace=False):
        """Show search/replace interface"""
        # Hide existing search frame if it exists
        if self.search_frame:
            self.search_frame.destroy()
            self.search_frame = None

        # Create new search frame
        self.search_frame = tk.Frame(
            self.root, bg=self.colors["bg_color"], padx=10, pady=5
        )
        self.search_frame.pack(fill="x", after=self.tab_bar, pady=(0, 5))

        # Search field
        search_label = tk.Label(
            self.search_frame,
            text="Find:",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
        )
        search_label.pack(side="left", padx=(0, 5))

        self.search_entry = tk.Entry(
            self.search_frame,
            width=30,
            bg=self.colors["text_bg"],
            fg=self.colors["fg_color"],
            insertbackground=self.colors["fg_color"],
            relief="solid",
            bd=1,
        )
        self.search_entry.pack(side="left", padx=(0, 10))

        # Replace field (optional)
        if with_replace:
            replace_label = tk.Label(
                self.search_frame,
                text="Replace:",
                bg=self.colors["bg_color"],
                fg=self.colors["fg_color"],
            )
            replace_label.pack(side="left", padx=(0, 5))

            self.replace_entry = tk.Entry(
                self.search_frame,
                width=30,
                bg=self.colors["text_bg"],
                fg=self.colors["fg_color"],
                insertbackground=self.colors["fg_color"],
                relief="solid",
                bd=1,
            )
            self.replace_entry.pack(side="left", padx=(0, 10))

        # Search buttons
        find_btn = tk.Button(
            self.search_frame,
            text="Find Next",
            command=self.find_next,
            bg=self.colors["accent_color"],
            fg="white",
            relief="flat",
            padx=10,
        )
        find_btn.pack(side="left", padx=(0, 5))

        if with_replace:
            replace_btn = tk.Button(
                self.search_frame,
                text="Replace",
                command=self.replace_next,
                bg=self.colors["accent_color"],
                fg="white",
                relief="flat",
                padx=10,
            )
            replace_btn.pack(side="left", padx=(0, 5))

            replace_all_btn = tk.Button(
                self.search_frame,
                text="Replace All",
                command=self.replace_all,
                bg=self.colors["accent_color"],
                fg="white",
                relief="flat",
                padx=10,
            )
            replace_all_btn.pack(side="left", padx=(0, 5))

        # Close button
        close_btn = tk.Button(
            self.search_frame,
            text="×",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            relief="flat",
            font=("Segoe UI", 12),
            command=lambda: self.search_frame.destroy(),
        )
        close_btn.pack(side="right")

        # Set focus to search entry
        self.search_entry.focus_set()

        # Pre-populate with selected text
        if 0 <= self.current_tab < len(self.tabs):
            text_area = self.tabs[self.current_tab]["text_area"]
            try:
                selected_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    self.search_entry.insert(0, selected_text)
                    self.search_entry.selection_range(0, tk.END)
            except:
                pass

    def find_next(self, event=None):
        """Find the next occurrence of search text"""
        if not self.search_entry or not 0 <= self.current_tab < len(self.tabs):
            return

        search_text = self.search_entry.get()
        if not search_text:
            return

        text_area = self.tabs[self.current_tab]["text_area"]

        # Start from current position
        start_pos = text_area.index(tk.INSERT)

        # Remove previous search highlighting
        text_area.tag_remove("search", "1.0", tk.END)

        # Configure search highlighting
        text_area.tag_configure("search", background="#4A4A4A", foreground="white")

        # First, try to find after current position
        pos = text_area.search(search_text, start_pos, stopindex=tk.END, nocase=True)

        # If not found, wrap around to beginning
        if not pos:
            pos = text_area.search(search_text, "1.0", stopindex=start_pos, nocase=True)

        if pos:
            # Calculate end position
            end_pos = f"{pos}+{len(search_text)}c"

            # Select and highlight the found text
            text_area.tag_add("search", pos, end_pos)
            text_area.mark_set(tk.INSERT, end_pos)
            text_area.see(pos)

            # True select it
            text_area.tag_remove(tk.SEL, "1.0", tk.END)
            text_area.tag_add(tk.SEL, pos, end_pos)

            return True
        else:
            # Not found
            messagebox.showinfo("Search", f"Cannot find '{search_text}'")
            return False

    def replace_next(self, event=None):
        """Replace the next occurrence of search text"""
        if (
            not self.search_entry
            or not self.replace_entry
            or not 0 <= self.current_tab < len(self.tabs)
        ):
            return

        # First find the next occurrence
        found = self.find_next()
        if not found:
            return

        # Then replace it
        text_area = self.tabs[self.current_tab]["text_area"]
        replace_text = self.replace_entry.get()

        # Get the current selection
        try:
            start = text_area.index(tk.SEL_FIRST)
            end = text_area.index(tk.SEL_LAST)

            # Replace the selection
            text_area.delete(start, end)
            text_area.insert(start, replace_text)

            # Move cursor after the replacement and find next
            new_pos = f"{start}+{len(replace_text)}c"
            text_area.mark_set(tk.INSERT, new_pos)

            # Find the next occurrence
            self.find_next()

        except tk.TclError:
            pass

    def replace_all(self, event=None):
        """Replace all occurrences of search text"""
        if (
            not self.search_entry
            or not self.replace_entry
            or not 0 <= self.current_tab < len(self.tabs)
        ):
            return

        search_text = self.search_entry.get()
        replace_text = self.replace_entry.get()

        if not search_text:
            return

        text_area = self.tabs[self.current_tab]["text_area"]
        content = text_area.get("1.0", tk.END)

        # Count occurrences
        count = content.count(search_text)

        if count == 0:
            messagebox.showinfo("Replace All", f"Cannot find '{search_text}'")
            return

        # Confirm replacement
        confirm = messagebox.askyesno(
            "Replace All",
            f"Replace all {count} occurrences of '{search_text}' with '{replace_text}'?",
        )

        if not confirm:
            return

        # Replace all occurrences
        new_content = content.replace(search_text, replace_text)

        # Update text
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", new_content)

        # Show message
        messagebox.showinfo("Replace All", f"Replaced {count} occurrences.")

    def undo(self, event=None):
        """Undo last edit"""
        if 0 <= self.current_tab < len(self.tabs):
            try:
                self.tabs[self.current_tab]["text_area"].edit_undo()
            except:
                pass

    def redo(self, event=None):
        """Redo last edit"""
        if 0 <= self.current_tab < len(self.tabs):
            try:
                self.tabs[self.current_tab]["text_area"].edit_redo()
            except:
                pass

    def cut_text(self, event=None):
        """Cut selected text"""
        if 0 <= self.current_tab < len(self.tabs):
            self.tabs[self.current_tab]["text_area"].event_generate("<<Cut>>")

    def copy_text(self, event=None):
        """Copy selected text"""
        if 0 <= self.current_tab < len(self.tabs):
            self.tabs[self.current_tab]["text_area"].event_generate("<<Copy>>")

    def paste_text(self, event=None):
        """Paste text from clipboard"""
        if 0 <= self.current_tab < len(self.tabs):
            self.tabs[self.current_tab]["text_area"].event_generate("<<Paste>>")

    def select_all(self, event=None):
        """Select all text in the current tab"""
        if 0 <= self.current_tab < len(self.tabs):
            text_area = self.tabs[self.current_tab]["text_area"]
            text_area.tag_add(tk.SEL, "1.0", "end-1c")
            text_area.mark_set(tk.INSERT, "end")
            text_area.see(tk.INSERT)
            return "break"

    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # File Operations
        self.root.bind("<Control-n>", lambda e: self.new_tab())
        self.root.bind("<Control-o>", self.open_file)
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())

        # Edit Operations
        self.root.bind("<Control-a>", self.select_all)
        self.root.bind("<Control-f>", self.show_search)
        self.root.bind("<Control-h>", lambda e: self.show_search(with_replace=True))
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("<Control-y>", self.redo)

        # Navigation
        self.root.bind("<Control-Tab>", lambda e: self.next_tab())
        self.root.bind("<Control-Shift-Tab>", lambda e: self.previous_tab())

    def next_tab(self):
        """Switch to next tab"""
        new_idx = (self.current_tab + 1) % len(self.tabs)
        self.select_tab(new_idx)

    def previous_tab(self):
        """Switch to previous tab"""
        new_idx = (self.current_tab - 1) % len(self.tabs)
        self.select_tab(new_idx)

    def start_move(self, event):
        """Handle window movement start"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """Handle window movement"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_maximize(self):
        """Toggle window maximized state"""
        if self.is_maximized:
            self.root.geometry(self.prev_geometry)
        else:
            self.prev_geometry = self.root.geometry()
            self.root.geometry(
                f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
            )
        self.is_maximized = not self.is_maximized

    def on_close(self):
        """Handle application close"""
        # Check for unsaved changes
        unsaved = [tab for tab in self.tabs if tab["modified"]]
        if unsaved:
            response = messagebox.askyesnocancel(
                "Unsaved Changes", "You have unsaved changes. Save all before exiting?"
            )
            if response is None:  # Cancel
                return
            if response:  # Save all
                for i in range(len(self.tabs)):
                    if not self.save_file(i):
                        return  # Abort close if any save fails
        # Save settings and quit
        self.save_settings()
        self.root.destroy()

    def create_context_menu(self, text_area):
        """Create right-click context menu"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Undo", command=self.undo)
        context_menu.add_command(label="Redo", command=self.redo)
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=self.cut_text)
        context_menu.add_command(label="Copy", command=self.copy_text)
        context_menu.add_command(label="Paste", command=self.paste_text)
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=self.select_all)

        def show_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        text_area.bind("<Button-3>", show_menu)


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedNotepad(root)
    root.mainloop()
