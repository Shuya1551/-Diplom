"""
Фрейм для отображения ВСЕХ сгенерированных новостей.
"""

import customtkinter as ctk
from functools import partial

from repositories.generated_news_repository import get_all_generated_news, delete_generated_news
from utils import show_centered_dialog

# ---------- ЦВЕТА ----------
COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class AllNewsFrame(ctk.CTkFrame):
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
        ctk.CTkLabel(top_frame, text="Все сгенерированные новости",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_news()

    def load_news(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()

        news_list = get_all_generated_news()
        if not news_list:
            lbl = ctk.CTkLabel(self.scrollable, text="Нет сгенерированных новостей",
                               text_color=COLOR_GRAY)
            lbl.pack(pady=20)
            return

        for news in news_list:
            news_id = news[0]
            text = news[1]
            gen_date = news[2]
            approved = news[3]
            rating = news[4]
            plan_id = news[5]
            plan_title = news[6] if len(news) > 6 else f"План #{plan_id}"

            card = ctk.CTkFrame(self.scrollable, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=10)

            status_text = "✅ Утверждена" if approved else "🟡 Не утверждена"
            header = f"{gen_date} | {status_text} | Рейтинг: {rating or 'нет'} | План: {plan_title}"
            ctk.CTkLabel(info_frame, text=header, font=ctk.CTkFont(size=12), text_color=COLOR_GRAY).pack(anchor="w")

            short_text = text[:200] + "..." if len(text) > 200 else text
            ctk.CTkLabel(info_frame, text=short_text, font=ctk.CTkFont(size=13),
                         text_color=COLOR_TEXT, anchor="w", justify="left", wraplength=600).pack(anchor="w", pady=(5, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            view_btn = ctk.CTkButton(btn_frame, text="👁️ Просмотреть", width=120,
                                     command=partial(self.view_news, text, news_id, plan_id))
            view_btn.pack(side="left", padx=2)

            delete_btn = ctk.CTkButton(btn_frame, text="🗑 Удалить", width=100,
                                       fg_color="transparent", hover_color="#cc3333",
                                       command=partial(self.delete_news, news_id))
            delete_btn.pack(side="left", padx=2)

    def view_news(self, text, news_id, plan_id):
        # Передаём специальный callback для возврата во фрейм всех новостей
        if hasattr(self.parent, 'switch_to_frame'):
            self.parent.switch_to_frame("news_view", news_id=news_id, news_text=text, plan_id=plan_id,
                                        on_back_callback=self.return_to_all_news)
        else:
            show_centered_dialog(self, "Ошибка", "Не удалось открыть просмотр новости", "error")

    def return_to_all_news(self):
        # Возвращаемся во фрейм всех новостей
        self.parent.switch_to_frame("all_news")

    def delete_news(self, news_id):
        result = show_centered_dialog(self, "Подтверждение", "Удалить выбранную новость?", "question", ("Да", "Нет"))
        if result == "Да":
            if delete_generated_news(news_id):
                show_centered_dialog(self, "Успех", "Новость удалена", "success")
                self.load_news()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось удалить новость", "error")