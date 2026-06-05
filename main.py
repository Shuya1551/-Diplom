"""
Главный модуль приложения.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import Menu
from datetime import datetime, date, timedelta
import calendar
import bcrypt
import csv
import os

from services.file_storage import (
    init_admin_user, authenticate_user, create_user,
    get_all_event_plans, delete_event_plan, get_event_plan_by_id,
    create_event_plan, update_event_plan,
    get_recent_news, get_all_generated_news, save_generated_news,
    delete_generated_news, get_news_by_user_id, get_setting, set_setting,
    log_generation, get_all_generation_logs, get_generation_stats,
    get_all_users, get_user_by_id, update_user, delete_user, change_password
)
from services.gpt_news_generator import GPTNewsGenerator
from gui.generation_frame import GenerationFrame
from gui.generation_process_frame import GenerationProcessFrame
from gui.news_view_frame import NewsViewFrame
from gui.all_news_frame import AllNewsFrame
from gui.export_selection_frame import ExportSelectionFrame
from gui.profile_frame import ProfileFrame
from gui.settings_window import SettingsWindow
from gui.admin_window import AdminWindow
from utils import show_centered_dialog

# ---------- ЦВЕТА ----------
COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_news_generator = None

def get_news_generator(model_path=None):
    global _news_generator
    if _news_generator is None:
        try:
            _news_generator = GPTNewsGenerator(initial_model_path=model_path)
        except Exception as e:
            show_centered_dialog(None, "Ошибка", f"Не удалось загрузить модель:\n{str(e)}", "error")
            return None
    elif model_path and _news_generator.current_model_path != model_path:
        _news_generator.switch_model(model_path)
    return _news_generator

# ---------- ЗАГРУЗКА ГОРОДОВ И КАТЕГОРИЙ ИЗ CSV ----------
def load_cities_from_csv(filepath="city.csv"):
    default_cities = ["Москва", "Санкт-Петербург", "Казань"]
    if not os.path.exists(filepath):
        return default_cities
    cities = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                city_name = (row.get('city') or row.get('settlement') or '').strip()
                if city_name:
                    city_name = city_name.lstrip('г ').lstrip('п ').lstrip('с ').lstrip('д ')
                    cities.append(city_name)
    except Exception as e:
        print(f"Ошибка загрузки городов: {e}")
        return default_cities
    seen = set()
    unique_cities = []
    for city in cities:
        if city not in seen:
            seen.add(city)
            unique_cities.append(city)
    return unique_cities

def load_categories_from_csv(filepath="category.csv"):
    default_categories = ["Конференция", "Семинар", "Вебинар", "Другое"]
    if not os.path.exists(filepath):
        return default_categories
    categories = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            f.seek(0)
            if first_line.lower() == 'category':
                reader = csv.DictReader(f)
                for row in reader:
                    cat = row.get('category', '').strip()
                    if cat:
                        categories.append(cat)
            else:
                for line in f:
                    cat = line.strip()
                    if cat:
                        categories.append(cat)
    except Exception as e:
        print(f"Ошибка загрузки категорий: {e}")
        return default_categories
    seen = set()
    unique_cats = []
    for cat in categories:
        if cat and cat not in seen:
            seen.add(cat)
            unique_cats.append(cat)
    return unique_cats

LOCATION_PRESET = load_cities_from_csv("city.csv")
CATEGORY_PRESET = load_categories_from_csv("category.csv")
if "Другой город" not in LOCATION_PRESET:
    LOCATION_PRESET.append("Другой город")
if "Другое" not in CATEGORY_PRESET:
    CATEGORY_PRESET.append("Другое")

# ---------- ВЫПАДАЮЩИЙ СПИСОК С ПОИСКОМ ----------
class SearchBox(ctk.CTkFrame):
    def __init__(self, master, completevalues, special_values=None, **kwargs):
        super().__init__(master, **kwargs)
        self.completevalues = completevalues
        self.special_values = special_values or []
        self.var = ctk.StringVar()
        self.entry = ctk.CTkEntry(self, textvariable=self.var, width=450, height=40, font=("Arial", 14))
        self.entry.pack(fill="x")
        self.entry.bind('<KeyRelease>', self.on_keyrelease)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        self.entry.bind('<Escape>', self.hide_listbox)
        self.entry.bind('<Down>', self.on_down_arrow)
        self.entry.bind('<Up>', self.on_up_arrow)
        self.listbox_window = None
        self.listbox = None
        self.current_filtered = []
        self.selected_index = -1

        self.root = master.winfo_toplevel()
        self._bind_root_events()

    def _bind_root_events(self):
        self.root.bind("<MouseWheel>", self._on_root_scroll, add=True)
        self.root.bind("<Button-4>", self._on_root_scroll, add=True)
        self.root.bind("<Button-5>", self._on_root_scroll, add=True)
        self.root.bind("<Configure>", self._on_root_configure, add=True)
        self.root.bind("<Button-1>", self._on_global_click, add=True)

    def _unbind_root_events(self):
        try:
            self.root.unbind("<MouseWheel>", self._on_root_scroll)
            self.root.unbind("<Button-4>", self._on_root_scroll)
            self.root.unbind("<Button-5>", self._on_root_scroll)
            self.root.unbind("<Configure>", self._on_root_configure)
            self.root.unbind("<Button-1>", self._on_global_click)
        except:
            pass

    def _on_root_scroll(self, event):
        if self.listbox_window and self.listbox_window.winfo_exists() and self.listbox_window.winfo_viewable():
            try:
                widget_under_cursor = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_cursor == self.listbox:
                    return
            except:
                pass
            self.hide_listbox()

    def _on_root_configure(self, event):
        if self.listbox_window and self.listbox_window.winfo_exists() and self.listbox_window.winfo_viewable():
            self.hide_listbox()

    def _on_global_click(self, event):
        if not (self.listbox_window and self.listbox_window.winfo_exists() and self.listbox_window.winfo_viewable()):
            return
        if event.widget == self.entry:
            return
        if event.widget == self.listbox:
            return
        try:
            if self.listbox_window.winfo_containing(event.x_root, event.y_root):
                return
        except:
            pass
        self.hide_listbox()

    def on_keyrelease(self, event):
        typed = self.var.get()
        if typed == '':
            self.current_filtered = self.completevalues
        else:
            self.current_filtered = [item for item in self.completevalues if typed.lower() in item.lower()]
        self._update_and_show_listbox()
        self.selected_index = -1

    def _update_and_show_listbox(self):
        if not self.current_filtered:
            self.hide_listbox()
            return
        if self.listbox_window is None:
            self.listbox_window = tk.Toplevel(self)
            self.listbox_window.wm_overrideredirect(True)
            self.listbox_window.attributes('-topmost', True)
            self.listbox = tk.Listbox(self.listbox_window, height=6, selectmode=tk.SINGLE,
                                      bg=COLOR_CARD, fg=COLOR_TEXT, font=('Segoe UI', 11))
            self.listbox.pack(fill=tk.BOTH, expand=True)
            self.listbox.bind('<ButtonRelease-1>', self.on_listbox_click)
            self.listbox.bind('<Escape>', self.hide_listbox)
            self.listbox.bind('<MouseWheel>', self._on_listbox_mousewheel)
            self.listbox.bind('<Button-4>', self._on_listbox_mousewheel)
            self.listbox.bind('<Button-5>', self._on_listbox_mousewheel)

        self.listbox.delete(0, tk.END)
        for item in self.current_filtered:
            self.listbox.insert(tk.END, item)
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()
        height = min(6, len(self.current_filtered)) * 24 + 5
        self.listbox_window.geometry(f"{width}x{height}+{x}+{y}")
        self.listbox_window.deiconify()

    def _on_listbox_mousewheel(self, event):
        if self.listbox is None:
            return
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            delta = -1 * (event.delta // 120) if event.delta else 0
        self.listbox.yview_scroll(delta, "units")
        return "break"

    def hide_listbox(self, event=None):
        if self.listbox_window and self.listbox_window.winfo_exists():
            self.listbox_window.withdraw()

    def on_focus_out(self, event):
        self.hide_listbox()

    def on_listbox_click(self, event):
        if self.listbox.curselection():
            selected = self.current_filtered[self.listbox.curselection()[0]]
            self.var.set(selected)
            if selected in self.special_values:
                self.var.set("")
            self.hide_listbox()
        self.entry.focus_set()

    def on_down_arrow(self, event):
        if not self.listbox_window or not self.listbox_window.winfo_exists() or not self.listbox_window.winfo_viewable():
            self._update_and_show_listbox()
            if not self.current_filtered:
                return
            self.selected_index = 0
        else:
            if self.selected_index < len(self.current_filtered) - 1:
                self.selected_index += 1
            else:
                self.selected_index = 0
        if self.selected_index >= 0 and self.listbox:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)
        return "break"

    def on_up_arrow(self, event):
        if self.listbox_window and self.listbox_window.winfo_exists() and self.listbox_window.winfo_viewable() and self.listbox:
            if self.selected_index > 0:
                self.selected_index -= 1
            else:
                self.selected_index = len(self.current_filtered) - 1
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.selected_index)
            self.listbox.see(self.selected_index)
        return "break"

    def get(self):
        return self.var.get().strip()

    def set(self, value):
        self.var.set(value)

    def destroy(self):
        self._unbind_root_events()
        super().destroy()

# ---------- ВЫПАДАЮЩИЙ КАЛЕНДАРЬ ----------
class CalendarDropdown(ctk.CTkToplevel):
    def __init__(self, parent, entry_widget, initial_date=None, callback=None):
        super().__init__(parent)
        self.entry_widget = entry_widget
        self.callback = callback
        self.selected_date = initial_date if initial_date else datetime.now().date()
        self.display_year = self.selected_date.year
        self.display_month = self.selected_date.month

        self.overrideredirect(True)
        self.configure(fg_color=COLOR_CARD)
        self.geometry("280x300")

        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.update_calendar()
        self.bind("<FocusOut>", self.on_focus_out)
        self.focus_set()

    def create_widgets(self):
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10, pady=5)
        self.prev_btn = ctk.CTkButton(self.nav_frame, text="◀", width=30, command=self.prev_month,
                                      fg_color="transparent", text_color=COLOR_SECONDARY)
        self.prev_btn.pack(side="left")
        self.month_label = ctk.CTkLabel(self.nav_frame, text="", font=("Arial", 14, "bold"))
        self.month_label.pack(side="left", expand=True)
        self.next_btn = ctk.CTkButton(self.nav_frame, text="▶", width=30, command=self.next_month,
                                      fg_color="transparent", text_color=COLOR_SECONDARY)
        self.next_btn.pack(side="right")

        days_frame = ctk.CTkFrame(self, fg_color="transparent")
        days_frame.pack(fill="x", padx=10)
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, d in enumerate(weekdays):
            label = ctk.CTkLabel(days_frame, text=d, width=35, font=("Arial", 12))
            label.grid(row=0, column=i, padx=2, pady=2)

        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        self.month_label.configure(text=f"{calendar.month_name[self.display_month]} {self.display_year}")
        cal = calendar.monthcalendar(self.display_year, self.display_month)
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    btn = ctk.CTkButton(self.calendar_frame, text="", width=35, height=35,
                                        fg_color="transparent", state="disabled")
                else:
                    btn = ctk.CTkButton(self.calendar_frame, text=str(day), width=35, height=35,
                                        fg_color="transparent", hover_color=COLOR_SECONDARY,
                                        command=lambda d=day: self.select_day(d))
                    if day == self.selected_date.day and self.display_year == self.selected_date.year and self.display_month == self.selected_date.month:
                        btn.configure(fg_color=COLOR_PRIMARY, text_color=COLOR_TEXT)
                btn.grid(row=week_idx, column=day_idx, padx=2, pady=2)

    def select_day(self, day):
        self.selected_date = date(self.display_year, self.display_month, day)
        if self.callback:
            self.callback(self.selected_date)
        self.destroy()

    def prev_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1
        self.update_calendar()

    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1
        self.update_calendar()

    def on_focus_out(self, event):
        self.destroy()

# ---------- ВСПЛЫВАЮЩИЙ ВЫБОР ВРЕМЕНИ ----------
class TimePickerPopup(ctk.CTkToplevel):
    def __init__(self, parent, entry_widget, initial_hour=0, initial_minute=0, callback=None):
        super().__init__(parent)
        self.entry_widget = entry_widget
        self.callback = callback
        self.hour = initial_hour
        self.minute = initial_minute
        self.after_id = None

        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.transient(parent)
        self.lift()
        self.configure(fg_color=COLOR_CARD)
        self.geometry("180x220")

        # Позиционирование под полем ввода
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        self.geometry(f"+{x}+{y}")

        self.create_widgets()
        self.focus_set()
        self.grab_set()
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind_all("<Button-1>", self.on_global_click, add=True)

    def create_widgets(self):
        """Создаёт элементы управления: часы, минуты, кнопки +/-, OK."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Часы
        hour_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        hour_frame.pack(side="left", expand=True, fill="both")
        ctk.CTkLabel(hour_frame, text="Часы", font=("Arial", 12)).pack(pady=(0, 5))

        self.hour_up_btn = ctk.CTkButton(hour_frame, text="▲", width=60,
                                         fg_color="transparent", text_color=COLOR_SECONDARY)
        self.hour_up_btn.pack(pady=2)
        self.hour_up_btn.bind("<ButtonPress-1>", self.on_hour_up_press)
        self.hour_up_btn.bind("<ButtonRelease-1>", self.on_release)

        self.hour_var = ctk.StringVar(value=f"{self.hour:02d}")
        self.hour_entry = ctk.CTkEntry(hour_frame, textvariable=self.hour_var, width=60, justify="center")
        self.hour_entry.pack(pady=2)

        self.hour_down_btn = ctk.CTkButton(hour_frame, text="▼", width=60,
                                           fg_color="transparent", text_color=COLOR_SECONDARY)
        self.hour_down_btn.pack(pady=2)
        self.hour_down_btn.bind("<ButtonPress-1>", self.on_hour_down_press)
        self.hour_down_btn.bind("<ButtonRelease-1>", self.on_release)

        # Разделитель
        ctk.CTkLabel(main_frame, text=":", font=("Arial", 24)).pack(side="left", padx=10)

        # Минуты
        minute_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        minute_frame.pack(side="left", expand=True, fill="both")
        ctk.CTkLabel(minute_frame, text="Минуты", font=("Arial", 12)).pack(pady=(0, 5))

        self.minute_up_btn = ctk.CTkButton(minute_frame, text="▲", width=60,
                                           fg_color="transparent", text_color=COLOR_SECONDARY)
        self.minute_up_btn.pack(pady=2)
        self.minute_up_btn.bind("<ButtonPress-1>", self.on_minute_up_press)
        self.minute_up_btn.bind("<ButtonRelease-1>", self.on_release)

        self.minute_var = ctk.StringVar(value=f"{self.minute:02d}")
        self.minute_entry = ctk.CTkEntry(minute_frame, textvariable=self.minute_var, width=60, justify="center")
        self.minute_entry.pack(pady=2)

        self.minute_down_btn = ctk.CTkButton(minute_frame, text="▼", width=60,
                                             fg_color="transparent", text_color=COLOR_SECONDARY)
        self.minute_down_btn.pack(pady=2)
        self.minute_down_btn.bind("<ButtonPress-1>", self.on_minute_down_press)
        self.minute_down_btn.bind("<ButtonRelease-1>", self.on_release)

        # Кнопка OK
        ok_btn = ctk.CTkButton(self, text="OK", command=self.select_time,
                               fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        ok_btn.pack(pady=(0, 10))

    # ----- Логика повтора при удержании кнопок -----
    def on_hour_up_press(self, event):
        self.hour_increment()
        self.after_id = self.after(200, self.repeat_hour_up)

    def on_hour_down_press(self, event):
        self.hour_decrement()
        self.after_id = self.after(200, self.repeat_hour_down)

    def on_minute_up_press(self, event):
        self.minute_increment()
        self.after_id = self.after(200, self.repeat_minute_up)

    def on_minute_down_press(self, event):
        self.minute_decrement()
        self.after_id = self.after(200, self.repeat_minute_down)

    def on_release(self, event):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def repeat_hour_up(self):
        self.hour_increment()
        self.after_id = self.after(100, self.repeat_hour_up)

    def repeat_hour_down(self):
        self.hour_decrement()
        self.after_id = self.after(100, self.repeat_hour_down)

    def repeat_minute_up(self):
        self.minute_increment()
        self.after_id = self.after(100, self.repeat_minute_up)

    def repeat_minute_down(self):
        self.minute_decrement()
        self.after_id = self.after(100, self.repeat_minute_down)

    def hour_increment(self):
        self.hour = (self.hour + 1) % 24
        self.hour_var.set(f"{self.hour:02d}")

    def hour_decrement(self):
        self.hour = (self.hour - 1) % 24
        self.hour_var.set(f"{self.hour:02d}")

    def minute_increment(self):
        self.minute = (self.minute + 1) % 60
        self.minute_var.set(f"{self.minute:02d}")

    def minute_decrement(self):
        self.minute = (self.minute - 1) % 60
        self.minute_var.set(f"{self.minute:02d}")

    def select_time(self):
        if self.callback:
            self.callback(self.hour, self.minute)
        self.destroy()

    # ----- Закрытие при клике вне -----
    def on_global_click(self, event):
        if not self.winfo_exists():
            return
        if event.widget == self.entry_widget:
            return
        try:
            toplevel = event.widget.winfo_toplevel()
            if toplevel == self:
                return
        except:
            pass
        self.destroy()

    def on_focus_out(self, event):
        self.destroy()

    # ----- Безопасное уничтожение -----
    def destroy(self):
        try:
            self.unbind_all("<Button-1>")
        except:
            pass
        try:
            self.grab_release()
        except:
            pass
        super().destroy()

# ---------- ВСПЛЫВАЮЩЕЕ ОКНО "О ПРОГРАММЕ" ----------
class AboutPopup(ctk.CTkToplevel):
    def __init__(self, parent, anchor_widget):
        super().__init__(parent)
        self.anchor_widget = anchor_widget
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(fg_color=COLOR_BG)

        frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12,
                             border_width=2, border_color="white")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(frame, text="ℹ️ О программе", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(6, 2))
        ctk.CTkLabel(frame, text="Автор: Головатый И.Н.", font=ctk.CTkFont(size=11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Группа: Идс23Б", font=ctk.CTkFont(size=11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Год: 2026", font=ctk.CTkFont(size=11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Версия: 1.0", font=ctk.CTkFont(size=11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Генератор новостей на основе нейросети ruGPT-3",
                     font=ctk.CTkFont(size=10), text_color=COLOR_GRAY, wraplength=220).pack(anchor="w", padx=12, pady=(6, 6))

        self.update_idletasks()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()

        anchor_x = anchor_widget.winfo_rootx()
        anchor_y = anchor_widget.winfo_rooty()
        anchor_width = anchor_widget.winfo_width()
        anchor_height = anchor_widget.winfo_height()

        anchor_right = anchor_x + anchor_width
        anchor_top = anchor_y

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        offset = 10
        x = anchor_right - popup_width - offset
        y = anchor_top

        if x + popup_width > parent_x + parent_width:
            x = parent_x + parent_width - popup_width - 5
        if x < parent_x + 5:
            x = parent_x + 5
        if y + popup_height > parent_y + parent_height:
            y = anchor_top - popup_height
        if y < parent_y + 5:
            y = parent_y + 5

        self.geometry(f"{popup_width}x{popup_height}+{int(x)}+{int(y)}")

        self.focus_set()
        self.bind("<FocusOut>", lambda e: self.destroy())
        parent.bind("<Button-1>", lambda e: self.destroy(), add=True)
        self.bind("<Escape>", lambda e: self.destroy())

# ---------- ФРЕЙМ АВТОРИЗАЦИИ ----------
class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLOR_BG)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.card = ctk.CTkFrame(self, width=480, height=600, corner_radius=20, fg_color=COLOR_CARD)
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)

        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent", height=40)
        self.top_bar.pack(fill="x", padx=15, pady=(10, 0))
        self.back_btn = ctk.CTkButton(self.top_bar, text="←", width=30, height=30,
                                      fg_color="transparent", text_color=COLOR_SECONDARY,
                                      font=("Arial", 24), command=self.hide_register)
        self.back_btn.pack(side="left")
        self.back_btn.pack_forget()

        self.content_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.login_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.login_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="Генератор новостей", font=("Arial", 22, "bold"),
                     text_color=COLOR_PRIMARY).pack(pady=(0, 5))
        ctk.CTkLabel(self.login_frame, text="Добро пожаловать", font=("Arial", 18),
                     text_color=COLOR_TEXT).pack(pady=(0, 5))
        ctk.CTkLabel(self.login_frame, text="Войдите в свой аккаунт", font=("Arial", 12),
                     text_color=COLOR_TEXT).pack(pady=(0, 15))

        ctk.CTkLabel(self.login_frame, text="Email / Логин", text_color=COLOR_TEXT).pack(anchor="w")
        self.entry_login = ctk.CTkEntry(self.login_frame, placeholder_text="Введите логин или email",
                                        fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.entry_login.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.login_frame, text="Пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.entry_password = ctk.CTkEntry(self.login_frame, placeholder_text="••••••••", show="*",
                                           fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.entry_password.pack(fill="x", pady=(5, 10))

        self.remember_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.login_frame, text="Запомнить меня", variable=self.remember_var,
                        fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY).pack(anchor="w", pady=(0, 10))

        self.login_btn = ctk.CTkButton(self.login_frame, text="ВОЙТИ", command=self.do_login,
                                       height=40, fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                       font=("Arial", 14, "bold"))
        self.login_btn.pack(fill="x", pady=(10, 5))

        self.register_label = ctk.CTkLabel(self.login_frame, text="Нет аккаунта? Зарегистрироваться",
                                           cursor="hand2", text_color=COLOR_SECONDARY)
        self.register_label.pack(pady=10)
        self.register_label.bind("<Button-1>", lambda e: self.show_register())

        self.register_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.entry_password.bind("<Return>", lambda e: self.do_login())

    def show_register(self):
        self.login_frame.pack_forget()
        self.back_btn.pack(side="left")
        for widget in self.register_frame.winfo_children():
            widget.destroy()
        self.register_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.register_frame, text="Регистрация", font=("Arial", 20, "bold"),
                    text_color=COLOR_PRIMARY).pack(pady=(0, 10))

        ctk.CTkLabel(self.register_frame, text="Логин", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_login = ctk.CTkEntry(self.register_frame, placeholder_text="Придумайте логин",
                                    fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_login.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Email", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_email = ctk.CTkEntry(self.register_frame, placeholder_text="your@email.com",
                                    fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_email.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_password = ctk.CTkEntry(self.register_frame, show="*", placeholder_text="минимум 4 символа",
                                        fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_password.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Подтвердите пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_password2 = ctk.CTkEntry(self.register_frame, show="*", fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_password2.pack(fill="x", pady=(5, 10))

        # Роль удалена – всегда будет "user"

        self.register_btn = ctk.CTkButton(self.register_frame, text="Зарегистрироваться", command=self.do_register,
                                        fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        self.register_btn.pack(pady=(15, 5))

    def hide_register(self):
        self.register_frame.pack_forget()
        self.back_btn.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def do_login(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        if not login or not password:
            show_centered_dialog(self, "Ошибка", "Введите логин/email и пароль", "error")
            return
        user = authenticate_user(login, password)
        if user:
            self.on_login_success(user)
        else:
            show_centered_dialog(self, "Ошибка", "Неверный логин/email или пароль", "error")

    def do_register(self):
        login = self.reg_login.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        password2 = self.reg_password2.get()
        if not login or not email or not password:
            show_centered_dialog(self, "Ошибка", "Заполните все поля", "error")
            return
        if password != password2:
            show_centered_dialog(self, "Ошибка", "Пароли не совпадают", "error")
            return
        if len(password) < 4:
            show_centered_dialog(self, "Ошибка", "Пароль должен быть не менее 4 символов", "error")
            return
        # Роль теперь всегда user (is_admin=False)
        pass_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = create_user(login, pass_hash, email, is_admin=False)
        if user_id:
            show_centered_dialog(self, "Успех", f"Пользователь {login} зарегистрирован! Теперь войдите.", "success")
            self.hide_register()
        else:
            show_centered_dialog(self, "Ошибка", "Пользователь с таким логином или email уже существует", "error")

# ---------- ФРЕЙМ РЕДАКТИРОВАНИЯ ПЛАНА ----------
class PlanEditFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back, plan_id=None):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.plan_id = plan_id
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=30, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← Назад", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=("Arial", 14), hover_color="#3A3450")
        back_btn.pack(side="left")
        title = "Редактирование плана" if plan_id else "Создание нового плана"
        ctk.CTkLabel(top_frame, text=title, font=("Arial", 22, "bold"),
                     text_color=COLOR_PRIMARY).pack(side="left", padx=30)

        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=40, pady=10)
        self.center_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.center_frame.pack(expand=True)

        self._create_form()
        if plan_id:
            self._load_data()

    def _create_form(self):
        frame = self.center_frame
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        row = 0

        # Название мероприятия
        ctk.CTkLabel(frame, text="Название мероприятия:*", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.entry_title = ctk.CTkEntry(frame, width=450, height=40, font=("Arial", 14))
        self.entry_title.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Дата проведения
        ctk.CTkLabel(frame, text="Дата проведения:*", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.date_var = ctk.StringVar(value=datetime.now().strftime("%d.%m.%Y"))
        self.date_entry = ctk.CTkEntry(frame, textvariable=self.date_var, width=200, state="normal")
        self.date_entry.grid(row=row, column=1, sticky="w", pady=8)
        self.date_entry.bind("<Button-1>", self.show_calendar_dropdown)

        row += 1
        # Время проведения
        ctk.CTkLabel(frame, text="Время проведения:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        time_frame = ctk.CTkFrame(frame, fg_color="transparent")
        time_frame.grid(row=row, column=1, sticky="w", pady=8)

        ctk.CTkLabel(time_frame, text="Начало:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
        self.start_hour_entry = ctk.CTkEntry(time_frame, width=50, justify="center")
        self.start_hour_entry.pack(side="left")
        self.start_hour_entry.insert(0, "00")
        self.start_hour_entry.bind("<Button-1>", lambda e: self.show_time_picker(True))
        ctk.CTkLabel(time_frame, text=":", font=("Arial", 14)).pack(side="left")
        self.start_minute_entry = ctk.CTkEntry(time_frame, width=50, justify="center")
        self.start_minute_entry.pack(side="left")
        self.start_minute_entry.insert(0, "00")
        self.start_minute_entry.bind("<Button-1>", lambda e: self.show_time_picker(True))

        ctk.CTkLabel(time_frame, text="Окончание:", font=("Arial", 12)).pack(side="left", padx=(15, 5))
        self.end_hour_entry = ctk.CTkEntry(time_frame, width=50, justify="center")
        self.end_hour_entry.pack(side="left")
        self.end_hour_entry.insert(0, "00")
        self.end_hour_entry.bind("<Button-1>", lambda e: self.show_time_picker(False))
        ctk.CTkLabel(time_frame, text=":", font=("Arial", 14)).pack(side="left")
        self.end_minute_entry = ctk.CTkEntry(time_frame, width=50, justify="center")
        self.end_minute_entry.pack(side="left")
        self.end_minute_entry.insert(0, "00")
        self.end_minute_entry.bind("<Button-1>", lambda e: self.show_time_picker(False))

        row += 1
        # Место проведения
        ctk.CTkLabel(frame, text="Место проведения:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.location_box = SearchBox(frame, LOCATION_PRESET, special_values=["Другой город"])
        self.location_box.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Количество участников
        ctk.CTkLabel(frame, text="Количество участников:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.participants_entry = ctk.CTkEntry(frame, width=150, height=40, font=("Arial", 14))
        self.participants_entry.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Категория мероприятия
        ctk.CTkLabel(frame, text="Категория мероприятия:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.category_box = SearchBox(frame, CATEGORY_PRESET, special_values=["Другое"])
        self.category_box.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Формат проведения (новое поле)
        ctk.CTkLabel(frame, text="Формат проведения:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.format_combo = ctk.CTkComboBox(frame, values=["Очный", "Онлайн", "Гибрид"],
                                            width=200, state="readonly")
        self.format_combo.set("Очный")
        self.format_combo.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Спикеры / Ведущие (новое поле)
        ctk.CTkLabel(frame, text="Спикеры / Ведущие:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.entry_speaker = ctk.CTkEntry(frame, width=450, height=40, font=("Arial", 14))
        self.entry_speaker.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Целевая аудитория (новое поле)
        ctk.CTkLabel(frame, text="Целевая аудитория:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.entry_audience = ctk.CTkEntry(frame, width=450, height=40, font=("Arial", 14))
        self.entry_audience.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Организатор / Контактное лицо (новое поле)
        ctk.CTkLabel(frame, text="Организатор / Контактное лицо:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="e", pady=8, padx=(0, 15))
        self.entry_organizer = ctk.CTkEntry(frame, width=450, height=40, font=("Arial", 14))
        self.entry_organizer.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Описание мероприятия (многострочное)
        ctk.CTkLabel(frame, text="Описание мероприятия:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="ne", pady=8, padx=(0, 15))
        self.text_description = ctk.CTkTextbox(frame, height=120, width=450, font=("Arial", 13))
        self.text_description.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Цель мероприятия (многострочное)
        ctk.CTkLabel(frame, text="Цель мероприятия:", font=("Arial", 14),
                    text_color=COLOR_TEXT).grid(row=row, column=0, sticky="ne", pady=8, padx=(0, 15))
        self.text_goal = ctk.CTkTextbox(frame, height=80, width=450, font=("Arial", 13))
        self.text_goal.grid(row=row, column=1, sticky="w", pady=8)

        row += 1
        # Кнопки Сохранить / Отмена
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=25)
        ctk.CTkButton(btn_frame, text="Сохранить", command=self._save,
                    fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                    width=120, height=40, font=("Arial", 14)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Отмена", command=self.on_back,
                    fg_color="transparent", hover_color="#3A3450",
                    width=120, height=40, font=("Arial", 14)).pack(side="left", padx=10)

    def show_calendar_dropdown(self, event):
        current = None
        try:
            current = datetime.strptime(self.date_var.get(), "%d.%m.%Y").date()
        except:
            current = datetime.now().date()
        CalendarDropdown(self, self.date_entry, initial_date=current, callback=self.set_date)

    def set_date(self, date_obj):
        self.date_var.set(date_obj.strftime("%d.%m.%Y"))

    def show_time_picker(self, is_start):
        if is_start:
            hour_val = self.start_hour_entry.get()
            minute_val = self.start_minute_entry.get()
        else:
            hour_val = self.end_hour_entry.get()
            minute_val = self.end_minute_entry.get()
        try:
            hour = int(hour_val)
        except:
            hour = 0
        try:
            minute = int(minute_val)
        except:
            minute = 0

        def on_time_selected(h, m):
            if is_start:
                self.start_hour_entry.delete(0, "end")
                self.start_hour_entry.insert(0, f"{h:02d}")
                self.start_minute_entry.delete(0, "end")
                self.start_minute_entry.insert(0, f"{m:02d}")
            else:
                self.end_hour_entry.delete(0, "end")
                self.end_hour_entry.insert(0, f"{h:02d}")
                self.end_minute_entry.delete(0, "end")
                self.end_minute_entry.insert(0, f"{m:02d}")

        TimePickerPopup(self, self.start_hour_entry if is_start else self.end_hour_entry,
                        initial_hour=hour, initial_minute=minute, callback=on_time_selected)

    def _load_data(self):
        plan = get_event_plan_by_id(self.plan_id, self.user_data['id'], self.user_data['role'])
        if not plan:
            show_centered_dialog(self, "Ошибка", "План не найден", "error")
            self.on_back()
            return

        self.entry_title.insert(0, plan["title"])
        if plan["event_date"]:
            try:
                event_date = datetime.strptime(plan["event_date"], "%Y-%m-%d").date()
                self.set_date(event_date)
            except:
                pass
        if plan.get("event_time"):
            parts = plan["event_time"].split(':')
            if len(parts) >= 2:
                self.start_hour_entry.delete(0, "end")
                self.start_hour_entry.insert(0, f"{int(parts[0]):02d}")
                self.start_minute_entry.delete(0, "end")
                self.start_minute_entry.insert(0, f"{int(parts[1]):02d}")
        if plan.get("event_end_time"):
            parts = plan["event_end_time"].split(':')
            if len(parts) >= 2:
                self.end_hour_entry.delete(0, "end")
                self.end_hour_entry.insert(0, f"{int(parts[0]):02d}")
                self.end_minute_entry.delete(0, "end")
                self.end_minute_entry.insert(0, f"{int(parts[1]):02d}")

        self.location_box.set(plan.get("location", "") or "")
        self.text_description.insert("0.0", plan.get("description", "") or "")
        self.category_box.set(plan.get("category", "") or "")
        self.participants_entry.insert(0, plan.get("participants_count", "0"))
        self.text_goal.insert("0.0", plan.get("goal", "") or "")
        
        # Новые поля
        self.format_combo.set(plan.get("format_type", "Очный") or "Очный")
        self.entry_speaker.insert(0, plan.get("speaker", "") or "")
        self.entry_audience.insert(0, plan.get("audience", "") or "")
        self.entry_organizer.insert(0, plan.get("organizer", "") or "")

    def _save(self):
        title = self.entry_title.get().strip()
        if not title:
            show_centered_dialog(self, "Ошибка", "Название обязательно", "error")
            return
        try:
            event_date = datetime.strptime(self.date_var.get(), "%d.%m.%Y").date()
        except:
            show_centered_dialog(self, "Ошибка", "Некорректная дата", "error")
            return

        start_time = None
        if self.start_hour_entry.get() != "00" or self.start_minute_entry.get() != "00":
            start_time = f"{self.start_hour_entry.get()}:{self.start_minute_entry.get()}:00"
        end_time = None
        if self.end_hour_entry.get() != "00" or self.end_minute_entry.get() != "00":
            end_time = f"{self.end_hour_entry.get()}:{self.end_minute_entry.get()}:00"

        location = self.location_box.get() or None
        category = self.category_box.get() or None
        description = self.text_description.get("0.0", "end").strip() or None
        goal = self.text_goal.get("0.0", "end").strip() or None
        participants_count = self.participants_entry.get().strip()
        try:
            participants_count = int(participants_count) if participants_count else 0
        except:
            participants_count = 0

        # Новые поля
        speaker = self.entry_speaker.get().strip() or None
        audience = self.entry_audience.get().strip() or None
        organizer = self.entry_organizer.get().strip() or None
        format_type = self.format_combo.get().strip() or None

        if self.plan_id:
            success = update_event_plan(
                self.plan_id, title, event_date, start_time, end_time,
                location, description, speaker, audience, category,
                participants_count=participants_count, goal=goal,
                organizer=organizer, format_type=format_type
            )
            if success:
                show_centered_dialog(self, "Успех", "План обновлён", "success")
                self.on_back()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось обновить план", "error")
        else:
            if not self.user_data:
                show_centered_dialog(self, "Ошибка", "Неизвестный пользователь", "error")
                return
            new_id = create_event_plan(
                title, event_date, start_time, end_time,
                location, description, speaker, audience, category,
                self.user_data["id"], participants_count=participants_count, goal=goal,
                organizer=organizer, format_type=format_type
            )
            if new_id:
                show_centered_dialog(self, "Успех", "План создан", "success")
                self.on_back()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось создать план", "error")

# ---------- ФРЕЙМ СПИСКА ПЛАНОВ ----------
class PlansViewFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, switch_to_edit_callback, on_back_to_dashboard):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.switch_to_edit_callback = switch_to_edit_callback
        self.on_back_to_dashboard = on_back_to_dashboard
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← На главную", command=on_back_to_dashboard,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=("Arial", 14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Список планов мероприятий",
                     font=("Arial", 20, "bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)
        new_btn = ctk.CTkButton(top_frame, text="+ Новый план", command=self.new_plan,
                                fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        new_btn.pack(side="right")

        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=10)
        self.load_plans()

    def load_plans(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        plans = get_all_event_plans(self.user_data['id'], self.user_data['role'])
        if not plans:
            lbl = ctk.CTkLabel(self.scrollable, text="Нет планов. Создайте первый план.",
                               text_color=COLOR_GRAY)
            lbl.pack(pady=20)
            return
        for plan in plans:
            plan_id = int(plan["id"])
            title = plan["title"]
            event_date = datetime.fromisoformat(plan["event_date"]) if plan["event_date"] else None
            start_time = plan["event_time"] or ""
            end_time = plan["event_end_time"] or ""
            location = plan["location"] or ""
            description = plan["description"] or ""

            card = ctk.CTkFrame(self.scrollable, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(info_frame, text=title, font=("Arial", 16, "bold"),
                         text_color=COLOR_PRIMARY).pack(anchor="w")
            date_str = event_date.strftime("%d.%m.%Y") if event_date else "дата не указана"
            time_str = f"{start_time} - {end_time}" if start_time or end_time else ""
            details = f"{date_str}  {time_str}  •  {location}" if location else f"{date_str}  {time_str}"
            ctk.CTkLabel(info_frame, text=details, text_color=COLOR_GRAY).pack(anchor="w", pady=(2, 2))
            if description:
                short_desc = description[:150] + "..." if len(description) > 150 else description
                ctk.CTkLabel(info_frame, text=short_desc, text_color=COLOR_TEXT, anchor="w",
                             justify="left", wraplength=400).pack(anchor="w", pady=(5, 0))

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(side="right", padx=10, pady=10)
            edit_btn = ctk.CTkButton(actions, text="✏️ Редактировать", width=100,
                                     command=lambda pid=plan_id: self.switch_to_edit_callback(pid))
            edit_btn.pack(side="left", padx=5)
            delete_btn = ctk.CTkButton(actions, text="🗑 Удалить", width=80,
                                       fg_color="transparent", hover_color="#cc3333",
                                       command=lambda pid=plan_id, ttl=title: self.delete_plan(pid, ttl))
            delete_btn.pack(side="left", padx=5)

    def delete_plan(self, plan_id, plan_title):
        result = show_centered_dialog(self, "Подтверждение", f"Удалить план?\n\n{plan_title}", "question", ("Да", "Нет"))
        if result == "Да":
            delete_event_plan(plan_id)
            self.load_plans()

    def new_plan(self):
        self.switch_to_edit_callback(None)

# ---------- ГЛАВНЫЙ ФРЕЙМ (ДАШБОРД) ----------
class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, switch_to_callback):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.switch_to_callback = switch_to_callback
        self.profile_popup = None
        self.pack(fill="both", expand=True)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.top_nav = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_nav.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.top_nav, text="Генератор новостей",
                     font=("Arial", 20, "bold"), text_color=COLOR_PRIMARY).pack(side="left")
        self.profile_btn = ctk.CTkButton(self.top_nav, text="👤", width=40, height=40,
                                         fg_color="transparent", text_color=COLOR_TEXT,
                                         font=("Arial", 20),
                                         command=lambda: self.show_profile_menu(self.profile_btn))
        self.profile_btn.pack(side="right", padx=(0, 5))

        self.nav_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CARD, corner_radius=10)
        self.nav_frame.pack(fill="x", pady=(0, 20))
        nav_buttons = [("Планы", self.switch_to_plans), ("Генерация", self.switch_to_generation), ("Экспорт", self.switch_to_reports)]
        for i, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(self.nav_frame, text=text, command=command,
                                fg_color="transparent", text_color=COLOR_TEXT,
                                hover_color="#3A3450", width=100)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.nav_frame.grid_columnconfigure(i, weight=1)

        self.grid_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, pady=(0, 20))
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        self.upcoming_frame = ctk.CTkFrame(self.grid_frame, fg_color=COLOR_CARD, corner_radius=15)
        self.upcoming_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        ctk.CTkLabel(self.upcoming_frame, text="📋 Ближайшие планы",
                     font=("Arial", 16, "bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))
        self.upcoming_list_frame = ctk.CTkFrame(self.upcoming_frame, fg_color="transparent")
        self.upcoming_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.quick_gen_frame = ctk.CTkFrame(self.grid_frame, fg_color=COLOR_CARD, corner_radius=15)
        self.quick_gen_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        ctk.CTkLabel(self.quick_gen_frame, text="✨ Быстрая генерация",
                     font=("Arial", 16, "bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))
        self.quick_plan_combo = ctk.CTkComboBox(self.quick_gen_frame, values=["Загрузка..."],
                                                state="readonly", fg_color="#3A3450", button_color=COLOR_PRIMARY)
        self.quick_plan_combo.pack(fill="x", padx=15, pady=(5, 10))
        self.generate_btn = ctk.CTkButton(self.quick_gen_frame, text="🚀 СГЕНЕРИРОВАТЬ НОВОСТЬ",
                                          command=self.quick_generate, height=40,
                                          fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                          font=("Arial", 14, "bold"))
        self.generate_btn.pack(fill="x", padx=15, pady=10)

        self.recent_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_CARD, corner_radius=15)
        self.recent_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.recent_frame, text="🗞️ Последние сгенерированные новости",
                     font=("Arial", 16, "bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))
        self.recent_news_list = ctk.CTkScrollableFrame(self.recent_frame, fg_color="transparent", height=150)
        self.recent_news_list.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        all_news_btn = ctk.CTkButton(self.recent_frame, text="Все новости →", command=self.show_saved_news,
                                     fg_color="transparent", text_color=COLOR_SECONDARY, hover_color="#3A3450")
        all_news_btn.pack(anchor="e", padx=15, pady=(0, 15))

        self.status_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_bar.pack(fill="x", pady=(10, 0))
        self.status_label = ctk.CTkLabel(self.status_bar, text="🟢 Нейросеть активна и готова к работе",
                                         font=("Arial", 12), text_color=COLOR_SECONDARY)
        self.status_label.pack(side="left")
        self.about_label = ctk.CTkLabel(self.status_bar, text="О программе",
                                        font=("Arial", 12, "underline"),
                                        text_color=COLOR_GRAY, cursor="hand2")
        self.about_label.pack(side="right", padx=(0, 10))
        self.about_label.bind("<Button-1>", self.show_about_popup)

        self.load_upcoming_plans()
        self.load_recent_news()
        self.load_plan_list_for_quick()

    def load_upcoming_plans(self):
        for widget in self.upcoming_list_frame.winfo_children():
            widget.destroy()
        all_plans = get_all_event_plans(self.user_data['id'], self.user_data['role'])
        today = date.today()
        future_limit = today + timedelta(days=14)
        upcoming = []
        for plan in all_plans:
            if plan["event_date"]:
                plan_date = datetime.fromisoformat(plan["event_date"]).date()
                if today <= plan_date <= future_limit:
                    upcoming.append((plan_date, plan["title"], int(plan["id"])))
        upcoming.sort(key=lambda x: x[0])
        if not upcoming:
            lbl = ctk.CTkLabel(self.upcoming_list_frame, text="Нет запланированных мероприятий на ближайшие 14 дней",
                               text_color=COLOR_TEXT)
            lbl.pack(anchor="w", pady=2)
        else:
            for plan_date, title, _ in upcoming[:5]:
                lbl = ctk.CTkLabel(self.upcoming_list_frame, text=f"• {title} ({plan_date.strftime('%d.%m.%Y')})",
                                   text_color=COLOR_TEXT, anchor="w")
                lbl.pack(anchor="w", pady=2)

    def load_recent_news(self):
        for widget in self.recent_news_list.winfo_children():
            widget.destroy()
        news_list = get_recent_news(limit=5, user_id=self.user_data['id'], user_role=self.user_data['role'])
        if not news_list:
            lbl = ctk.CTkLabel(self.recent_news_list, text="Нет сгенерированных новостей",
                               text_color=COLOR_TEXT)
            lbl.pack(anchor="w", pady=2)
        else:
            for _, text, gen_date, _ in news_list:
                short_text = text[:100] + "..." if len(text) > 100 else text
                lbl = ctk.CTkLabel(self.recent_news_list, text=f"• {short_text} ({gen_date})",
                                   text_color=COLOR_TEXT, anchor="w")
                lbl.pack(anchor="w", pady=2)

    def load_plan_list_for_quick(self):
        plans = get_all_event_plans(self.user_data['id'], self.user_data['role'])
        if not plans:
            self.quick_plan_combo.configure(values=["Нет доступных планов"])
            self.quick_plan_combo.set("Нет доступных планов")
            return
        plan_display = [f"{p['id']} - {p['title']} ({p['event_date']})" for p in plans]
        self.quick_plan_combo.configure(values=plan_display)
        self.quick_plan_combo.set(plan_display[0])

    def quick_generate(self):
        selected = self.quick_plan_combo.get()
        if not selected or selected == "Нет доступных планов":
            show_centered_dialog(self, "Предупреждение", "Нет доступных планов для генерации", "warning")
            return
        try:
            plan_id = int(selected.split(" - ")[0])
        except:
            show_centered_dialog(self, "Ошибка", "Не удалось определить ID плана", "error")
            return
        self.switch_to_callback("generation_process", plan_id, return_to_main=True)

    def show_saved_news(self):
        self.switch_to_callback("all_news")

    def switch_to_plans(self):
        self.nav_frame.pack_forget()
        self.switch_to_callback("plans")

    def switch_to_generation(self):
        self.switch_to_callback("generation")

    def switch_to_reports(self):
        self.switch_to_callback("export")

    def show_about_popup(self, event):
        AboutPopup(self, self.about_label)

    def show_profile_menu(self, source_widget):
        if self.profile_popup and self.profile_popup.winfo_exists():
            self.profile_popup.destroy()
            self.profile_popup = None
            return

        popup = ctk.CTkToplevel(self.parent)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.configure(fg_color=COLOR_BG)

        frame = ctk.CTkFrame(popup, fg_color=COLOR_CARD, corner_radius=12,
                             border_width=2, border_color="white")
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        items = [
            ("Личный кабинет", "👤", lambda: self._close_and_switch("profile")),
            ("Настройки", "⚙️", lambda: self._close_and_switch("settings")),
        ]
        if self.user_data.get('role') == 'admin':
            items.append(("Администрирование", "👑", lambda: self._close_and_switch("admin")))
        items.extend([
            ("Выйти из профиля", "🚪", self._logout_and_close),
            ("Выйти из приложения", "❌", self._exit_app_and_close)
        ])

        for i, (text, icon, cmd) in enumerate(items):
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)

            btn = ctk.CTkButton(btn_frame, text=text, command=cmd,
                                fg_color="transparent", hover_color="#3A3450",
                                anchor="w", height=32, font=("Arial", 12))
            btn.pack(side="left", fill="x", expand=True)

            icon_label = ctk.CTkLabel(btn_frame, text=icon, font=("Arial", 12),
                                      text_color=COLOR_TEXT, width=25)
            icon_label.pack(side="right", padx=(0, 3))
            icon_label.bind("<Button-1>", lambda e, c=cmd: c())

            if i < len(items) - 1:
                sep = ctk.CTkFrame(frame, height=1, fg_color=COLOR_GRAY)
                sep.pack(fill="x", padx=10, pady=2)

        popup.update_idletasks()
        popup_width = popup.winfo_reqwidth()
        popup_height = popup.winfo_reqheight()

        icon_x = source_widget.winfo_rootx()
        icon_y = source_widget.winfo_rooty()
        icon_width = source_widget.winfo_width()
        icon_height = source_widget.winfo_height()

        icon_right = icon_x + icon_width
        icon_top = icon_y

        parent = self.parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        popup_x = icon_right - popup_width - 45
        popup_y = icon_top

        if popup_x + popup_width > parent_x + parent_width:
            popup_x = parent_x + parent_width - popup_width - 10
        if popup_x < parent_x:
            popup_x = parent_x + 10

        if popup_y + popup_height > parent_y + parent_height:
            popup_y = parent_y + parent_height - popup_height - 10
        if popup_y < parent_y:
            popup_y = parent_y + 10

        popup.geometry(f"{popup_width}x{popup_height}+{int(popup_x)}+{int(popup_y)}")

        popup.bind("<FocusOut>", lambda e: popup.destroy() or setattr(self, 'profile_popup', None))
        popup.bind("<Escape>", lambda e: popup.destroy() or setattr(self, 'profile_popup', None))
        popup.focus_set()

        self.profile_popup = popup

    def _close_and_switch(self, target):
        if self.profile_popup and self.profile_popup.winfo_exists():
            self.profile_popup.destroy()
            self.profile_popup = None
        self.switch_to_callback(target)

    def _logout_and_close(self):
        if self.profile_popup and self.profile_popup.winfo_exists():
            self.profile_popup.destroy()
            self.profile_popup = None
        self.logout()

    def _exit_app_and_close(self):
        if self.profile_popup and self.profile_popup.winfo_exists():
            self.profile_popup.destroy()
            self.profile_popup = None
        self.exit_app()

    def open_profile(self):
        self.switch_to_callback("profile")

    def open_settings(self):
        self.switch_to_callback("settings")

    def about(self):
        pass

    def logout(self):
        self.destroy()
        self.parent.show_login()

    def exit_app(self):
        self.parent.quit()

# ---------- ВСПЛЫВАЮЩЕЕ ОКНО "О ПРОГРАММЕ" ----------
class AboutPopup(ctk.CTkToplevel):
    def __init__(self, parent, anchor_widget):
        super().__init__(parent)
        self.anchor_widget = anchor_widget
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(fg_color=COLOR_BG)

        frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=12,
                             border_width=2, border_color="white")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(frame, text="ℹ️ О программе", font=("Arial", 13, "bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(6, 2))
        ctk.CTkLabel(frame, text="Автор: Головатый И.Н.", font=("Arial", 11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Группа: Идс23Б", font=("Arial", 11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Год: 2026", font=("Arial", 11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Версия: 1.0", font=("Arial", 11),
                     text_color=COLOR_TEXT, anchor="w").pack(anchor="w", padx=12, pady=1)
        ctk.CTkLabel(frame, text="Генератор новостей на основе нейросети ruGPT-3",
                     font=("Arial", 10), text_color=COLOR_GRAY, wraplength=220).pack(anchor="w", padx=12, pady=(6, 6))

        self.update_idletasks()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()

        anchor_x = anchor_widget.winfo_rootx()
        anchor_y = anchor_widget.winfo_rooty()
        anchor_width = anchor_widget.winfo_width()
        anchor_height = anchor_widget.winfo_height()

        anchor_right = anchor_x + anchor_width
        anchor_top = anchor_y

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        offset = 10
        x = anchor_right - popup_width - offset
        y = anchor_top

        if x + popup_width > parent_x + parent_width:
            x = parent_x + parent_width - popup_width - 5
        if x < parent_x + 5:
            x = parent_x + 5
        if y + popup_height > parent_y + parent_height:
            y = anchor_top - popup_height
        if y < parent_y + 5:
            y = parent_y + 5

        self.geometry(f"{popup_width}x{popup_height}+{int(x)}+{int(y)}")

        self.focus_set()
        self.bind("<FocusOut>", lambda e: self.destroy())
        parent.bind("<Button-1>", lambda e: self.destroy(), add=True)
        self.bind("<Escape>", lambda e: self.destroy())

# ---------- ГЛАВНОЕ ОКНО ----------
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Генератор новостей мероприятий")
        self.geometry("520x670")
        self.minsize(480, 600)
        self.resizable(True, True)
        self.configure(fg_color=COLOR_BG)

        # Инициализируем администратора при первом запуске
        init_admin_user()

        # Путь к базовой модели (или любой другой, которая загружается по умолчанию)
        default_model = "./ruGPT3medium_based_on_gpt2"
        self.news_generator = get_news_generator(default_model)
        if self.news_generator is None:
            self.destroy()
            return

        self.apply_window_settings()

        self.current_user_data = None
        self.current_frame = None
        self.show_login()

    def apply_window_settings(self):
        """Применяет сохранённые настройки окна (разрешение и режим)."""
        resolution = get_setting("window_resolution", "1000x700")
        mode = get_setting("window_mode", "Обычный")

        if resolution == "Полноэкранный":
            self.attributes('-fullscreen', True)
        else:
            self.attributes('-fullscreen', False)
            if 'x' in resolution:
                w, h = resolution.split('x')
                self.geometry(f"{w}x{h}")

        if mode == "Развёрнуто на весь экран" and resolution != "Полноэкранный":
            self.state('zoomed')
        elif mode == "На весь экран (F11)":
            self.attributes('-fullscreen', True)
        elif mode == "Обычный":
            self.state('normal')

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self.on_login_success)
        self.current_frame.pack(fill="both", expand=True)
        self.geometry("520x670")

    def on_login_success(self, user_data):
        self.current_user_data = user_data
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, user_data, self.news_generator, self.switch_to_frame)
        self.current_frame.pack(fill="both", expand=True)
        self.geometry("1000x700")

    def switch_to_frame(self, target, plan_id=None, news_id=None, news_text=None, return_to_main=False, selected_plan_id=None, on_back_callback=None):
        if target == "plans":
            self.current_frame.destroy()
            self.current_frame = PlansViewFrame(self, self.current_user_data,
                                                self.news_generator,
                                                self.switch_to_plan_edit,
                                                self.switch_to_dashboard)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "plan_edit":
            self.current_frame.destroy()
            self.current_frame = PlanEditFrame(self, self.current_user_data,
                                               self.news_generator,
                                               self.switch_back_to_plans,
                                               plan_id)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "generation":
            self.current_frame.destroy()
            self.current_frame = GenerationFrame(self, self.current_user_data,
                                                 self.news_generator,
                                                 self.switch_to_dashboard,
                                                 selected_plan_id=selected_plan_id)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "generation_process":
            self.current_frame.destroy()
            if return_to_main:
                on_back = self.switch_to_dashboard
            else:
                on_back = lambda: self.switch_back_to_generation(plan_id)
            self.current_frame = GenerationProcessFrame(self, self.current_user_data,
                                                        self.news_generator,
                                                        on_back,
                                                        plan_id)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "news_view":
            self.current_frame.destroy()
            if on_back_callback is None:
                on_back_callback = lambda: self.switch_back_to_generation(plan_id)
            self.current_frame = NewsViewFrame(self, self.current_user_data,
                                               self.news_generator,
                                               on_back_callback,
                                               news_id, news_text)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "all_news":
            self.current_frame.destroy()
            self.current_frame = AllNewsFrame(self, self.current_user_data,
                                              self.news_generator,
                                              self.switch_to_dashboard)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "export":
            self.current_frame.destroy()
            self.current_frame = ExportSelectionFrame(self, self.current_user_data,
                                                      self.news_generator,
                                                      self.switch_to_dashboard)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "profile":
            self.current_frame.destroy()
            self.current_frame = ProfileFrame(self, self.current_user_data,
                                              self.news_generator,
                                              self.switch_to_dashboard)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "settings":
            self.current_frame.destroy()
            self.current_frame = SettingsWindow(self, self.current_user_data,
                                                self.news_generator,
                                                self.switch_to_dashboard,
                                                apply_window_callback=self.apply_window_settings)
            self.current_frame.pack(fill="both", expand=True)
        elif target == "admin":
            self.current_frame.destroy()
            self.current_frame = AdminWindow(self, self.current_user_data,
                                             self.news_generator,
                                             self.switch_to_dashboard)
            self.current_frame.pack(fill="both", expand=True)

    def switch_to_plan_edit(self, plan_id):
        self.switch_to_frame("plan_edit", plan_id=plan_id)

    def switch_back_to_plans(self):
        self.switch_to_frame("plans")

    def switch_back_to_generation(self, plan_id):
        self.switch_to_frame("generation", selected_plan_id=plan_id)

    def switch_to_dashboard(self):
        self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, self.current_user_data,
                                          self.news_generator, self.switch_to_frame)
        self.current_frame.pack(fill="both", expand=True)

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()