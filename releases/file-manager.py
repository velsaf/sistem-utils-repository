import os
import curses
import shutil
import time
from PIL import Image

# Цветовые пары
COLOR_PAIR_NORMAL = 1
COLOR_PAIR_HIGHLIGHT = 2
COLOR_PAIR_WARNING = 3
COLOR_PAIR_TITLE = 4
COLOR_PAIR_BUTTON = 5
COLOR_PAIR_SELECTED = 6

def setup_colors():
    curses.start_color()
    curses.init_pair(COLOR_PAIR_NORMAL, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_HIGHLIGHT, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(COLOR_PAIR_WARNING, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_TITLE, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIR_BUTTON, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(COLOR_PAIR_SELECTED, curses.COLOR_YELLOW, curses.COLOR_BLUE)

def list_directory(path):
    try:
        files = os.listdir(path)
        files = [f for f in files if not f.startswith('.')]
    except PermissionError:
        return None
    return files

def display_file_info(win, path):
    win.clear()
    win.addstr(0, 0, "File Info:", curses.color_pair(COLOR_PAIR_HIGHLIGHT))
    win.addstr(1, 0, f"Path: {path}", curses.color_pair(COLOR_PAIR_NORMAL))
    win.addstr(2, 0, f"Size: {os.path.getsize(path)} bytes", curses.color_pair(COLOR_PAIR_NORMAL))
    win.addstr(3, 0, f"Modified: {time.ctime(os.path.getmtime(path))}", curses.color_pair(COLOR_PAIR_NORMAL))
    win.refresh()
    win.getch()

def copy_file(src, dst):
    try:
        shutil.copy(src, dst)
    except Exception as e:
        return str(e)
    return None

def delete_file(path):
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
    except Exception as e:
        return str(e)
    return None

def search_files(win, path, query):
    win.clear()
    matches = [f for f in os.listdir(path) if query in f and not f.startswith('.')]
    for idx, file in enumerate(matches):
        if idx < win.getmaxyx()[0] - 1:
            win.addstr(idx, 0, file, curses.color_pair(COLOR_PAIR_NORMAL))
    win.refresh()
    return matches

def draw_breadcrumbs(win, path):
    win.clear()
    parts = path.split(os.sep)
    breadcrumbs = " > ".join(parts)
    win.addstr(0, 0, breadcrumbs[:win.getmaxyx()[1] - 1], curses.color_pair(COLOR_PAIR_NORMAL))
    win.refresh()

def draw_buttons(win, selected_button):
    win.clear()
    buttons = [
        ("Home", "F1"),
        ("Back", "F2"),
        ("Copy", "F3"),
        ("Delete", "F4"),
        ("Search", "F5"),
        ("Quit", "F6"),
    ]
    x = 2
    for idx, (label, key) in enumerate(buttons):
        if idx == selected_button:
            win.addstr(0, x, f"[{label}]", curses.color_pair(COLOR_PAIR_SELECTED))
        else:
            win.addstr(0, x, f"[{label}]", curses.color_pair(COLOR_PAIR_BUTTON))
        x += len(label) + 4
    win.refresh()

def image_to_ascii(image_path, width=100):
    try:
        img = Image.open(image_path)
        img = img.convert("L")
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        ascii_chars = "@#S%?*+;:,. "
        ascii_art = ""
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                ascii_art += ascii_chars[pixel // 25]
            ascii_art += "\n"
        return ascii_art
    except Exception as e:
        return f"Error: {e}"

def preview_image(win, path):
    win.clear()
    ascii_art = image_to_ascii(path, width=50)  # Ширина ASCII-арта
    win.addstr(0, 0, "Image Preview (ASCII):", curses.color_pair(COLOR_PAIR_HIGHLIGHT))
    win.addstr(1, 0, ascii_art, curses.color_pair(COLOR_PAIR_NORMAL))
    win.refresh()
    win.getch()

def main(win):
    curses.curs_set(0)
    setup_colors()
    home_path = os.path.expanduser("~")
    current_path = home_path
    selected_index = 0
    selected_button = 0
    scroll_offset = 0
    search_mode = False
    search_query = ""
    focus_on_files = True

    height, width = win.getmaxyx()
    title_win = curses.newwin(1, width, 0, 0)
    main_win = curses.newwin(height - 3, width, 1, 0)
    breadcrumbs_win = curses.newwin(1, width, height - 2, 0)
    buttons_win = curses.newwin(1, width, height - 1, 0)

    main_win.border('#', '#', '#', '#', '#', '#', '#', '#')

    while True:
        new_height, new_width = win.getmaxyx()
        if new_height != height or new_width != width:
            height, width = new_height, new_width
            curses.resize_term(height, width)
            title_win = curses.newwin(1, width, 0, 0)
            main_win = curses.newwin(height - 3, width, 1, 0)
            breadcrumbs_win = curses.newwin(1, width, height - 2, 0)
            buttons_win = curses.newwin(1, width, height - 1, 0)
            main_win.border('#', '#', '#', '#', '#', '#', '#', '#')

        title_win.clear()
        title_win.addstr(0, (width - len("File Manager")) // 2, "File Manager", curses.color_pair(COLOR_PAIR_TITLE))
        title_win.refresh()

        if not search_mode:
            files = list_directory(current_path)
            if files is None:
                continue

            main_win.clear()
            main_win.border('#', '#', '#', '#', '#', '#', '#', '#')
            main_win.addstr(0, 2, "Files", curses.color_pair(COLOR_PAIR_HIGHLIGHT))
            max_y, max_x = main_win.getmaxyx()

            visible_files = files[scroll_offset:scroll_offset + max_y - 2]
            for idx, file in enumerate(visible_files):
                if idx == selected_index - scroll_offset and focus_on_files:
                    main_win.addstr(idx + 1, 1, file[:max_x - 2], curses.color_pair(COLOR_PAIR_SELECTED))
                else:
                    main_win.addstr(idx + 1, 1, file[:max_x - 2], curses.color_pair(COLOR_PAIR_NORMAL))

            if scroll_offset > 0:
                main_win.addstr(0, max_x - 2, "↑", curses.color_pair(COLOR_PAIR_NORMAL))
            if scroll_offset + max_y - 2 < len(files):
                main_win.addstr(max_y - 2, max_x - 2, "↓", curses.color_pair(COLOR_PAIR_NORMAL))

            main_win.refresh()

            draw_breadcrumbs(breadcrumbs_win, current_path)

            draw_buttons(buttons_win, selected_button if not focus_on_files else -1)

            key = win.getch()

            if focus_on_files:
                if key == curses.KEY_UP:
                    if selected_index > 0:
                        selected_index -= 1
                        if selected_index < scroll_offset:
                            scroll_offset = selected_index
                elif key == curses.KEY_DOWN:
                    if selected_index < len(files) - 1:
                        selected_index += 1
                        if selected_index >= scroll_offset + max_y - 2:
                            scroll_offset = selected_index - max_y + 3
                elif key == ord('\t'):
                    focus_on_files = False
                elif key == ord('\n'):
                    selected_file = files[selected_index]
                    new_path = os.path.join(current_path, selected_file)
                    if os.path.isdir(new_path):
                        current_path = new_path
                        selected_index = 0
                        scroll_offset = 0
                    else:
                        if selected_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                            preview_image(main_win, new_path)
                        else:
                            display_file_info(main_win, new_path)
            else:
                if key == curses.KEY_LEFT:
                    if selected_button > 0:
                        selected_button -= 1
                elif key == curses.KEY_RIGHT:
                    if selected_button < 5:
                        selected_button += 1
                elif key == ord('\t'):
                    focus_on_files = True
                elif key == ord('\n'):
                    if selected_button == 0:
                        current_path = home_path
                        selected_index = 0
                        scroll_offset = 0
                    elif selected_button == 1:
                        if current_path != home_path:
                            current_path = os.path.dirname(current_path)
                            selected_index = 0
                            scroll_offset = 0
                    elif selected_button == 2:
                        src = os.path.join(current_path, files[selected_index])
                        dst = os.path.join(current_path, "copy_" + files[selected_index])
                        error = copy_file(src, dst)
                        if error:
                            buttons_win.addstr(0, 0, f"Error: {error}", curses.color_pair(COLOR_PAIR_WARNING))
                        else:
                            buttons_win.addstr(0, 0, "File copied successfully.", curses.color_pair(COLOR_PAIR_NORMAL))
                        buttons_win.refresh()
                        win.getch()
                    elif selected_button == 3:
                        path_to_delete = os.path.join(current_path, files[selected_index])
                        buttons_win.addstr(0, 0, "Are you sure? (y/n)", curses.color_pair(COLOR_PAIR_WARNING))
                        buttons_win.refresh()
                        confirm = win.getch()
                        if confirm == ord('y'):
                            error = delete_file(path_to_delete)
                            if error:
                                buttons_win.addstr(0, 0, f"Error: {error}", curses.color_pair(COLOR_PAIR_WARNING))
                            else:
                                buttons_win.addstr(0, 0, "File deleted successfully.", curses.color_pair(COLOR_PAIR_NORMAL))
                            buttons_win.refresh()
                            win.getch()
                    elif selected_button == 4:
                        search_mode = True
                        search_query = ""
                        main_win.clear()
                        main_win.addstr(0, 0, "Enter search query (press Enter to search):", curses.color_pair(COLOR_PAIR_NORMAL))
                        main_win.refresh()
                        while True:
                            char = win.getch()
                            if char == ord('\n'):
                                break
                            elif char == 127:
                                search_query = search_query[:-1]
                            else:
                                search_query += chr(char)
                            main_win.clear()
                            main_win.addstr(0, 0, "Enter search query (press Enter to search):", curses.color_pair(COLOR_PAIR_NORMAL))
                            main_win.addstr(1, 0, search_query, curses.color_pair(COLOR_PAIR_NORMAL))
                            main_win.refresh()
                        matches = search_files(main_win, current_path, search_query)
                        main_win.addstr(len(matches) + 2, 0, "Press any key to return.", curses.color_pair(COLOR_PAIR_NORMAL))
                        main_win.refresh()
                        win.getch()
                        search_mode = False
                    elif selected_button == 5:
                        break

        else:
            main_win.clear()
            main_win.addstr(0, 0, "Search mode. Press 'q' to exit search.", curses.color_pair(COLOR_PAIR_NORMAL))
            main_win.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
