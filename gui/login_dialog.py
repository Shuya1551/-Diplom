"""
Окно авторизации (корневое окно).
После успешного входа уничтожается.
"""

import tkinter as tk
from tkinter import messagebox
from database.user_repository import authenticate_user

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.success = False
        self.user_data = None
        self.root.title("Авторизация")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        tk.Label(root, text="Логин:").pack(pady=5)
        self.entry_username = tk.Entry(root, width=30)
        self.entry_username.pack()

        tk.Label(root, text="Пароль:").pack(pady=5)
        self.entry_password = tk.Entry(root, width=30, show="*")
        self.entry_password.pack()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Войти", command=self.check_auth).pack(side=tk.LEFT, padx=5)
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

    def _cancel(self):
        self.success = False
        self.root.destroy()