"""
Вспомогательные функции для приложения: тосты и кастомные модальные диалоги.
"""

import customtkinter as ctk
import tkinter as tk

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_SUCCESS = "#00C9A7"
COLOR_ERROR = "#FF5555"
COLOR_WARNING = "#FFAA00"

def show_toast(parent, message, dialog_type="info", duration=2000):
    if not parent or not parent.winfo_exists():
        return

    toast = ctk.CTkToplevel(parent)
    toast.overrideredirect(True)
    toast.attributes('-topmost', True)
    toast.configure(fg_color=COLOR_BG)

    if dialog_type == "success":
        icon = "✅"
        color = COLOR_SUCCESS
    elif dialog_type == "error":
        icon = "❌"
        color = COLOR_ERROR
    elif dialog_type == "warning":
        icon = "⚠️"
        color = COLOR_WARNING
    else:
        icon = "ℹ️"
        color = COLOR_PRIMARY

    frame = ctk.CTkFrame(toast, fg_color=COLOR_CARD, corner_radius=10)
    frame.pack(padx=10, pady=10)
    label = ctk.CTkLabel(frame, text=f"{icon}  {message}", font=ctk.CTkFont(size=13), text_color=color)
    label.pack(padx=15, pady=10)

    toast.update_idletasks()
    w = toast.winfo_width()
    h = toast.winfo_height()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    x = parent_x + parent_w - w - 10
    y = parent_y + 10
    screen_w = toast.winfo_screenwidth()
    screen_h = toast.winfo_screenheight()
    if x + w > screen_w:
        x = screen_w - w - 10
    if x < 0:
        x = 10
    if y + h > screen_h:
        y = screen_h - h - 10
    if y < 0:
        y = 10
    toast.geometry(f"+{int(x)}+{int(y)}")
    toast.after(duration, toast.destroy)

def show_centered_dialog(parent, title, message, dialog_type="info", buttons=None):
    if dialog_type in ("info", "success", "warning", "error") and buttons is None:
        show_toast(parent, message, dialog_type)
        return True

    dialog = tk.Toplevel(parent)
    dialog.overrideredirect(True)
    dialog.attributes('-topmost', True)
    dialog.attributes('-transparentcolor', 'black')
    dialog.configure(bg='black')

    frame = ctk.CTkFrame(dialog, fg_color=COLOR_CARD, corner_radius=15,
                         border_width=2, border_color="white")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    if dialog_type == "question":
        icon = "❓"
        title_color = COLOR_PRIMARY
    elif dialog_type == "warning":
        icon = "⚠️"
        title_color = COLOR_WARNING
    elif dialog_type == "error":
        icon = "❌"
        title_color = COLOR_ERROR
    else:
        icon = "ℹ️"
        title_color = COLOR_PRIMARY

    title_label = ctk.CTkLabel(frame, text=f"{icon} {title}", font=ctk.CTkFont(size=16, weight="bold"),
                               text_color=title_color)
    title_label.pack(pady=(15, 5))

    msg_label = ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=13),
                             text_color=COLOR_TEXT, wraplength=400)
    msg_label.pack(pady=5, padx=15)

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(pady=(10, 15))

    result = None

    if buttons is None:
        if dialog_type == "question":
            buttons = ("Да", "Нет")
        else:
            buttons = ("OK",)

    def on_click(value):
        nonlocal result
        result = value
        dialog.destroy()

    for btn_text in buttons:
        if btn_text == "Отмена":
            cmd = lambda t=btn_text: on_click(False)
            fg = "transparent"
            hover = "#3A3450"
        else:
            cmd = lambda t=btn_text: on_click(t)
            fg = COLOR_PRIMARY
            hover = COLOR_SECONDARY
        ctk.CTkButton(btn_frame, text=btn_text, width=80, command=cmd,
                      fg_color=fg, hover_color=hover).pack(side="left", padx=5)

    dialog.update_idletasks()
    required_w = frame.winfo_reqwidth() + 20
    required_h = frame.winfo_reqheight() + 20
    required_w = max(280, min(500, required_w))
    required_h = max(150, required_h)

    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - required_w) // 2
    y = parent_y + (parent_h - required_h) // 2

    screen_w = dialog.winfo_screenwidth()
    screen_h = dialog.winfo_screenheight()
    if x + required_w > screen_w:
        x = screen_w - required_w - 10
    if x < 0:
        x = 10
    if y + required_h > screen_h:
        y = screen_h - required_h - 10
    if y < 0:
        y = 10

    dialog.geometry(f"{required_w}x{required_h}+{int(x)}+{int(y)}")

    dialog.bind("<Escape>", lambda e: on_click(False))
    dialog.grab_set()
    dialog.wait_window()
    return result