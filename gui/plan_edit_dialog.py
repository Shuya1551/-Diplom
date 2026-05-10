"""
Диалоговое окно для добавления/редактирования плана мероприятия.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from repositories.event_plan_repository import get_event_plan_by_id, create_event_plan, update_event_plan
from tkcalendar import DateEntry

class PlanEditDialog:
    def __init__(self, parent, plan_id=None, user_data=None):
        self.parent = parent
        self.plan_id = plan_id
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Редактирование плана" if plan_id else "Новый план")
        self.window.geometry("500x550")
        self.window.transient(parent)
        self.window.grab_set()

        frame = tk.Frame(self.window, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Поля
        row = 0
        tk.Label(frame, text="Название мероприятия:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_title = tk.Entry(frame, width=50)
        self.entry_title.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Дата:*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.calendar_date = DateEntry(
            frame, 
            width=17, 
            background='darkblue', 
            foreground='white', 
            borderwidth=2,
            locale='ru_RU',          
            date_pattern='yyyy-mm-dd'
        )
        self.calendar_date.grid(row=row, column=1, sticky=tk.W, pady=5) # Добавили sticky=tk.W

        row += 1
        tk.Label(frame, text="Время (часы:минуты):").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        # Создаём фрейм для размещения двух Spinbox рядом
        time_frame = tk.Frame(frame)
        time_frame.grid(row=row, column=1, sticky=tk.W, pady=5)

        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")

        self.spin_hour = tk.Spinbox(
            time_frame, 
            from_=0, to=23,       
            textvariable=self.hour_var, 
            width=3, 
            format="%02.0f",    
            wrap=True             
        )
        self.spin_hour.pack(side=tk.LEFT)

        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

        self.spin_minute = tk.Spinbox(
            time_frame, 
            from_=0, to=59,
            textvariable=self.minute_var, 
            width=3,
            format="%02.0f",
            wrap=True
        )
        self.spin_minute.pack(side=tk.LEFT)

        row += 1
        tk.Label(frame, text="Место проведения:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_location = tk.Entry(frame, width=50)
        self.entry_location.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Описание:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.text_description = tk.Text(frame, height=5, width=40)
        self.text_description.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Спикер(ы):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_speaker = tk.Entry(frame, width=50)
        self.entry_speaker.grid(row=row, column=1, pady=5, padx=5)

        row += 1
        tk.Label(frame, text="Аудитория (категория):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_audience = tk.Entry(frame, width=30)
        self.entry_audience.grid(row=row, column=1, sticky=tk.W, pady=5)

        # Кнопки
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=row+1, column=0, columnspan=2, pady=20)
        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        if plan_id:
            self.load_data()

    def load_data(self):
        plan = get_event_plan_by_id(self.plan_id)
        if plan:
            # plan: (id, title, date, time, location, description, speaker, audience, created_by, created_at)

            self.entry_title.insert(0, plan[1])
        
            if plan[2]:
                self.calendar_date.set_date(plan[2])
        
            if plan[3]:
                time_str = str(plan[3])
                time_parts = time_str.split(':')
                if len(time_parts) >= 2:
                    self.hour_var.set(time_parts[0].zfill(2))
                    self.minute_var.set(time_parts[1].zfill(2))

            self.entry_location.insert(0, plan[4] or "")
            self.text_description.insert(tk.END, plan[5] or "")
            self.entry_speaker.insert(0, plan[6] or "")
            self.entry_audience.insert(0, plan[7] or "")

    def save(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название обязательно")
            return

        try:
            event_date = self.calendar_date.get_date()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить дату: {e}")
            return

        event_time = None

        if self.hour_var.get() and self.minute_var.get():
            try:
                hour = int(self.hour_var.get())
                minute = int(self.minute_var.get())
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    event_time = datetime.strptime(f"{hour:02d}:{minute:02d}:00", "%H:%M:%S").time()
                else:
                    messagebox.showerror("Ошибка", "Некорректные часы (0-23) или минуты (0-59).")
                    return
            except ValueError:
                messagebox.showerror("Ошибка", "Введите числовые значения для часов и минут.")
                return

        location = self.entry_location.get().strip() or None
        description = self.text_description.get("1.0", tk.END).strip() or None
        speaker = self.entry_speaker.get().strip() or None
        audience = self.entry_audience.get().strip() or None

        if self.plan_id:
            success = update_event_plan(self.plan_id, title, event_date, event_time, location, description, speaker, audience)
            if success:
                messagebox.showinfo("Успех", "План обновлён")
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить план")
        else:
            if not self.user_data:
                messagebox.showerror("Ошибка", "Неизвестный пользователь")
                return
            new_id = create_event_plan(title, event_date, event_time, location, description, speaker, audience, self.user_data["id"])
            if new_id:
                messagebox.showinfo("Успех", f"План создан с ID {new_id}")
                self.window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать план")