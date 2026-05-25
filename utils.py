"""
Вспомогательные функции для приложения: тосты и кастомные модальные диалоги.
"""

import customtkinter as ctk

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_SUCCESS = "#00C9A7"
COLOR_ERROR = "#FF5555"
COLOR_WARNING = "#FFAA00"
COLOR_BORDER = "#FFFFFF" 

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

    # Создаём окно без рамки
    dialog = ctk.CTkToplevel(parent)
    dialog.overrideredirect(True)
    dialog.configure(fg_color=COLOR_BG)  
    dialog.transient(parent)
    dialog.grab_set()

    # Основной фрейм с закруглениями и белой обводкой
    frame = ctk.CTkFrame(dialog, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
    frame.pack(fill="both", expand=True, padx=2, pady=2) 

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

    result = False

    def on_yes():
        nonlocal result
        result = True
        dialog.destroy()

    def on_no():
        nonlocal result
        result = False
        dialog.destroy()

    if buttons is None:
        if dialog_type == "question":
            buttons = ("Да", "Нет")
        else:
            buttons = ("OK",)

    if len(buttons) == 2:
        ctk.CTkButton(btn_frame, text=buttons[0], width=100, command=on_yes,
                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=buttons[1], width=100, command=on_no,
                      fg_color="transparent", hover_color="#3A3450").pack(side="left", padx=10)
    else:
        ctk.CTkButton(btn_frame, text=buttons[0], width=120, command=on_yes,
                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY).pack()

    # Автоматическое изменение размеров окна под содержимое
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    w = max(w, 300)
    h = max(h, 160)
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_w = parent.winfo_width()
    parent_h = parent.winfo_height()
    x = parent_x + (parent_w - w) // 2
    y = parent_y + (parent_h - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    dialog.bind("<Escape>", lambda e: on_no())

    dialog.wait_window()
    return result