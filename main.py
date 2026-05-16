"""
Главный модуль приложения «Автоматическая генерация новостей из плана мероприятий».
"""

import tkinter as tk
from tkinter import messagebox
from database.db_connection import init_connection_pool, close_all_connections
from gui.login_dialog import LoginWindow
from gui.plans_list_window import PlansListWindow
from gui.plan_edit_dialog import PlanEditDialog
from gui.news_view_window import NewsViewWindow
from gui.export_dialog import ExportDialog
from gui.settings_window import SettingsWindow
from gui.admin_window import AdminWindow
from services.gpt_news_generator import GPTNewsGenerator

# Глобальная переменная для генератора (загружается один раз)
_news_generator = None

def get_news_generator():
    global _news_generator
    if _news_generator is None:
        try:
            _news_generator = GPTNewsGenerator()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить модель:\n{str(e)}")
            return None
    return _news_generator

class Application:
    def __init__(self, root, user_data, news_generator):
        self.root = root
        self.user_data = user_data
        self.news_generator = news_generator
        self.root.title(f"Генератор новостей - {user_data['username']} ({user_data['role']})")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)  # при закрытии окна

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
        file_menu.add_command(label="Настройки", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Сменить пользователя", command=self.logout)
        file_menu.add_separator()
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
        gen_menu.add_separator()
        gen_menu.add_command(label="Сохранённые новости", command=self.show_saved_news)
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

        # 6. Администрирование (только для admin)
        if self.user_data.get('role') == 'admin':
            admin_menu = tk.Menu(menubar, tearoff=0)
            admin_menu.add_command(label="Панель администратора", command=self.open_admin_panel)
            menubar.add_cascade(label="Администрирование", menu=admin_menu)

        self.root.config(menu=menubar)

    # ---------- Методы меню ----------
    def show_plans_list(self):
        PlansListWindow(self.root, self.user_data, self.news_generator)

    def new_plan(self):
        PlanEditDialog(self.root, plan_id=None, user_data=self.user_data)

    def generate_news(self):
        self.show_plans_list()  # открывает список, а там уже кнопка генерации

    def show_saved_news(self):
        NewsViewWindow(self.root, self.user_data)

    def export_excel(self):
        ExportDialog(self.root, self.user_data, 'xlsx')

    def export_word(self):
        ExportDialog(self.root, self.user_data, 'docx')

    def open_settings(self):
        SettingsWindow(self.root, self.user_data)

    def open_admin_panel(self):
        AdminWindow(self.root, self.user_data)

    def about(self):
        messagebox.showinfo("О программе", "Автор: Головатый И.Н\nГруппа: Идс23Б\nГод: 2026")

    def logout(self):
        """Выход из текущего пользователя: закрываем главное окно и запускаем авторизацию заново."""
        self.root.destroy()
        run_auth_flow()  # функция внизу

    def exit_app(self):
        close_all_connections()
        self.root.destroy()

# ---------- Функции для управления потоками входа ----------
def run_auth_flow():
    """Создаёт окно входа и, при успехе, запускает главное приложение."""
    login_root = tk.Tk()
    login_window = LoginWindow(login_root)
    login_root.mainloop()

    if login_window.success and login_window.user_data:
        # Загружаем генератор (один раз, кешируется)
        generator = get_news_generator()
        if generator is None:
            close_all_connections()
            return
        root = tk.Tk()
        app = Application(root, login_window.user_data, generator)
        root.mainloop()
    else:
        close_all_connections()
        print("Авторизация отменена, выход.")

def main():
    # Инициализация БД
    if not init_connection_pool():
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        return

    # Запускаем процесс авторизации и приложения
    run_auth_flow()

if __name__ == "__main__":
    main()