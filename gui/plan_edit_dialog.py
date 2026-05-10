"""
Диалоговое окно для добавления/редактирования плана мероприятия.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from repositories.event_plan_repository import get_event_plan_by_id, create_event_plan, update_event_plan

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
        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):*").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_date = tk.Entry(frame, width=20)
        self.entry_date.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        tk.Label(frame, text="Время (ЧЧ:ММ:СС):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_time = tk.Entry(frame, width=20)
        self.entry_time.grid(row=row, column=1, sticky=tk.W, pady=5)

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
            self.entry_date.insert(0, str(plan[2]))
            self.entry_time.insert(0, str(plan[3]) if plan[3] else "")
            self.entry_location.insert(0, plan[4] or "")
            self.text_description.insert(tk.END, plan[5] or "")
            self.entry_speaker.insert(0, plan[6] or "")
            self.entry_audience.insert(0, plan[7] or "")

    def save(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название обязательно")
            return
        date_str = self.entry_date.get().strip()
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return
        time_str = self.entry_time.get().strip()
        event_time = None
        if time_str:
            try:
                event_time = datetime.strptime(time_str, "%H:%M:%S").time()
            except:
                messagebox.showerror("Ошибка", "Время должно быть в формате ЧЧ:ММ:СС")
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