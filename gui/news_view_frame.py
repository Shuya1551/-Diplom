"""
Фрейм для просмотра полного текста новости с возможностью удаления.
"""

import customtkinter as ctk
from repositories.generated_news_repository import delete_generated_news
from utils import show_centered_dialog

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"

class NewsViewFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back, news_id=None, news_text=""):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.news_id = news_id
        self.news_text = news_text
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← Назад", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Просмотр новости",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.text_area = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=14))
        self.text_area.pack(fill="both", expand=True, padx=20, pady=10)
        self.text_area.insert("0.0", self.news_text)
        self.text_area.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        delete_btn = ctk.CTkButton(btn_frame, text="🗑 Удалить новость", command=self.delete_news,
                                   fg_color="transparent", hover_color="#cc3333", width=150)
        delete_btn.pack(side="right", padx=5)

        close_btn = ctk.CTkButton(btn_frame, text="Закрыть", command=self.on_back,
                                  fg_color="transparent", hover_color="#3A3450", width=150)
        close_btn.pack(side="right", padx=5)

    def delete_news(self):
        if not self.news_id:
            show_centered_dialog(self, "Ошибка", "Не удалось определить ID новости", "error")
            return
        if show_centered_dialog(self, "Подтверждение", "Удалить эту новость?", "question", ("Да", "Нет")):
            if delete_generated_news(self.news_id):
                show_centered_dialog(self, "Успех", "Новость удалена", "success")
                self.on_back()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось удалить новость", "error")