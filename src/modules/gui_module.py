import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, simpledialog
import threading
import time

# Tkinter-based GUI system
windows = {}
widgets = {}
radio_groups = {}
main_loop_running = False

def create_window(title, width, height):
    window = tk.Tk()
    window.title(title)
    window.geometry(f"{width}x{height}")
    window_id = id(window)
    windows[window_id] = window
    return window_id

def add_button(window_id, text, x, y, width, height, command):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    button = tk.Button(window, text=text, command=lambda: command())
    button.place(x=x, y=y, width=width, height=height)
    widget_id = id(button)
    widgets[widget_id] = button
    return widget_id

def add_label(window_id, text, x, y):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    label = tk.Label(window, text=text)
    label.place(x=x, y=y)
    widget_id = id(label)
    widgets[widget_id] = label
    return widget_id

def add_entry(window_id, x, y, width):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    entry = tk.Entry(window)
    entry.place(x=x, y=y, width=width)
    widget_id = id(entry)
    widgets[widget_id] = entry
    return widget_id

def add_text(window_id, x, y, width, height):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    text_widget = tk.Text(window)
    text_widget.place(x=x, y=y, width=width, height=height)
    widget_id = id(text_widget)
    widgets[widget_id] = text_widget
    return widget_id

def add_checkbox(window_id, text, x, y):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(window, text=text, variable=var)
    checkbox.place(x=x, y=y)
    widget_id = id(checkbox)
    widgets[widget_id] = (checkbox, var)
    return widget_id

def add_radio_button(window_id, text, x, y, group):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    if group not in radio_groups:
        radio_groups[group] = tk.StringVar()
    var = radio_groups[group]
    radio = tk.Radiobutton(window, text=text, variable=var, value=text)
    radio.place(x=x, y=y)
    widget_id = id(radio)
    widgets[widget_id] = (radio, var, group)
    return widget_id

def add_listbox(window_id, x, y, width, height):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    listbox = tk.Listbox(window)
    listbox.place(x=x, y=y, width=width, height=height)
    widget_id = id(listbox)
    widgets[widget_id] = listbox
    return widget_id

def add_canvas(window_id, x, y, width, height):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    canvas = tk.Canvas(window, bg='white')
    canvas.place(x=x, y=y, width=width, height=height)
    widget_id = id(canvas)
    widgets[widget_id] = canvas
    return widget_id

def add_menu(window_id, label):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    window = windows[window_id]
    menubar = window.menu if hasattr(window, 'menu') else tk.Menu(window)
    window.config(menu=menubar)
    menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label=label, menu=menu)
    menu_id = id(menu)
    widgets[menu_id] = menu
    return menu_id

def add_menu_item(menu_id, label, command):
    if menu_id not in widgets:
        raise RuntimeError("Menu not found")
    menu = widgets[menu_id]
    menu.add_command(label=label, command=lambda: command())
    item_id = id(label)  # Simple ID for menu item
    return item_id

def set_title(window_id, title):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    windows[window_id].title(title)

def set_geometry(window_id, width, height):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    windows[window_id].geometry(f"{width}x{height}")

def show_window(window_id):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    windows[window_id].deiconify()

def hide_window(window_id):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    windows[window_id].withdraw()

def close_window(window_id):
    if window_id not in windows:
        raise RuntimeError("Window not found")
    windows[window_id].destroy()
    del windows[window_id]

def get_button_text(button_id):
    if button_id not in widgets:
        raise RuntimeError("Button not found")
    return widgets[button_id]['text']

def set_button_text(button_id, text):
    if button_id not in widgets:
        raise RuntimeError("Button not found")
    widgets[button_id].config(text=text)

def get_label_text(label_id):
    if label_id not in widgets:
        raise RuntimeError("Label not found")
    return widgets[label_id]['text']

def set_label_text(label_id, text):
    if label_id not in widgets:
        raise RuntimeError("Label not found")
    widgets[label_id].config(text=text)

def get_entry_text(entry_id):
    if entry_id not in widgets:
        raise RuntimeError("Entry not found")
    return widgets[entry_id].get()

def set_entry_text(entry_id, text):
    if entry_id not in widgets:
        raise RuntimeError("Entry not found")
    widgets[entry_id].delete(0, tk.END)
    widgets[entry_id].insert(0, text)

def get_text_content(text_id):
    if text_id not in widgets:
        raise RuntimeError("Text widget not found")
    return widgets[text_id].get("1.0", tk.END).strip()

def set_text_content(text_id, content):
    if text_id not in widgets:
        raise RuntimeError("Text widget not found")
    widgets[text_id].delete("1.0", tk.END)
    widgets[text_id].insert("1.0", content)

def insert_text(text_id, text):
    if text_id not in widgets:
        raise RuntimeError("Text widget not found")
    widgets[text_id].insert(tk.END, text)

def delete_text(text_id, start, end):
    if text_id not in widgets:
        raise RuntimeError("Text widget not found")
    widgets[text_id].delete(start, end)

def get_checkbox_state(checkbox_id):
    if checkbox_id not in widgets:
        raise RuntimeError("Checkbox not found")
    checkbox, var = widgets[checkbox_id]
    return var.get()

def set_checkbox_state(checkbox_id, state):
    if checkbox_id not in widgets:
        raise RuntimeError("Checkbox not found")
    checkbox, var = widgets[checkbox_id]
    var.set(state)

def get_selected_radio(group):
    if group not in radio_groups:
        return None
    return radio_groups[group].get()

def set_selected_radio(radio_id):
    if radio_id not in widgets:
        raise RuntimeError("Radio button not found")
    radio, var, group = widgets[radio_id]
    var.set(radio['text'])

def get_listbox_selection(listbox_id):
    if listbox_id not in widgets:
        raise RuntimeError("Listbox not found")
    listbox = widgets[listbox_id]
    selection = listbox.curselection()
    if selection:
        return listbox.get(selection[0])
    return None

def set_listbox_items(listbox_id, items):
    if listbox_id not in widgets:
        raise RuntimeError("Listbox not found")
    listbox = widgets[listbox_id]
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

def add_listbox_item(listbox_id, item):
    if listbox_id not in widgets:
        raise RuntimeError("Listbox not found")
    widgets[listbox_id].insert(tk.END, item)

def remove_listbox_item(listbox_id, index):
    if listbox_id not in widgets:
        raise RuntimeError("Listbox not found")
    widgets[listbox_id].delete(index)

def clear_listbox(listbox_id):
    if listbox_id not in widgets:
        raise RuntimeError("Listbox not found")
    widgets[listbox_id].delete(0, tk.END)

def draw_line(canvas_id, x1, y1, x2, y2, color, width):
    if canvas_id not in widgets:
        raise RuntimeError("Canvas not found")
    canvas = widgets[canvas_id]
    return canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

def draw_rectangle(canvas_id, x, y, width, height, fill_color, outline_color, outline_width):
    if canvas_id not in widgets:
        raise RuntimeError("Canvas not found")
    canvas = widgets[canvas_id]
    return canvas.create_rectangle(x, y, x+width, y+height, fill=fill_color, outline=outline_color, width=outline_width)

def draw_oval(canvas_id, x, y, width, height, fill_color, outline_color, outline_width):
    if canvas_id not in widgets:
        raise RuntimeError("Canvas not found")
    canvas = widgets[canvas_id]
    return canvas.create_oval(x, y, x+width, y+height, fill=fill_color, outline=outline_color, width=outline_width)

def draw_text(canvas_id, x, y, text, font, color):
    if canvas_id not in widgets:
        raise RuntimeError("Canvas not found")
    canvas = widgets[canvas_id]
    return canvas.create_text(x, y, text=text, font=font, fill=color)

def clear_canvas(canvas_id):
    if canvas_id not in widgets:
        raise RuntimeError("Canvas not found")
    widgets[canvas_id].delete("all")

def bind_event(widget_id, event, callback):
    if widget_id not in widgets:
        raise RuntimeError("Widget not found")
    widget = widgets[widget_id]
    if isinstance(widget, tuple):
        widget = widget[0]  # For checkboxes and radios
    widget.bind(event, lambda e: callback())

def message_box(title, message, type):
    if type == "info":
        return messagebox.showinfo(title, message)
    elif type == "warning":
        return messagebox.showwarning(title, message)
    elif type == "error":
        return messagebox.showerror(title, message)
    elif type == "question":
        return messagebox.askquestion(title, message)
    elif type == "yesno":
        return messagebox.askyesno(title, message)
    elif type == "okcancel":
        return messagebox.askokcancel(title, message)
    elif type == "retrycancel":
        return messagebox.askretrycancel(title, message)
    else:
        return messagebox.showinfo(title, message)

def input_dialog(title, prompt):
    return simpledialog.askstring(title, prompt)

def file_dialog(title, filetypes, save):
    if save:
        return filedialog.asksaveasfilename(title=title, filetypes=filetypes)
    else:
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

def color_chooser(title, initial_color):
    return colorchooser.askcolor(title=title, color=initial_color)

def start_main_loop():
    global main_loop_running
    main_loop_running = True
    tk.mainloop()

def quit_main_loop():
    global main_loop_running
    main_loop_running = False
    for window in windows.values():
        try:
            window.quit()
        except:
            pass
