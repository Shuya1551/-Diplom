"""
Диалоговое окно для добавления/редактирования плана мероприятия.
Списки городов и категорий загружаются из CSV-файлов.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from repositories.event_plan_repository import get_event_plan_by_id, create_event_plan, update_event_plan
import csv
import os


# ------------------------ Загрузка данных из CSV ------------------------
def load_cities_from_csv(filepath="city.csv"):
    """
    Загружает список городов из CSV-файла.
    Возвращает список строк.
    """
    default_cities = ["Москва", "Санкт-Петербург", "Казань"]  # резерв
    if not os.path.exists(filepath):
        return default_cities
    cities = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Берём название города из колонки 'city', если нет — из 'settlement'
                city_name = (row.get('city') or row.get('settlement') or '').strip()
                if city_name:
                    # Убираем приставки типа "г " или "п "
                    city_name = city_name.lstrip('г ').lstrip('п ').lstrip('с ').lstrip('д ')
                    cities.append(city_name)
    except Exception as e:
        print(f"Ошибка загрузки городов: {e}")
        return default_cities
    # Убираем дубликаты, сохраняя порядок
    seen = set()
    unique_cities = []
    for city in cities:
        if city not in seen:
            seen.add(city)
            unique_cities.append(city)
    return unique_cities


def load_categories_from_csv(filepath="category.csv"):
    """
    Загружает список категорий из CSV-файла.
    Возвращает список строк.
    """
    default_categories = ["Конференция", "Семинар", "Вебинар", "Другое"]
    if not os.path.exists(filepath):
        return default_categories
    categories = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            f.seek(0)
            # Определяем, есть ли заголовок
            if first_line.lower() == 'category':
                reader = csv.DictReader(f)
                for row in reader:
                    cat = row.get('category', '').strip()
                    if cat:
                        categories.append(cat)
            else:
                # Простой список построчно
                for line in f:
                    cat = line.strip()
                    if cat:
                        categories.append(cat)
    except Exception as e:
        print(f"Ошибка загрузки категорий: {e}")
        return default_categories
    # Убираем пустые и дубликаты
    seen = set()
    unique_cats = []
    for cat in categories:
        if cat and cat not in seen:
            seen.add(cat)
            unique_cats.append(cat)
    return unique_cats


# Загружаем глобальные списки при запуске модуля
LOCATION_PRESET = load_cities_from_csv("city.csv")
CATEGORY_PRESET = load_categories_from_csv("category.csv")

# Добавляем специальные значения "Другой город" и "Другое" в конец, если их ещё нет
if "Другой город" not in LOCATION_PRESET:
    LOCATION_PRESET.append("Другой город")
if "Другое" not in CATEGORY_PRESET:
    CATEGORY_PRESET.append("Другое")


# ------------------------ NumberPicker с симметричной прокруткой ------------------------
class NumberPicker(tk.Canvas):
    """Вертикальный прокручиваемый список чисел с поддержкой drag (симметрично) и wheel."""

    def __init__(self, master, from_, to, default=None, width=60, height=150, item_height=30, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=1, highlightbackground='gray', **kwargs)
        self.from_ = from_
        self.to = to
        self.item_height = item_height
        self.values = list(range(from_, to+1))
        self.selected_index = 0
        if default is not None and default in self.values:
            self.selected_index = self.values.index(default)

        self.visible_items = height // item_height
        self.drag_start_y = None
        self.drag_start_index = None
        self.sensitivity = 25  # пикселей на один шаг

        self.configure(bg='white')
        self.bind('<MouseWheel>', self.on_mousewheel)
        self.bind('<Button-1>', self.on_drag_start)
        self.bind('<B1-Motion>', self.on_drag_move)
        self.bind('<ButtonRelease-1>', self.on_drag_end)
        self.bind('<Configure>', self.on_configure)

        self.draw()

    def on_configure(self, event):
        self.draw()

    def draw(self):
        self.delete('all')
        center_y = self.winfo_height() // 2
        self.create_rectangle(0, center_y - self.item_height//2,
                              self.winfo_width(), center_y + self.item_height//2,
                              fill='lightblue', outline='', tags='selector')

        start_idx = self.selected_index - self.visible_items // 2
        for i in range(self.visible_items + 2):
            idx = start_idx + i
            if 0 <= idx < len(self.values):
                y = i * self.item_height + (self.item_height // 2)
                font = ('Arial', 14, 'bold') if idx == self.selected_index else ('Arial', 12)
                fill = 'blue' if idx == self.selected_index else 'black'
                self.create_text(self.winfo_width()//2, y, text=str(self.values[idx]),
                                 font=font, fill=fill, tags=f'item_{idx}')

    def on_mousewheel(self, event):
        delta = -1 if event.delta < 0 else 1
        self._change_selection(delta)

    def on_drag_start(self, event):
        self.drag_start_y = event.y
        self.drag_start_index = self.selected_index

    def on_drag_move(self, event):
        if self.drag_start_y is None:
            return
        dy = event.y - self.drag_start_y
        if abs(dy) >= self.sensitivity:
            steps = dy // self.sensitivity
            if steps != 0:
                new_index = self.drag_start_index - steps
                self.drag_start_y = event.y - (dy % self.sensitivity)
                self.drag_start_index = new_index
                self._change_selection(0, absolute_index=new_index)

    def on_drag_end(self, event):
        self.drag_start_y = None
        self.drag_start_index = None

    def _change_selection(self, delta=0, absolute_index=None):
        if absolute_index is not None:
            new_idx = absolute_index
        else:
            new_idx = self.selected_index + delta
        if 0 <= new_idx < len(self.values):
            self.selected_index = new_idx
        elif new_idx < 0:
            self.selected_index = 0
        elif new_idx >= len(self.values):
            self.selected_index = len(self.values) - 1
        self.draw()
        self.event_generate('<<NumberPicked>>')

    def get(self):
        return self.values[self.selected_index]

    def set(self, value):
        if value in self.values:
            self.selected_index = self.values.index(value)
            self.draw()


# ------------------------ Всплывающее окно выбора времени ------------------------
class TimePickerPopup(tk.Toplevel):
    def __init__(self, parent, initial_time="00:00"):
        super().__init__(parent)
        self.title("Выберите время")
        self.transient(parent)
        self.grab_set()
        self.result = initial_time
        try:
            h, m = map(int, initial_time.split(':'))
        except:
            h, m = 0, 0

        frame = ttk.Frame(self, padding=10)
        frame.pack()

        ttk.Label(frame, text="Часы").grid(row=0, column=0, padx=5)
        self.hour_picker = NumberPicker(frame, from_=0, to=23, default=h, width=70, height=150, item_height=30)
        self.hour_picker.grid(row=1, column=0, padx=5)

        ttk.Label(frame, text=":", font=('Arial', 20)).grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Минуты").grid(row=0, column=2, padx=5)
        self.minute_picker = NumberPicker(frame, from_=0, to=59, default=m, width=70, height=150, item_height=30)
        self.minute_picker.grid(row=1, column=2, padx=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(btn_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.cancel).pack(side=tk.LEFT, padx=5)
        self.bind('<Escape>', lambda e: self.cancel())
        self.wait_window()

    def ok(self):
        h = self.hour_picker.get()
        m = self.minute_picker.get()
        self.result = f"{h:02d}:{m:02d}"
        self.destroy()

    def cancel(self):
        self.destroy()


# ------------------------ Поле ввода времени с вызовом пикера ------------------------
class TimeEntry(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar(value="00:00")
        self.entry = tk.Entry(self, textvariable=self.var, width=8, font=('Arial', 11))
        self.entry.pack(side=tk.LEFT, padx=2)
        self.entry.bind('<Button-1>', self.show_picker)
        self.btn = ttk.Button(self, text="▼", width=2, command=self.show_picker)
        self.btn.pack(side=tk.LEFT, padx=2)

    def show_picker(self, event=None):
        picker = TimePickerPopup(self, self.var.get())
        self.var.set(picker.result)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


# ------------------------ Виджет поиска с подсказками (без изменений) ------------------------
class SearchBox(tk.Frame):
    def __init__(self, master, completevalues, special_values=None, **kwargs):
        super().__init__(master, **kwargs)
        self.completevalues = completevalues
        self.special_values = special_values or []
        self.var = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.var, width=50)
        self.entry.pack(fill=tk.X)
        self.entry.bind('<KeyRelease>', self.on_keyrelease)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        self.entry.bind('<Escape>', self.hide_listbox)
        self.entry.bind('<Down>', self.on_down_arrow)
        self.entry.bind('<Up>', self.on_up_arrow)
        self.listbox_window = None
        self.listbox = None
        self.current_filtered = []
        self.selected_index = -1

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
            self.listbox = tk.Listbox(self.listbox_window, height=6, selectmode=tk.SINGLE)
            self.listbox.pack(fill=tk.BOTH, expand=True)
            self.listbox.bind('<ButtonRelease-1>', self.on_listbox_click)
            self.listbox.bind('<Escape>', self.hide_listbox)
        self.listbox.delete(0, tk.END)
        for item in self.current_filtered:
            self.listbox.insert(tk.END, item)
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = self.entry.winfo_width()
        height = min(6, len(self.current_filtered)) * 20 + 5
        self.listbox_window.geometry(f"{width}x{height}+{x}+{y}")
        self.listbox_window.deiconify()

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
        if not self.listbox_window or not self.listbox_window.winfo_viewable():
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
        if self.listbox_window and self.listbox_window.winfo_viewable() and self.listbox:
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


# ------------------------ Основной диалог ------------------------
class PlanEditDialog:
    def __init__(self, parent, plan_id=None, user_data=None):
        self.parent = parent
        self.plan_id = plan_id
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Редактирование плана" if plan_id else "Новый план")
        self.window.geometry("550x650")
        self.window.transient(parent)
        self.window.grab_set()
        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        self._create_widgets(frame)
        if plan_id:
            self._load_data()

    def _create_widgets(self, frame):
        row = 0
        tk.Label(frame, text="Название мероприятия:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_title = tk.Entry(frame, width=50)
        self.entry_title.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Дата:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.calendar_date = DateEntry(frame, width=17, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       locale='ru_RU', date_pattern='yyyy-mm-dd')
        self.calendar_date.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        time_frame = tk.Frame(frame)
        time_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        tk.Label(time_frame, text="Начало:").pack(side=tk.LEFT, padx=5)
        self.start_time = TimeEntry(time_frame)
        self.start_time.pack(side=tk.LEFT, padx=5)
        tk.Label(time_frame, text="Окончание:").pack(side=tk.LEFT, padx=5)
        self.end_time = TimeEntry(time_frame)
        self.end_time.pack(side=tk.LEFT, padx=5)

        row += 1
        tk.Label(frame, text="Место проведения:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.location_box = SearchBox(frame, LOCATION_PRESET, special_values=["Другой город"])
        self.location_box.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        tk.Label(frame, text="Категория мероприятия:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_box = SearchBox(frame, CATEGORY_PRESET, special_values=["Другое"])
        self.category_box.grid(row=row, column=1, pady=5, padx=5, sticky=tk.W)

        row += 1
        tk.Label(frame, text="Описание мероприятия:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.text_description = tk.Text(frame, height=5, width=40)
        self.text_description.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Аудитория (кому предназначено):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_audience = tk.Entry(frame, width=50)
        self.entry_audience.grid(row=row, column=1, pady=5, padx=5)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=row+1, column=0, columnspan=2, pady=20)
        tk.Button(btn_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def _load_data(self):
        plan = get_event_plan_by_id(self.plan_id)
        if not plan:
            return
        self.entry_title.insert(0, plan[1])
        if plan[2]:
            self.calendar_date.set_date(plan[2])
        if plan[3]:
            self.start_time.set(plan[3].strftime("%H:%M"))
        if plan[4]:
            self.end_time.set(plan[4].strftime("%H:%M"))
        self.location_box.set(plan[5] or "")
        self.category_box.set(plan[7] or "")
        self.text_description.insert(tk.END, plan[6] or "")
        self.entry_audience.insert(0, plan[8] or "")

    def _save(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название мероприятия обязательно")
            return
        try:
            event_date = self.calendar_date.get_date()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить дату: {e}")
            return
        start_time_str = self.start_time.get()
        end_time_str = self.end_time.get()
        start_time = None
        end_time = None
        try:
            if start_time_str and start_time_str != "00:00":
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except:
            pass
        try:
            if end_time_str and end_time_str != "00:00":
                end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except:
            pass
        location = self.location_box.get() or None
        category = self.category_box.get() or None
        description = self.text_description.get("1.0", tk.END).strip() or None
        audience = self.entry_audience.get().strip() or None

        if self.plan_id:
            success = update_event_plan(self.plan_id, title, event_date, start_time, end_time,
                                        location, description, category, audience)
            if success:
                messagebox.showinfo("Успех", "План обновлён")
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить план")
        else:
            if not self.user_data:
                messagebox.showerror("Ошибка", "Неизвестный пользователь")
                return
            new_id = create_event_plan(title, event_date, start_time, end_time,
                                       location, description, category, audience, self.user_data["id"])
            if new_id:
                messagebox.showinfo("Успех", f"План создан с ID {new_id}")
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать план")