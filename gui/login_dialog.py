"""
Окно авторизации с возможностью регистрации новых пользователей (роли user/manager).
"""

import tkinter as tk
from tkinter import messagebox
import bcrypt
from database.db_connection import get_connection, return_connection
from repositories.user_repository import authenticate_user, create_user, get_role_id_by_name

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.success = False
        self.user_data = None
        self.root.title("Авторизация")
        self.root.geometry("320x250")
        self.root.resizable(False, False)

        # Поля входа
        tk.Label(root, text="Логин:").pack(pady=5)
        self.entry_username = tk.Entry(root, width=30)
        self.entry_username.pack()

        tk.Label(root, text="Пароль:").pack(pady=5)
        self.entry_password = tk.Entry(root, width=30, show="*")
        self.entry_password.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Войти", command=self.check_auth).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Регистрация", command=self.open_register).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self._cancel).pack(side=tk.LEFT, padx=5)

        self.root.bind('<Return>', lambda e: self.check_auth())
        self.entry_username.focus()

    def check_auth(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = authenticate_user(username, password)
        if user:
            self.user_data = user
            self.success = True
            self.root.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_register(self):
        """Открывает окно регистрации нового пользователя."""
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Регистрация")
        reg_win.geometry("350x400")
        reg_win.transient(self.root)
        reg_win.grab_set()

        tk.Label(reg_win, text="Логин (уникальный):").pack(pady=5)
        entry_login = tk.Entry(reg_win, width=30)
        entry_login.pack()

        tk.Label(reg_win, text="Email:").pack(pady=5)
        entry_email = tk.Entry(reg_win, width=30)
        entry_email.pack()

        tk.Label(reg_win, text="Пароль:").pack(pady=5)
        entry_pass = tk.Entry(reg_win, width=30, show="*")
        entry_pass.pack()

        tk.Label(reg_win, text="Подтверждение пароля:").pack(pady=5)
        entry_pass2 = tk.Entry(reg_win, width=30, show="*")
        entry_pass2.pack()

        tk.Label(reg_win, text="Роль:").pack(pady=5)
        role_var = tk.StringVar(value="user")
        role_frame = tk.Frame(reg_win)
        role_frame.pack()
        tk.Radiobutton(role_frame, text="Пользователь (user)", variable=role_var, value="user").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(role_frame, text="Менеджер (manager)", variable=role_var, value="manager").pack(side=tk.LEFT, padx=5)
        # admin не предлагаем при регистрации

        def do_register():
            login = entry_login.get().strip()
            email = entry_email.get().strip()
            password = entry_pass.get()
            password2 = entry_pass2.get()
            role_name = role_var.get()

            if not login or not email or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            if password != password2:
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return
            if len(password) < 4:
                messagebox.showerror("Ошибка", "Пароль должен быть не менее 4 символов")
                return

            # Проверка уникальности логина и email
            conn = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE username = %s", (login,))
                if cur.fetchone():
                    messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
                    return
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    messagebox.showerror("Ошибка", "Пользователь с таким email уже существует")
                    return
            finally:
                if conn:
                    return_connection(conn)

            role_id = get_role_id_by_name(role_name)
            if not role_id:
                messagebox.showerror("Ошибка", "Роль не найдена")
                return

            pass_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user_id = create_user(login, pass_hash, email, role_id, is_active=True)
            if user_id:
                messagebox.showinfo("Успех", f"Пользователь {login} зарегистрирован!\nТеперь можете войти.")
                reg_win.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать пользователя. Возможно, проблема с БД.")

        tk.Button(reg_win, text="Зарегистрироваться", command=do_register).pack(pady=15)
        tk.Button(reg_win, text="Отмена", command=reg_win.destroy).pack()

    def _cancel(self):
        self.success = False
        self.root.destroy()