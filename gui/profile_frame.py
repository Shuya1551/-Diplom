"""
Фрейм личного кабинета: информация о пользователе, свои новости, смена пароля.
"""

import customtkinter as ctk
from functools import partial

from repositories.user_repository import get_user_by_id, change_password
from repositories.generated_news_repository import get_news_by_user_id
from utils import show_centered_dialog
import bcrypt

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class ProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.pack(fill="both", expand=True)

        # Верхняя панель
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← На главную", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Личный кабинет",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        # Основной скролл
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=10)

        # Блок информации о пользователе
        self.info_frame = ctk.CTkFrame(self.scrollable, fg_color=COLOR_CARD, corner_radius=15)
        self.info_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self.info_frame, text="👤 Информация о пользователе",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))

        self.load_user_info()

        change_pwd_btn = ctk.CTkButton(self.info_frame, text="🔑 Сменить пароль", command=self.change_password,
                                       fg_color="transparent", hover_color="#3A3450", width=150)
        change_pwd_btn.pack(anchor="w", padx=15, pady=(5, 15))

        # Блок своих новостей
        news_frame = ctk.CTkFrame(self.scrollable, fg_color=COLOR_CARD, corner_radius=15)
        news_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(news_frame, text="📰 Мои сгенерированные новости",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY).pack(anchor="w", padx=15, pady=(15, 5))

        self.news_list = ctk.CTkScrollableFrame(news_frame, fg_color="transparent", height=300)
        self.news_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.load_my_news()

    def load_user_info(self):
        user = get_user_by_id(self.user_data['id'])
        if not user:
            return
        # user – словарь с ключами: id, username, email, role, is_active, created_at, last_login
        info_text = f"Логин: {user['username']}\nEmail: {user['email']}\nРоль: {user['role']}\nЗарегистрирован: {user['created_at']}\nПоследний вход: {user['last_login'] or 'никогда'}"
        info_label = ctk.CTkLabel(self.info_frame, text=info_text, font=ctk.CTkFont(size=13),
                                  text_color=COLOR_TEXT, justify="left", anchor="w")
        info_label.pack(anchor="w", padx=15, pady=5)

    def load_my_news(self):
        for widget in self.news_list.winfo_children():
            widget.destroy()
        news_list = get_news_by_user_id(self.user_data['id'])
        if not news_list:
            lbl = ctk.CTkLabel(self.news_list, text="Нет сгенерированных новостей",
                               text_color=COLOR_GRAY)
            lbl.pack(anchor="w", pady=5)
            return
        for news in news_list:
            # news: (id, text, gen_date, approved, rating, plan_title)
            news_id, text, gen_date, approved, rating, plan_title = news
            card = ctk.CTkFrame(self.news_list, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=10)

            status_text = "✅ Утверждена" if approved else "🟡 Не утверждена"
            header = f"{gen_date} | {status_text} | Рейтинг: {rating or 'нет'} | План: {plan_title}"
            ctk.CTkLabel(info_frame, text=header, font=ctk.CTkFont(size=12), text_color=COLOR_GRAY).pack(anchor="w")
            short_text = text[:150] + "..." if len(text) > 150 else text
            ctk.CTkLabel(info_frame, text=short_text, font=ctk.CTkFont(size=13),
                         text_color=COLOR_TEXT, anchor="w", justify="left", wraplength=500).pack(anchor="w", pady=(5, 0))

            view_btn = ctk.CTkButton(card, text="👁️ Просмотреть", width=100,
                                     command=partial(self.view_news, text, news_id))
            view_btn.pack(side="right", padx=10, pady=10)

    def view_news(self, text, news_id):
        self.parent.switch_to_frame("news_view", news_id=news_id, news_text=text,
                                    on_back_callback=self.return_to_profile)

    def return_to_profile(self):
        self.parent.switch_to_frame("profile")

    def change_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Смена пароля")
        dialog.geometry("350x250")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Старый пароль:", font=ctk.CTkFont(size=13)).pack(pady=5)
        old_pass = ctk.CTkEntry(dialog, show="*", width=250)
        old_pass.pack(pady=5)

        ctk.CTkLabel(dialog, text="Новый пароль:", font=ctk.CTkFont(size=13)).pack(pady=5)
        new_pass = ctk.CTkEntry(dialog, show="*", width=250)
        new_pass.pack(pady=5)

        ctk.CTkLabel(dialog, text="Подтверждение:", font=ctk.CTkFont(size=13)).pack(pady=5)
        confirm_pass = ctk.CTkEntry(dialog, show="*", width=250)
        confirm_pass.pack(pady=5)

        def do_change():
            old = old_pass.get()
            new = new_pass.get()
            confirm = confirm_pass.get()
            if not old or not new:
                show_centered_dialog(dialog, "Ошибка", "Заполните все поля", "error")
                return
            if new != confirm:
                show_centered_dialog(dialog, "Ошибка", "Новые пароли не совпадают", "error")
                return
            # Проверяем старый пароль
            user = get_user_by_id(self.user_data['id'])
            if not user or not bcrypt.checkpw(old.encode(), user['password_hash'].encode()):
                show_centered_dialog(dialog, "Ошибка", "Неверный старый пароль", "error")
                return
            new_hash = bcrypt.hashpw(new.encode(), bcrypt.gensalt()).decode()
            if change_password(self.user_data['id'], new_hash):
                show_centered_dialog(dialog, "Успех", "Пароль изменён", "success")
                dialog.destroy()
            else:
                show_centered_dialog(dialog, "Ошибка", "Не удалось изменить пароль", "error")

        ctk.CTkButton(dialog, text="Сохранить", command=do_change, fg_color=COLOR_PRIMARY).pack(pady=10)