"""
Главный модуль приложения «Автоматическая генерация новостей из плана мероприятий».
Запускает окно авторизации, затем главное окно.
"""

import tkinter as tk
from tkinter import messagebox
from database.db_connection import init_connection_pool, close_all_connections
from gui.login_dialog import LoginWindow
from gui.plans_list_window import PlansListWindow
from gui.plan_edit_dialog import PlanEditDialog

class Application:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Генератор новостей - {user_data['username']} ({user_data['role']})")
        self.root.geometry("800x600")

        self.create_menu()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        lbl = tk.Label(
            self.main_frame,
            text=f"Добро пожаловать, {user_data['username']}!\nВаша роль: {user_data['role']}",
            font=("Arial", 14)
        )
        lbl.pack(expand=True)

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # 1. Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.exit_app)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # 2. Планы мероприятий
        plans_menu = tk.Menu(menubar, tearoff=0)
        plans_menu.add_command(label="Список планов", command=self.show_plans_list)
        plans_menu.add_command(label="Новый план", command=self.new_plan)
        menubar.add_cascade(label="Планы", menu=plans_menu)

        # 3. Генерация новостей
        gen_menu = tk.Menu(menubar, tearoff=0)
        gen_menu.add_command(label="Сгенерировать новость", command=self.generate_news)
        menubar.add_cascade(label="Генерация", menu=gen_menu)

        # 4. Отчёты
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Экспорт в Excel", command=self.export_excel)
        reports_menu.add_command(label="Экспорт в Word", command=self.export_word)
        menubar.add_cascade(label="Отчёты", menu=reports_menu)

        # 5. Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menubar)

    def show_plans_list(self):
        PlansListWindow(self.root, self.user_data, refresh_callback=self.refresh_plans_list)

    def new_plan(self):
        dialog = PlanEditDialog(self.root, plan_id=None, user_data=self.user_data)
        self.root.wait_window(dialog.window)
        self.refresh_plans_list()

    def refresh_plans_list(self):
        # метод нужен для колбэка
        pass

    # Заглушки

    def generate_news(self):
        messagebox.showinfo("Генерация", "Окно генерации новости")

    def export_excel(self):
        messagebox.showinfo("Excel", "Экспорт в Excel")

    def export_word(self):
        messagebox.showinfo("Word", "Экспорт в Word")

    def about(self):
        messagebox.showinfo("О программе", "Автор: Головатый И.Н\nГруппа: Идс23Б\nГод: 2026")

    def exit_app(self):
        close_all_connections()
        self.root.destroy()


def main():
    # Инициализация БД
    if not init_connection_pool():
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        return

    # Окно входа
    login_root = tk.Tk()
    login_window = LoginWindow(login_root)
    login_root.mainloop()

    # После закрытия окна входа
    if login_window.success and login_window.user_data:
        # Создаём главное окно
        root = tk.Tk()
        app = Application(root, login_window.user_data)
        root.mainloop()
    else:
        close_all_connections()
        print("Авторизация отменена, выход.")


if __name__ == "__main__":
    main()