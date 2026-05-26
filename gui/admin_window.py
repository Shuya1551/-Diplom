"""
Окно панели администратора: управление пользователями, просмотр логов, статистика.
"""

import customtkinter as ctk
from functools import partial
import bcrypt
from repositories.user_repository import (
    get_all_users, create_user, update_user, delete_user,
    change_password, get_roles, get_user_by_id
)
from repositories.log_repository import get_all_generation_logs, get_generation_stats
from repositories.generated_news_repository import get_all_generated_news
from utils import show_centered_dialog

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class AdminWindow(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← Назад", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Панель администратора",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.notebook = ctk.CTkTabview(self, fg_color=COLOR_CARD, segmented_button_fg_color=COLOR_BG,
                                       segmented_button_selected_color=COLOR_PRIMARY,
                                       segmented_button_unselected_color=COLOR_CARD,
                                       text_color=COLOR_TEXT)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.users_tab = self.notebook.add("Пользователи")
        self.logs_tab = self.notebook.add("Логи генерации")
        self.stats_tab = self.notebook.add("Статистика")

        self.create_users_tab()
        self.create_logs_tab()
        self.create_stats_tab()

    def create_users_tab(self):
        # Верхняя панель с кнопками управления
        ctrl_frame = ctk.CTkFrame(self.users_tab, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(ctrl_frame, text="➕ Добавить пользователя", command=self.add_user,
                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=180).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="🔄 Обновить список", command=self.load_users,
                      fg_color="transparent", hover_color="#3A3450", width=150).pack(side="left", padx=5)

        self.users_scrollable = ctk.CTkScrollableFrame(self.users_tab, fg_color="transparent")
        self.users_scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_users()

    def load_users(self):
        for widget in self.users_scrollable.winfo_children():
            widget.destroy()
        users = get_all_users()
        if not users:
            lbl = ctk.CTkLabel(self.users_scrollable, text="Нет пользователей", text_color=COLOR_GRAY)
            lbl.pack(pady=20)
            return
        for user in users:
            user_id, username, email, role, is_active, created_at, last_login = user
            card = ctk.CTkFrame(self.users_scrollable, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=10, side="left", expand=True)

            # Логин и роль
            ctk.CTkLabel(info_frame, text=username, font=ctk.CTkFont(size=15, weight="bold"),
                         text_color=COLOR_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"ID: {user_id} | Роль: {role} | Активен: {'Да' if is_active else 'Нет'}",
                         font=ctk.CTkFont(size=11), text_color=COLOR_GRAY).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Email: {email}", font=ctk.CTkFont(size=12),
                         text_color=COLOR_TEXT).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"Создан: {created_at}", font=ctk.CTkFont(size=11),
                         text_color=COLOR_GRAY).pack(anchor="w")
            if last_login:
                ctk.CTkLabel(info_frame, text=f"Последний вход: {last_login}", font=ctk.CTkFont(size=11),
                             text_color=COLOR_GRAY).pack(anchor="w")

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(side="right", padx=10, pady=10)

            edit_btn = ctk.CTkButton(actions, text="✏️ Редактировать", width=110,
                                     command=lambda uid=user_id: self.edit_user(uid))
            edit_btn.pack(pady=2)
            reset_btn = ctk.CTkButton(actions, text="🔑 Сбросить пароль", width=110,
                                      fg_color="transparent", hover_color="#3A3450",
                                      command=lambda uid=user_id: self.reset_password(uid))
            reset_btn.pack(pady=2)
            if user_id != self.user_data['id']:
                delete_btn = ctk.CTkButton(actions, text="🗑 Удалить", width=110,
                                           fg_color="transparent", hover_color="#cc3333",
                                           command=lambda uid=user_id: self.delete_user(uid))
                delete_btn.pack(pady=2)

    def edit_user(self, user_id):
        users = get_all_users()
        user_data = next((u for u in users if u[0] == user_id), None)
        if not user_data:
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Редактирование пользователя")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Email:").pack(pady=5)
        entry_email = ctk.CTkEntry(dialog, width=250)
        entry_email.insert(0, user_data[2])
        entry_email.pack()

        ctk.CTkLabel(dialog, text="Активен:").pack(pady=5)
        active_var = ctk.BooleanVar(value=user_data[4])
        ctk.CTkCheckBox(dialog, text="Да", variable=active_var).pack()

        ctk.CTkLabel(dialog, text="Роль:").pack(pady=5)
        roles = get_roles()
        role_var = ctk.StringVar(value=user_data[3])
        role_combo = ctk.CTkComboBox(dialog, values=[r[1] for r in roles], variable=role_var, width=200)
        role_combo.pack()

        def save():
            email = entry_email.get().strip()
            is_active = active_var.get()
            role_name = role_var.get()
            role_id = next((r[0] for r in roles if r[1] == role_name), None)
            if not email or role_id is None:
                show_centered_dialog(dialog, "Ошибка", "Заполните поля", "error")
                return
            success = update_user(user_id, email=email, role_id=role_id, is_active=is_active)
            if success:
                show_centered_dialog(dialog, "Успех", "Данные обновлены", "success")
                dialog.destroy()
                self.load_users()
            else:
                show_centered_dialog(dialog, "Ошибка", "Не удалось обновить", "error")

        ctk.CTkButton(dialog, text="Сохранить", command=save, fg_color=COLOR_PRIMARY).pack(pady=15)

    def reset_password(self, user_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Сброс пароля")
        dialog.geometry("350x200")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Новый пароль:").pack(pady=10)
        entry_pass = ctk.CTkEntry(dialog, show="*", width=200)
        entry_pass.pack()

        def save():
            new_pass = entry_pass.get()
            if not new_pass:
                show_centered_dialog(dialog, "Ошибка", "Введите пароль", "error")
                return
            pass_hash = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
            if change_password(user_id, pass_hash):
                show_centered_dialog(dialog, "Успех", "Пароль изменён", "success")
                dialog.destroy()
            else:
                show_centered_dialog(dialog, "Ошибка", "Не удалось сменить пароль", "error")

        ctk.CTkButton(dialog, text="Сохранить", command=save, fg_color=COLOR_PRIMARY).pack(pady=15)

    def delete_user(self, user_id):
        if user_id == self.user_data['id']:
            show_centered_dialog(self, "Ошибка", "Нельзя удалить самого себя", "error")
            return
        if show_centered_dialog(self, "Подтверждение", "Удалить пользователя?", "question", ("Да", "Нет")):
            if delete_user(user_id):
                show_centered_dialog(self, "Успех", "Пользователь удалён", "success")
                self.load_users()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось удалить", "error")

    def add_user(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавление пользователя")
        dialog.geometry("400x420")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Логин:").pack(pady=5)
        entry_login = ctk.CTkEntry(dialog, width=250)
        entry_login.pack()

        ctk.CTkLabel(dialog, text="Email:").pack(pady=5)
        entry_email = ctk.CTkEntry(dialog, width=250)
        entry_email.pack()

        ctk.CTkLabel(dialog, text="Пароль:").pack(pady=5)
        entry_pass = ctk.CTkEntry(dialog, show="*", width=250)
        entry_pass.pack()

        ctk.CTkLabel(dialog, text="Роль:").pack(pady=5)
        roles = get_roles()
        role_var = ctk.StringVar()
        role_combo = ctk.CTkComboBox(dialog, values=[r[1] for r in roles], variable=role_var, width=200)
        role_combo.pack()
        if roles:
            role_combo.set(roles[0][1])

        def save():
            login = entry_login.get().strip()
            email = entry_email.get().strip()
            password = entry_pass.get()
            role_name = role_var.get()
            if not login or not email or not password:
                show_centered_dialog(dialog, "Ошибка", "Заполните все поля", "error")
                return
            role_id = next((r[0] for r in roles if r[1] == role_name), None)
            if not role_id:
                show_centered_dialog(dialog, "Ошибка", "Роль не выбрана", "error")
                return
            pass_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_id = create_user(login, pass_hash, email, role_id, True)
            if new_id:
                show_centered_dialog(dialog, "Успех", f"Пользователь {login} создан", "success")
                dialog.destroy()
                self.load_users()
            else:
                show_centered_dialog(dialog, "Ошибка", "Не удалось создать пользователя", "error")

        ctk.CTkButton(dialog, text="Сохранить", command=save, fg_color=COLOR_PRIMARY).pack(pady=15)

    def create_logs_tab(self):
        self.logs_text = ctk.CTkTextbox(self.logs_tab, wrap="word", font=ctk.CTkFont(size=12))
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=10)
        btn_frame = ctk.CTkFrame(self.logs_tab, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="Обновить логи", command=self.load_logs,
                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=120).pack()
        self.load_logs()

    def load_logs(self):
        self.logs_text.delete("1.0", "end")
        logs = get_all_generation_logs(limit=200)
        if not logs:
            self.logs_text.insert("1.0", "Нет логов")
            return
        for log in logs:
            self.logs_text.insert("end", f"ID: {log[0]} | {log[1]} | Пользователь: {log[2] or '-'} | План: {log[3] or '-'} | Успех: {'Да' if log[4] else 'Нет'} | Время: {log[5] or '-'} мс\n")
            if log[6]:
                self.logs_text.insert("end", f"Ошибка: {log[6][:100]}\n")
            self.logs_text.insert("end", "-" * 80 + "\n")
        self.logs_text.configure(state="disabled")

    def create_stats_tab(self):
        self.stats_text = ctk.CTkTextbox(self.stats_tab, wrap="word", font=ctk.CTkFont(size=13))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_stats()
        btn_frame = ctk.CTkFrame(self.stats_tab, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        ctk.CTkButton(btn_frame, text="Обновить статистику", command=self.load_stats,
                      fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=150).pack()

    def load_stats(self):
        stats = get_generation_stats()
        users_count = len(get_all_users())
        all_news = get_all_generated_news(None, 'admin')
        news_count = len(all_news)
        text = f"""
=== ОБЩАЯ СТАТИСТИКА ===

Пользователей в системе: {users_count}
Сгенерированных новостей: {news_count}

=== ГЕНЕРАЦИИ (логи) ===

Всего попыток генерации: {stats['total']}
Успешных: {stats['successful']}
Процент успеха: {stats['successful']/stats['total']*100:.1f}% если были попытки
Среднее время генерации: {stats['avg_time_ms']} мс

=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===

Версия приложения: 1.0
Текущий администратор: {self.user_data['username']}
        """
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", text)
        self.stats_text.configure(state="disabled")