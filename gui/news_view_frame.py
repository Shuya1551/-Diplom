"""
Фрейм для просмотра полного текста новости с возможностью редактирования и удаления.
"""

import customtkinter as ctk
from services.file_storage import delete_generated_news, update_generated_news
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
        self.original_text = news_text
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← Назад", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=("Arial", 14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Просмотр и редактирование новости",
                     font=("Arial", 20, "bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.text_area = ctk.CTkTextbox(self, wrap="word", font=("Arial", 14))
        self.text_area.pack(fill="both", expand=True, padx=20, pady=10)
        self.text_area.insert("0.0", self.original_text)
        self.text_area.configure(state="normal")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_frame, text="💾 Сохранить изменения", command=self.save_news,
                                 fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, width=160)
        save_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑 Удалить новость", command=self.delete_news,
                                   fg_color="transparent", hover_color="#cc3333", width=160)
        delete_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(btn_frame, text="Закрыть", command=self.on_back,
                                  fg_color="transparent", hover_color="#3A3450", width=160)
        close_btn.pack(side="right", padx=5)

    def save_news(self):
        if not self.news_id:
            show_centered_dialog(self, "Ошибка", "Не удалось определить ID новости", "error")
            return
        new_text = self.text_area.get("0.0", "end").strip()
        if not new_text:
            show_centered_dialog(self, "Ошибка", "Текст новости не может быть пустым", "error")
            return
        if update_generated_news(self.news_id, new_text):
            self.original_text = new_text
            show_centered_dialog(self, "Успех", "Новость сохранена", "success")
        else:
            show_centered_dialog(self, "Ошибка", "Не удалось сохранить новость", "error")

    def delete_news(self):
        if not self.news_id:
            show_centered_dialog(self, "Ошибка", "Не удалось определить ID новости", "error")
            return
        result = show_centered_dialog(self, "Подтверждение", "Удалить эту новость?", "question", ("Да", "Нет"))
        if result == "Да":
            if delete_generated_news(self.news_id):
                show_centered_dialog(self, "Успех", "Новость удалена", "success")
                self.on_back()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось удалить новость", "error")