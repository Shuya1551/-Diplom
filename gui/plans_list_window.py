"""
Окно списка планов мероприятий.
Отображает таблицу, позволяет редактировать, удалять, генерировать новости.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from repositories.event_plan_repository import get_all_event_plans, delete_event_plan
from gui.plan_edit_dialog import PlanEditDialog

class PlansListWindow:
    def __init__(self, parent, user_data, refresh_callback=None):
        self.parent = parent
        self.user_data = user_data
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Список планов мероприятий")
        self.window.geometry("900x500")
        self.window.transient(parent)
        self.window.grab_set()

        # Таблица
        self.tree = ttk.Treeview(self.window, columns=("ID", "Название", "Дата", "Время", "Место", "Спикер"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Время", text="Время")
        self.tree.heading("Место", text="Место")
        self.tree.heading("Спикер", text="Спикер")
        self.tree.column("ID", width=40)
        self.tree.column("Название", width=200)
        self.tree.column("Дата", width=100)
        self.tree.column("Время", width=80)
        self.tree.column("Место", width=150)
        self.tree.column("Спикер", width=150)

        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Редактировать", command=self.edit_plan).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_plan).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сгенерировать новость", command=self.generate_news).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Закрыть", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

        self.load_data()

    def load_data(self):
        """Загружает данные из БД в таблицу."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        plans = get_all_event_plans()
        for plan in plans:
            # plan: (id, title, event_date, event_time, location, description, speaker, audience, created_by, created_at)
            self.tree.insert("", tk.END, values=(
                plan[0], plan[1], plan[2], str(plan[3]) if plan[3] else "", plan[4], plan[6]
            ))

    def get_selected_plan_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите план из списка")
            return None
        values = self.tree.item(selected[0], "values")
        return values[0]  # ID

    def edit_plan(self):
        plan_id = self.get_selected_plan_id()
        if plan_id:
            dialog = PlanEditDialog(self.window, plan_id, self.user_data)
            self.window.wait_window(dialog.window)
            self.load_data()
            if self.refresh_callback:
                self.refresh_callback()

    def delete_plan(self):
        plan_id = self.get_selected_plan_id()
        if plan_id:
            if messagebox.askyesno("Подтверждение", "Удалить выбранный план?"):
                delete_event_plan(plan_id)
                self.load_data()
                if self.refresh_callback:
                    self.refresh_callback()

    def generate_news(self):
        plan_id = self.get_selected_plan_id()
        if plan_id:
            # Пока заглушка
            messagebox.showinfo("Генерация", f"Будет сгенерирована новость для плана ID {plan_id}")