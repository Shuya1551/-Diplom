"""
Главный модуль приложения «Автоматическая генерация новостей из плана мероприятий».
Единое окно с современным дизайном (CustomTkinter).
Навигационная панель: Планы, Генерация, Отчёты. Иконка профиля справа.
"""

import customtkinter as ctk
from tkinter import messagebox, Menu
from datetime import datetime, date, timedelta
from database.db_connection import init_connection_pool, close_all_connections
from repositories.user_repository import authenticate_user, create_user, get_role_id_by_name
from services.gpt_news_generator import GPTNewsGenerator
import bcrypt

# ---------- НАСТРОЙКА ЦВЕТОВОЙ ТЕМЫ ----------
COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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


class LoginFrame(ctk.CTkFrame):
    """Фрейм авторизации и регистрации – карточка фиксированного размера."""
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLOR_BG)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.card = ctk.CTkFrame(self, width=480, height=600, corner_radius=20, fg_color=COLOR_CARD)
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)

        self.top_bar = ctk.CTkFrame(self.card, fg_color="transparent", height=40)
        self.top_bar.pack(fill="x", padx=15, pady=(10, 0))
        self.back_btn = ctk.CTkButton(self.top_bar, text="←", width=30, height=30,
                                      fg_color="transparent", text_color=COLOR_SECONDARY,
                                      font=ctk.CTkFont(size=24), command=self.hide_register)
        self.back_btn.pack(side="left")
        self.back_btn.pack_forget()

        self.content_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.login_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.login_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.login_frame, text="Генератор новостей", font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(pady=(0, 5))
        ctk.CTkLabel(self.login_frame, text="Добро пожаловать", font=ctk.CTkFont(size=18),
                     text_color=COLOR_TEXT).pack(pady=(0, 5))
        ctk.CTkLabel(self.login_frame, text="Войдите в свой аккаунт", font=ctk.CTkFont(size=12),
                     text_color=COLOR_TEXT).pack(pady=(0, 15))

        ctk.CTkLabel(self.login_frame, text="Email / Логин", text_color=COLOR_TEXT).pack(anchor="w")
        self.entry_login = ctk.CTkEntry(self.login_frame, placeholder_text="Введите логин или email",
                                        fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.entry_login.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.login_frame, text="Пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.entry_password = ctk.CTkEntry(self.login_frame, placeholder_text="••••••••", show="*",
                                           fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.entry_password.pack(fill="x", pady=(5, 10))

        self.remember_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.login_frame, text="Запомнить меня", variable=self.remember_var,
                        fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY).pack(anchor="w", pady=(0, 10))

        self.login_btn = ctk.CTkButton(self.login_frame, text="ВОЙТИ", command=self.do_login,
                                       height=40, fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.login_btn.pack(fill="x", pady=(10, 5))

        self.register_label = ctk.CTkLabel(self.login_frame, text="Нет аккаунта? Зарегистрироваться",
                                           cursor="hand2", text_color=COLOR_SECONDARY)
        self.register_label.pack(pady=10)
        self.register_label.bind("<Button-1>", lambda e: self.show_register())

        self.register_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.entry_password.bind("<Return>", lambda e: self.do_login())

    def show_register(self):
        self.login_frame.pack_forget()
        self.back_btn.pack(side="left")
        for widget in self.register_frame.winfo_children():
            widget.destroy()
        self.register_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.register_frame, text="Регистрация", font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(pady=(0, 10))

        ctk.CTkLabel(self.register_frame, text="Логин", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_login = ctk.CTkEntry(self.register_frame, placeholder_text="Придумайте логин",
                                      fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_login.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Email", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_email = ctk.CTkEntry(self.register_frame, placeholder_text="your@email.com",
                                      fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_email.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_password = ctk.CTkEntry(self.register_frame, show="*", placeholder_text="минимум 4 символа",
                                         fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_password.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Подтвердите пароль", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_password2 = ctk.CTkEntry(self.register_frame, show="*", fg_color="#3A3450", border_color=COLOR_PRIMARY)
        self.reg_password2.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(self.register_frame, text="Роль", text_color=COLOR_TEXT).pack(anchor="w")
        self.reg_role = ctk.CTkComboBox(self.register_frame, values=["user", "manager"], state="readonly",
                                        fg_color="#3A3450", border_color=COLOR_PRIMARY, button_color=COLOR_PRIMARY)
        self.reg_role.set("user")
        self.reg_role.pack(fill="x", pady=(5, 10))

        self.register_btn = ctk.CTkButton(self.register_frame, text="Зарегистрироваться", command=self.do_register,
                                          fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
        self.register_btn.pack(pady=(15, 5))

    def hide_register(self):
        self.register_frame.pack_forget()
        self.back_btn.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def do_login(self):
        login = self.entry_login.get().strip()
        password = self.entry_password.get()
        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин/email и пароль")
            return
        user = authenticate_user(login, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин/email или пароль")

    def do_register(self):
        login = self.reg_login.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        password2 = self.reg_password2.get()
        role_name = self.reg_role.get()

        if not login or not email or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        if password != password2:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        if len(password) < 4:
            messagebox.showerror("Ошибка", "Пароль должен быть не менее 4 символов")
            return

        role_id = get_role_id_by_name(role_name)
        if not role_id:
            messagebox.showerror("Ошибка", "Роль не найдена")
            return

        pass_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_id = create_user(login, pass_hash, email, role_id, is_active=True)
        if user_id:
            messagebox.showinfo("Успех", f"Пользователь {login} зарегистрирован! Теперь войдите.")
            self.hide_register()
        else:
            messagebox.showerror("Ошибка", "Пользователь с таким логином или email уже существует")


class MainAppFrame(ctk.CTkFrame):
    """Главная страница с дашбордом и навигационной панелью."""
    def __init__(self, parent, user_data, news_generator):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.pack(fill="both", expand=True)

        self.main_canvas = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # ------ ВЕРХНЯЯ ПАНЕЛЬ (логотип + иконка профиля) ------
        self.top_nav = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.top_nav.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.top_nav, text="Генератор новостей",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(side="left")

        # Кнопка профиля с выпадающим меню
        self.profile_btn = ctk.CTkButton(self.top_nav, text="👤", width=40, height=40,
                                         fg_color="transparent", text_color=COLOR_TEXT,
                                         font=ctk.CTkFont(size=20),
                                         command=lambda: self.show_profile_menu(self.profile_btn))
        self.profile_btn.pack(side="right", padx=(0, 5))

        # ------ НАВИГАЦИОННАЯ ПАНЕЛЬ (только Планы, Генерация, Отчёты) ------
        self.nav_frame = ctk.CTkFrame(self.main_canvas, fg_color=COLOR_CARD, corner_radius=10)
        self.nav_frame.pack(fill="x", pady=(0, 20))

        nav_buttons = [
            ("Планы", self.show_plans_menu),
            ("Генерация", self.show_generation_menu),
            ("Отчёты", self.show_reports_menu)
        ]

        for i, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(self.nav_frame, text=text, command=command,
                                fg_color="transparent", text_color=COLOR_TEXT,
                                hover_color="#3A3450", width=100)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.nav_frame.grid_columnconfigure(i, weight=1)

        # ------ ОСТАЛЬНОЙ КОНТЕНТ (дашборд) ------
        self.grid_frame = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, pady=(0, 20))
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)

        # Левый блок: Ближайшие планы
        self.upcoming_frame = ctk.CTkFrame(self.grid_frame, fg_color=COLOR_CARD, corner_radius=15)
        self.upcoming_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        ctk.CTkLabel(self.upcoming_frame, text="📋 Ближайшие планы",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))

        self.upcoming_list_frame = ctk.CTkFrame(self.upcoming_frame, fg_color="transparent")
        self.upcoming_list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Правый блок: Быстрая генерация
        self.quick_gen_frame = ctk.CTkFrame(self.grid_frame, fg_color=COLOR_CARD, corner_radius=15)
        self.quick_gen_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        ctk.CTkLabel(self.quick_gen_frame, text="✨ Быстрая генерация",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))

        self.quick_plan_combo = ctk.CTkComboBox(self.quick_gen_frame, values=["Загрузка..."],
                                                state="readonly", fg_color="#3A3450", button_color=COLOR_PRIMARY)
        self.quick_plan_combo.pack(fill="x", padx=15, pady=(5, 10))

        self.generate_btn = ctk.CTkButton(self.quick_gen_frame, text="🚀 СГЕНЕРИРОВАТЬ НОВОСТЬ",
                                          command=self.quick_generate, height=40,
                                          fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY,
                                          font=ctk.CTkFont(size=14, weight="bold"))
        self.generate_btn.pack(fill="x", padx=15, pady=10)

        # Нижний блок: Последние новости
        self.recent_frame = ctk.CTkFrame(self.main_canvas, fg_color=COLOR_CARD, corner_radius=15)
        self.recent_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(self.recent_frame, text="🗞️ Последние сгенерированные новости",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))

        self.recent_news_list = ctk.CTkScrollableFrame(self.recent_frame, fg_color="transparent", height=150)
        self.recent_news_list.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        all_news_btn = ctk.CTkButton(self.recent_frame, text="Все новости →", command=self.show_saved_news,
                                     fg_color="transparent", text_color=COLOR_SECONDARY, hover_color="#3A3450")
        all_news_btn.pack(anchor="e", padx=15, pady=(0, 15))

        # Статусная строка
        self.status_bar = ctk.CTkFrame(self.main_canvas, fg_color="transparent")
        self.status_bar.pack(fill="x", pady=(10, 0))

        self.status_label = ctk.CTkLabel(self.status_bar, text="🟢 Нейросеть активна и готова к работе",
                                         font=ctk.CTkFont(size=12), text_color=COLOR_SECONDARY)
        self.status_label.pack(side="left")

        self.about_label = ctk.CTkLabel(self.status_bar, text="О программе",
                                        font=ctk.CTkFont(size=12, underline=True),
                                        text_color=COLOR_GRAY, cursor="hand2")
        self.about_label.pack(side="right", padx=(0, 10))
        self.about_label.bind("<Button-1>", lambda e: self.about())

        # Загружаем данные
        self.load_upcoming_plans()
        self.load_recent_news()
        self.load_plan_list_for_quick()

    # ---------- ВЫПАДАЮЩИЕ МЕНЮ ДЛЯ КНОПОК НАВИГАЦИИ ----------
    def show_plans_menu(self):
        menu = Menu(self.parent, tearoff=0, bg=COLOR_CARD, fg=COLOR_TEXT, activebackground=COLOR_SECONDARY)
        menu.add_command(label="Список планов", command=self.show_plans_list)
        menu.add_command(label="Новый план", command=self.new_plan)
        btn = self.nav_frame.winfo_children()[0]  # кнопка "Планы"
        self._show_menu(menu, btn)

    def show_generation_menu(self):
        menu = Menu(self.parent, tearoff=0, bg=COLOR_CARD, fg=COLOR_TEXT, activebackground=COLOR_SECONDARY)
        menu.add_command(label="Сгенерировать новость", command=self.generate_news)
        menu.add_command(label="Сохранённые новости", command=self.show_saved_news)
        btn = self.nav_frame.winfo_children()[1]  # кнопка "Генерация"
        self._show_menu(menu, btn)

    def show_reports_menu(self):
        menu = Menu(self.parent, tearoff=0, bg=COLOR_CARD, fg=COLOR_TEXT, activebackground=COLOR_SECONDARY)
        menu.add_command(label="Экспорт в Excel", command=self.export_excel)
        menu.add_command(label="Экспорт в Word", command=self.export_word)
        btn = self.nav_frame.winfo_children()[2]  # кнопка "Отчёты"
        self._show_menu(menu, btn)

    def show_profile_menu(self, source_widget):
        """Показывает меню для иконки профиля."""
        menu = Menu(self.parent, tearoff=0, bg=COLOR_CARD, fg=COLOR_TEXT, activebackground=COLOR_SECONDARY)
        menu.add_command(label="Личный кабинет", command=self.open_profile)
        menu.add_command(label="Настройки", command=self.open_settings)
        menu.add_separator()
        menu.add_command(label="Выйти из профиля", command=self.logout)
        menu.add_separator()
        menu.add_command(label="Выйти из приложения", command=self.exit_app)
        self._show_menu(menu, source_widget)

    def _show_menu(self, menu, widget):
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        menu.post(x, y)

    # ---------- ЗАГРУЗКА ДАННЫХ ДЛЯ ДАШБОРДА ----------
    def load_upcoming_plans(self):
        from repositories.event_plan_repository import get_all_event_plans
        for widget in self.upcoming_list_frame.winfo_children():
            widget.destroy()
        all_plans = get_all_event_plans()
        today = date.today()
        future_limit = today + timedelta(days=14)
        upcoming = []
        for plan in all_plans:
            plan_date = plan[2] if len(plan) > 2 and plan[2] else None
            if plan_date and isinstance(plan_date, (date, datetime)):
                if isinstance(plan_date, datetime):
                    plan_date = plan_date.date()
                if today <= plan_date <= future_limit:
                    upcoming.append((plan_date, plan[1], plan[0]))
        upcoming.sort(key=lambda x: x[0])
        if not upcoming:
            lbl = ctk.CTkLabel(self.upcoming_list_frame, text="Нет запланированных мероприятий на ближайшие 14 дней",
                               text_color=COLOR_TEXT)
            lbl.pack(anchor="w", pady=2)
        else:
            for plan_date, title, _ in upcoming[:5]:
                lbl = ctk.CTkLabel(self.upcoming_list_frame, text=f"• {title} ({plan_date.strftime('%d.%m.%Y')})",
                                   text_color=COLOR_TEXT, anchor="w")
                lbl.pack(anchor="w", pady=2)

    def load_recent_news(self):
        from repositories.generated_news_repository import get_recent_news
        for widget in self.recent_news_list.winfo_children():
            widget.destroy()
        news_list = get_recent_news(limit=5)
        if not news_list:
            lbl = ctk.CTkLabel(self.recent_news_list, text="Нет сгенерированных новостей",
                               text_color=COLOR_TEXT)
            lbl.pack(anchor="w", pady=2)
        else:
            for _, text, gen_date, _ in news_list:
                short_text = text[:100] + "..." if len(text) > 100 else text
                lbl = ctk.CTkLabel(self.recent_news_list, text=f"• {short_text} ({gen_date.strftime('%d.%m.%Y')})",
                                   text_color=COLOR_TEXT, anchor="w")
                lbl.pack(anchor="w", pady=2)

    def load_plan_list_for_quick(self):
        from repositories.event_plan_repository import get_all_event_plans
        plans = get_all_event_plans()
        if not plans:
            self.quick_plan_combo.configure(values=["Нет доступных планов"])
            self.quick_plan_combo.set("Нет доступных планов")
            return
        plan_display = [f"{p[0]} - {p[1]} ({p[2]})" for p in plans]
        self.quick_plan_combo.configure(values=plan_display)
        self.quick_plan_combo.set(plan_display[0])

    def quick_generate(self):
        selected = self.quick_plan_combo.get()
        if not selected or selected == "Нет доступных планов":
            messagebox.showwarning("Предупреждение", "Нет доступных планов для генерации")
            return
        try:
            plan_id = int(selected.split(" - ")[0])
        except:
            messagebox.showerror("Ошибка", "Не удалось определить ID плана")
            return
        from gui.generation_dialog import GenerationDialog
        GenerationDialog(self.parent, plan_id, self.user_data, self.news_generator)

    # ---------- ОБРАБОТЧИКИ ДЕЙСТВИЙ ----------
    def show_plans_list(self):
        from gui.plans_list_window import PlansListWindow
        PlansListWindow(self.parent, self.user_data, self.news_generator)

    def new_plan(self):
        from gui.plan_edit_dialog import PlanEditDialog
        PlanEditDialog(self.parent, plan_id=None, user_data=self.user_data)

    def generate_news(self):
        self.show_plans_list()

    def show_saved_news(self):
        from gui.news_view_window import NewsViewWindow
        NewsViewWindow(self.parent, self.user_data)

    def export_excel(self):
        from gui.export_dialog import ExportDialog
        ExportDialog(self.parent, self.user_data, 'xlsx')

    def export_word(self):
        from gui.export_dialog import ExportDialog
        ExportDialog(self.parent, self.user_data, 'docx')

    def open_settings(self):
        from gui.settings_window import SettingsWindow
        SettingsWindow(self.parent, self.user_data)

    def open_admin_panel(self):
        from gui.admin_window import AdminWindow
        AdminWindow(self.parent, self.user_data)

    def open_profile(self):
        from gui.profile_window import ProfileWindow
        ProfileWindow(self.parent, self.user_data)

    def about(self):
        messagebox.showinfo("О программе", "Автор: Головатый И.Н\nГруппа: Идс23Б\nГод: 2026")

    def logout(self):
        self.destroy()
        self.parent.show_login()

    def exit_app(self):
        close_all_connections()
        self.parent.quit()


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Генератор новостей мероприятий")
        self.geometry("520x670")
        self.minsize(480, 600)
        self.resizable(True, True)
        self.configure(fg_color=COLOR_BG)

        if not init_connection_pool():
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            self.destroy()
            return

        self.news_generator = get_news_generator()
        if self.news_generator is None:
            self.destroy()
            return

        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self.on_login_success)
        self.current_frame.pack(fill="both", expand=True)
        self.geometry("520x670")

    def on_login_success(self, user_data):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, user_data, self.news_generator)
        self.current_frame.pack(fill="both", expand=True)
        self.geometry("1000x700")

    def on_closing(self):
        close_all_connections()
        self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()