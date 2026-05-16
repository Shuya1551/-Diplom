"""
Панель администратора: управление пользователями, просмотр логов, статистика.
Доступна только пользователям с ролью admin.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from repositories.user_repository import (
    get_all_users, create_user, update_user, delete_user,
    change_password, get_roles
)
from repositories.log_repository import get_all_generation_logs, get_generation_stats
from repositories.settings_repository import get_setting

class AdminWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.current_admin = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Панель администратора")
        self.window.geometry("1000x600")
        self.window.transient(parent)
        self.window.grab_set()

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка "Пользователи"
        self.users_frame = tk.Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Пользователи")
        self.create_users_tab()

        # Вкладка "Логи генерации"
        self.logs_frame = tk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Логи генерации")
        self.create_logs_tab()

        # Вкладка "Статистика"
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")
        self.create_stats_tab()

        # Кнопка закрытия
        btn_close = tk.Button(self.window, text="Закрыть", command=self.window.destroy)
        btn_close.pack(side=tk.BOTTOM, pady=10)

    # ------------------ Вкладка "Пользователи" ------------------
    def create_users_tab(self):
        # Таблица пользователей
        self.user_tree = ttk.Treeview(self.users_frame, columns=("ID", "Логин", "Email", "Роль", "Активен", "Создан", "Последний вход"), show="headings")
        for col in ("ID", "Логин", "Email", "Роль", "Активен", "Создан", "Последний вход"):
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100 if col=="ID" else 150)
        self.user_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.users_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Панель кнопок
        btn_frame = tk.Frame(self.users_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Добавить", command=self.add_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Сбросить пароль", command=self.reset_password).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_users).pack(side=tk.LEFT, padx=5)

        self.load_users()

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        users = get_all_users()
        for user in users:
            # (id, username, email, role, is_active, created_at, last_login)
            self.user_tree.insert("", tk.END, values=(
                user[0], user[1], user[2], user[3], "Да" if user[4] else "Нет", user[5], user[6] or ""
            ), tags=(user[0],))

    def get_selected_user_id(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя")
            return None
        values = self.user_tree.item(selected[0], "values")
        return values[0]

    def add_user(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавление пользователя")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Логин:").pack(pady=5)
        entry_login = tk.Entry(dialog, width=30)
        entry_login.pack()

        tk.Label(dialog, text="Email:").pack(pady=5)
        entry_email = tk.Entry(dialog, width=30)
        entry_email.pack()

        tk.Label(dialog, text="Пароль:").pack(pady=5)
        entry_pass = tk.Entry(dialog, width=30, show="*")
        entry_pass.pack()

        tk.Label(dialog, text="Роль:").pack(pady=5)
        roles = get_roles()
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(dialog, textvariable=role_var, values=[r[1] for r in roles], width=20)
        role_combo.pack()
        if roles:
            role_combo.current(0)

        def save():
            login = entry_login.get().strip()
            email = entry_email.get().strip()
            password = entry_pass.get()
            role_name = role_var.get()
            if not login or not email or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            role_id = next((r[0] for r in roles if r[1] == role_name), None)
            if not role_id:
                messagebox.showerror("Ошибка", "Роль не выбрана")
                return
            pass_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_id = create_user(login, pass_hash, email, role_id, True)
            if new_id:
                messagebox.showinfo("Успех", f"Пользователь {login} создан")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя")

        tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def edit_user(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            return
        # Получаем текущие данные пользователя
        users = get_all_users()
        user_data = next((u for u in users if u[0] == int(user_id)), None)
        if not user_data:
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Редактирование пользователя")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Email:").pack(pady=5)
        entry_email = tk.Entry(dialog, width=30)
        entry_email.insert(0, user_data[2])
        entry_email.pack()

        tk.Label(dialog, text="Активен:").pack(pady=5)
        active_var = tk.BooleanVar(value=user_data[4])
        tk.Checkbutton(dialog, text="Да", variable=active_var).pack()

        tk.Label(dialog, text="Роль:").pack(pady=5)
        roles = get_roles()
        role_var = tk.StringVar(value=user_data[3])
        role_combo = ttk.Combobox(dialog, textvariable=role_var, values=[r[1] for r in roles], width=20)
        role_combo.pack()

        def save():
            email = entry_email.get().strip()
            is_active = active_var.get()
            role_name = role_var.get()
            role_id = next((r[0] for r in roles if r[1] == role_name), None)
            if not email or role_id is None:
                messagebox.showerror("Ошибка", "Заполните поля")
                return
            success = update_user(user_id, email=email, role_id=role_id, is_active=is_active)
            if success:
                messagebox.showinfo("Успех", "Данные обновлены")
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить")
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def reset_password(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Сброс пароля")
        dialog.geometry("300x150")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Новый пароль:").pack(pady=5)
        entry_pass = tk.Entry(dialog, show="*", width=20)
        entry_pass.pack()

        def save():
            new_pass = entry_pass.get()
            if not new_pass:
                messagebox.showerror("Ошибка", "Введите пароль")
                return
            pass_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
            if change_password(user_id, pass_hash):
                messagebox.showinfo("Успех", "Пароль изменён")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось сменить пароль")
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            return
        if int(user_id) == self.current_admin['id']:
            messagebox.showerror("Ошибка", "Нельзя удалить самого себя")
            return
        if messagebox.askyesno("Подтверждение", "Удалить пользователя?"):
            if delete_user(user_id):
                messagebox.showinfo("Успех", "Пользователь удалён")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить")

    # ------------------ Вкладка "Логи генерации" ------------------
    def create_logs_tab(self):
        self.log_tree = ttk.Treeview(self.logs_frame, columns=("ID", "Время", "Пользователь", "Мероприятие", "Успех", "Время, мс", "Ошибка"), show="headings")
        for col in ("ID", "Время", "Пользователь", "Мероприятие", "Успех", "Время, мс", "Ошибка"):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=80 if col=="ID" else 150)
        self.log_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.logs_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self.logs_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_logs).pack(side=tk.LEFT, padx=5)

        self.load_logs()

    def load_logs(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        logs = get_all_generation_logs(limit=200)
        for log in logs:
            # (id, timestamp, username, event_title, success, inference_time_ms, error_message)
            self.log_tree.insert("", tk.END, values=(
                log[0], log[1], log[2] or "-", log[3] or "-", "Да" if log[4] else "Нет", log[5] or "-", (log[6] or "")[:50]
            ))

    # ------------------ Вкладка "Статистика" ------------------
    def create_stats_tab(self):
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.load_stats()
        tk.Button(self.stats_frame, text="Обновить статистику", command=self.load_stats).pack(pady=5)

    def load_stats(self):
        stats = get_generation_stats()
        users_count = len(get_all_users())
        from repositories.generated_news_repository import get_all_generated_news
        all_news = get_all_generated_news()
        news_count = len(all_news)

        # Безопасное вычисление процента
        if stats['total'] > 0:
            percent_success = stats['successful'] / stats['total'] * 100
            percent_str = f"{percent_success:.1f}%"
        else:
            percent_str = "нет данных"

        text = f"""
=== ОБЩАЯ СТАТИСТИКА ===

Пользователей в системе: {users_count}
Сгенерированных новостей: {news_count}

=== ГЕНЕРАЦИИ (логи) ===

Всего попыток генерации: {stats['total']}
Успешных: {stats['successful']}
Процент успеха: {percent_str}
Среднее время генерации: {stats['avg_time_ms']} мс

=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===

Версия приложения: 1.0
Текущий администратор: {self.current_admin['username']}
    """
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, text)