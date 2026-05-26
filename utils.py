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
    """Показывает всплывающее уведомление в правом верхнем углу родительского окна."""
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
    toast.geometry(f"+{x}+{y}")
    toast.after(duration, toast.destroy)

def show_centered_dialog(parent, title, message, dialog_type="info", buttons=None):

    if dialog_type in ("info", "success", "warning", "error") and buttons is None:
        show_toast(parent, message, dialog_type)
        return True

    dialog = tk.Toplevel(parent)
    dialog.overrideredirect(True)
    dialog.attributes('-transparentcolor', 'black')
    dialog.configure(bg='black')

    w = 400
    h = 200
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - w) // 2
    y = parent_y + (parent_h - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    frame = ctk.CTkFrame(dialog, fg_color=COLOR_CARD, corner_radius=15,
                         border_width=2, border_color="white")
    frame.place(relwidth=1, relheight=1)

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
                             text_color=COLOR_TEXT, wraplength=350)
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
            cmd = lambda t=btn_text: on_click(False)  # Отмена возвращает False
            fg = "transparent"
            hover = "#3A3450"
        else:
            cmd = lambda t=btn_text: on_click(t)
            fg = COLOR_PRIMARY
            hover = COLOR_SECONDARY
        ctk.CTkButton(btn_frame, text=btn_text, width=100, command=cmd,
                      fg_color=fg, hover_color=hover).pack(side="left", padx=5)

    dialog.update_idletasks()
    # Авто-подбор размера
    required_w = frame.winfo_reqwidth() + 10
    required_h = frame.winfo_reqheight() + 10
    required_w = max(280, min(500, required_w))
    required_h = max(150, required_h)

    x = parent_x + (parent_w - required_w) // 2
    y = parent_y + (parent_h - required_h) // 2
    dialog.geometry(f"{required_w}x{required_h}+{x}+{y}")
    frame.place(relwidth=1, relheight=1)

    dialog.bind("<Escape>", lambda e: on_click(False))
    dialog.grab_set()
    dialog.wait_window()
    return result