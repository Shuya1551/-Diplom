"""
Личный кабинет пользователя: просмотр данных, смена пароля, мои новости, статистика.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
from datetime import datetime
from repositories.user_repository import get_user_by_id, change_password, update_last_login
from repositories.generated_news_repository import get_news_by_user_id
from repositories.log_repository import get_generation_stats  # общая статистика, но можно добавить свою

class ProfileWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.user_id = user_data['id']
        self.window = tk.Toplevel(parent)
        self.window.title(f"Личный кабинет - {user_data['username']}")
        self.window.geometry("750x550")
        self.window.transient(parent)
        self.window.grab_set()

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка "Мои данные"
        self.info_frame = tk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="Мои данные")
        self.create_info_tab()

        # Вкладка "Мои новости"
        self.news_frame = tk.Frame(self.notebook)
        self.notebook.add(self.news_frame, text="Мои новости")
        self.create_news_tab()

        # Вкладка "Статистика"
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")
        self.create_stats_tab()

        btn_close = tk.Button(self.window, text="Закрыть", command=self.window.destroy)
        btn_close.pack(side=tk.BOTTOM, pady=10)

        self.load_data()

    def create_info_tab(self):
        frame = tk.Frame(self.info_frame, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Логин:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.lbl_username = tk.Label(frame, text="", font=("Arial", 10, "bold"))
        self.lbl_username.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lbl_email = tk.Label(frame, text="")
        self.lbl_email.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Роль:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lbl_role = tk.Label(frame, text="")
        self.lbl_role.grid(row=2, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Дата регистрации:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.lbl_created = tk.Label(frame, text="")
        self.lbl_created.grid(row=3, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Последний вход:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.lbl_last_login = tk.Label(frame, text="")
        self.lbl_last_login.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Кнопка смены пароля
        tk.Button(frame, text="Сменить пароль", command=self.change_password_dialog).grid(row=5, column=0, columnspan=2, pady=20)

    def create_news_tab(self):
        # Таблица с новостями пользователя
        columns = ("ID", "Мероприятие", "Дата генерации", "Утверждено", "Рейтинг")
        self.news_tree = ttk.Treeview(self.news_frame, columns=columns, show="headings")
        for col in columns:
            self.news_tree.heading(col, text=col)
            self.news_tree.column(col, width=100 if col=="ID" else 200)
        self.news_tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.news_frame, orient=tk.VERTICAL, command=self.news_tree.yview)
        self.news_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка просмотра текста выбранной новости
        btn_frame = tk.Frame(self.news_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        tk.Button(btn_frame, text="Просмотреть текст", command=self.view_news_text).pack(side=tk.LEFT, padx=5)

        self.load_my_news()

    def create_stats_tab(self):
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.load_stats()

    def load_data(self):
        user_info = get_user_by_id(self.user_id)
        if user_info:
            self.lbl_username.config(text=user_info['username'])
            self.lbl_email.config(text=user_info['email'])
            self.lbl_role.config(text=user_info['role'])
            self.lbl_created.config(text=str(user_info['created_at']) if user_info['created_at'] else "")
            self.lbl_last_login.config(text=str(user_info['last_login']) if user_info['last_login'] else "никогда")

    def change_password_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Смена пароля")
        dialog.geometry("300x200")
        dialog.transient(self.window)
        dialog.grab_set()

        tk.Label(dialog, text="Текущий пароль:").pack(pady=5)
        entry_old = tk.Entry(dialog, show="*", width=25)
        entry_old.pack()

        tk.Label(dialog, text="Новый пароль (мин. 4 символа):").pack(pady=5)
        entry_new = tk.Entry(dialog, show="*", width=25)
        entry_new.pack()

        tk.Label(dialog, text="Подтверждение:").pack(pady=5)
        entry_new2 = tk.Entry(dialog, show="*", width=25)
        entry_new2.pack()

        def save():
            old = entry_old.get()
            new = entry_new.get()
            new2 = entry_new2.get()
            if not old or not new:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            if new != new2:
                messagebox.showerror("Ошибка", "Новые пароли не совпадают")
                return
            if len(new) < 4:
                messagebox.showerror("Ошибка", "Новый пароль слишком короткий (мин. 4 символа)")
                return
            # Проверка текущего пароля
            from repositories.user_repository import authenticate_user
            auth = authenticate_user(self.user_data['username'], old)
            if not auth:
                messagebox.showerror("Ошибка", "Неверный текущий пароль")
                return
            # Хешируем и меняем
            new_hash = bcrypt.hashpw(new.encode(), bcrypt.gensalt()).decode()
            if change_password(self.user_id, new_hash):
                messagebox.showinfo("Успех", "Пароль успешно изменён")
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось сменить пароль")

        tk.Button(dialog, text="Сохранить", command=save).pack(pady=10)
        tk.Button(dialog, text="Отмена", command=dialog.destroy).pack()

    def load_my_news(self):
        for row in self.news_tree.get_children():
            self.news_tree.delete(row)
        news_list = get_news_by_user_id(self.user_id)
        for news in news_list:
            # (id, text, gen_date, approved, rating, plan_title)
            news_id, text, gen_date, approved, rating, plan_title = news
            self.news_tree.insert("", tk.END, values=(
                news_id, plan_title, gen_date, "Да" if approved else "Нет", rating or ""
            ))

    def view_news_text(self):
        selected = self.news_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите новость")
            return
        values = self.news_tree.item(selected[0], "values")
        news_id = values[0]
        # Получим полный текст из БД
        from repositories.generated_news_repository import get_news_by_id
        news = get_news_by_id(news_id)
        if news:
            text = news[1]
            view_win = tk.Toplevel(self.window)
            view_win.title(f"Новость ID {news_id}")
            view_win.geometry("500x400")
            text_area = tk.Text(view_win, wrap=tk.WORD)
            text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_area.insert(tk.END, text)
            text_area.config(state=tk.DISABLED)
            tk.Button(view_win, text="Закрыть", command=view_win.destroy).pack(pady=5)
        else:
            messagebox.showerror("Ошибка", "Новость не найдена")

    def load_stats(self):
        # Статистика пользователя: сколько новостей сгенерировал, успешность генераций
        news_count = len(self.news_tree.get_children())  # уже загружено, но можно пересчитать из БД
        # Лучше запросить отдельно
        from repositories.log_repository import get_generation_stats  # общая, но мы сделаем свою
        # Сделаем простую статистику по логам пользователя
        conn = None
        try:
            from database.db_connection import get_connection, return_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*), SUM(CASE WHEN success THEN 1 ELSE 0 END), AVG(inference_time_ms)
                FROM generation_logs
                WHERE user_id = %s
            """, (self.user_id,))
            row = cur.fetchone()
            total = row[0] or 0
            successful = row[1] or 0
            avg_time = round(row[2], 2) if row[2] else 0
            cur.close()
            text = f"""
=== Ваша статистика ===

Сгенерировано новостей (сохранено в БД): {news_count}
Попыток генерации (всего): {total}
Успешных генераций: {successful}
Процент успеха: {successful/total*100:.1f}% если были попытки
Среднее время генерации: {avg_time} мс

Информация о пользователе:
Логин: {self.user_data['username']}
Роль: {self.user_data['role']}
            """
        except Exception as e:
            text = f"Ошибка загрузки статистики: {e}"
        finally:
            if conn:
                return_connection(conn)
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert(tk.END, text)