<div align="center">

# Notepad

Notepad is a modern, customizable text editor built using Python and Tkinter, designed to replace the default Windows Notepad. With features such as multiple tabs, a custom theme, and enhanced user interface, this application aims to provide a more functional and visually appealing experience for users.

</div>

## Features

- **Tabbed Interface**: Supports multiple documents opened in tabs.
- **Customizable Theme**: A sleek dark theme with a modern design and customizable colors.
- **File Operations**: Open, save, and save as for text files.
- **Text Editing**: Standard text editing features with keyboard shortcuts for cut, copy, paste, and select-all.
- **Drag & Drop Window**: The title bar can be dragged to move the window around.
- **Window Controls**: Custom buttons for minimizing, maximizing, and closing the application window.
- **Status Bar**: Displays the current line, column, and UTF-8 encoding of the text.
- **Context Menu**: Right-click to access common text operations such as cut, copy, and paste.
- **File Type Support**: Works with `.txt` files and other file formats.
- **Responsive Design**: The window size is adjustable and supports different screen resolutions.

<div align="center">

## ☕ [Support my work on Ko-Fi](https://ko-fi.com/thatsinewave)

</div>

## Installation

1. Ensure that Python 3.x is installed on your machine.
2. Install required libraries by running the following command:

   ```bash
   pip install pillow
   ```

   This will install the Pillow library, which is used for handling images like the app icon.

3. Download or clone the repository:

   ```bash
   git clone https://github.com/yourusername/notepad.git
   ```

4. Navigate to the project directory and run the application:

   ```bash
   python notepad.py
   ```

## Usage

1. **Opening a New File**: Press `Ctrl + N` to open a new tab.
2. **Opening an Existing File**: Press `Ctrl + O` to open a file from your file system.
3. **Saving a File**: Press `Ctrl + S` to save the current file. If it is a new file, it will prompt you to choose a location.
4. **Save As**: Press `Ctrl + Shift + S` to save the file with a new name.
5. **Close a Tab**: Press `Ctrl + W` to close the current tab. If there are unsaved changes, it will prompt to save.
6. **Basic Text Editing**: Use `Ctrl + C`, `Ctrl + X`, and `Ctrl + V` for copy, cut, and paste operations respectively.
7. **Search Text**: Use the `Edit > Find` menu option to search for specific text in the document (not yet implemented in the code, but can be added).

## Keybindings

- **Ctrl + N**: New Tab
- **Ctrl + O**: Open File
- **Ctrl + S**: Save File
- **Ctrl + Shift + S**: Save As
- **Ctrl + W**: Close Tab
- **Ctrl + T**: New Tab
- **Ctrl + X**: Cut Text
- **Ctrl + C**: Copy Text
- **Ctrl + V**: Paste Text
- **Ctrl + A**: Select All Text

<div align="center">

## [Join my discord server](https://discord.gg/2nHHHBWNDw)

</div>


## Customization

- **Colors**: The theme of the editor is customizable through the code. Adjust the following variables to change the appearance:
  - `bg_color`: Background color for the editor.
  - `title_bar_color`: Color of the title bar.
  - `text_bg`: Background color for the text area.
  - `fg_color`: Foreground (text) color.
  - `highlight_color`: Color for highlighted text.

- **Icons**: The app icon can be changed by replacing the `icon.ico` file in the project directory.

## Contributing

Contributions are welcome! If you want to contribute, feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE).