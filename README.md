<div align="center">

# Notepad

**A Modern Python-Powered Text Editor**  
*Work in Progress - Community Testing Phase*  

![Preview](https://github.com/ThatSINEWAVE/Notepad/blob/main/.github/SCREENSHOTS/Notepad.png)  
*Customizable dark/light themes with tabbed interface*

</div>

## 🚧 Project Status
This project is actively under development. Core functionality is stable, but expect occasional updates and improvements.  
**No pre-compiled .exe available yet** - users can:
- Run directly via Python (`python notepad.py`)
- [Compile it on your own using PyInstaller](#compiling-to-exe)

## ✨ Features

### Editor Core
- **Multi-Tab Interface** with unsaved changes indicators
- **Dark/Light Themes** - VS Code-inspired color schemes
- **Advanced Text Editing**:
  - Line numbers & current line highlighting
  - Customizable tab spacing (2/4/8 spaces)
  - Word wrap toggle
  - Auto-indent support
  - Undo/Redo history

### Productivity Tools
- **Find/Replace** with regex support
- **Auto-Save** (every 2 minutes)
- **Recent Files** list (last 10 files)
- **Status Bar** with:
  - Live position tracking (line/column)
  - Word counter
  - Encoding display
  - Modification status

### UX Enhancements
- Custom title bar with Windows 11-style controls
- Drag-to-move window functionality
- Right-click context menu (Cut/Copy/Paste/Select All)
- System tray icon support
- Customizable monospace fonts (Consolas, Fira Code, etc.)

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## 📥 Installation

### Requirements
- Python 3.10+
- Pillow library

### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/enhanced-notepad.git
cd enhanced-notepad

# Install dependencies
pip install -r requirements.txt

# Launch application
python notepad.py
```

## 🔧 Compiling to EXE
To create a standalone executable (Windows):
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico notepad.py
```
*Compiled binaries will appear in `/dist` directory*

<div align="center">

## [Join my discord server](https://thatsinewave.github.io/Discord-Redirect/)

</div>

## ⌨️ Keybindings

| Command              | Shortcut          |
|----------------------|-------------------|
| New Tab              | `Ctrl + N`        |
| Open File            | `Ctrl + O`        |
| Save File            | `Ctrl + S`        |
| Save As              | `Ctrl + Shift + S`|
| Find Text            | `Ctrl + F`        |
| Replace Text         | `Ctrl + H`        |
| Next Tab             | `Ctrl + Tab`      |
| Previous Tab         | `Ctrl + Shift + Tab`|
| Toggle Word Wrap     | `Ctrl + Alt + W`  |

*Full list available in Help > Keyboard Shortcuts*

## 🎨 Customization
Modify `settings.json` or use in-app menus to:
- Switch between dark/light themes
- Change editor font (supports 20+ monospace fonts)
- Adjust font size (8-24px range)
- Configure tab behavior
- Set custom settings storage location

```json
{
    "theme": "dark",
    "font": "Fira Code",
    "font_size": 14,
    "tab_size": 4,
    "word_wrap": true
}
```

## Contributing

Contributions are welcome! If you want to contribute, feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE).
