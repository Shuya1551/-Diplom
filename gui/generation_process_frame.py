"""
Фрейм для процесса генерации новости: генерация, сохранение.
"""

import customtkinter as ctk
import time
import threading

from repositories.event_plan_repository import get_event_plan_by_id
from repositories.generated_news_repository import save_generated_news
from repositories.log_repository import log_generation
from utils import show_centered_dialog

# ---------- ЦВЕТА ----------
COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class GenerationProcessFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back, plan_id):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.plan_id = plan_id
        self.generated_text = None
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← Назад", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Генерация новости",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.info_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD, corner_radius=10)
        self.info_frame.pack(fill="x", padx=20, pady=10)
        self.load_plan_info()

        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkLabel(self.text_frame, text="Сгенерированный текст:", font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLOR_TEXT).pack(anchor="w", pady=(0, 5))
        self.text_area = ctk.CTkTextbox(self.text_frame, wrap="word", font=ctk.CTkFont(size=12))
        self.text_area.pack(fill="both", expand=True)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=10)

        self.generate_btn = ctk.CTkButton(self.btn_frame, text="🚀 Сгенерировать", command=self.generate_news,
                                          fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=140)
        self.generate_btn.pack(side="left", padx=5)

        self.save_btn = ctk.CTkButton(self.btn_frame, text="💾 Сохранить", command=self.save_news,
                                      fg_color="transparent", hover_color="#3A3450", width=120, state="disabled")
        self.save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(self.btn_frame, text="Отмена", command=self.on_back,
                                   fg_color="transparent", hover_color="#3A3450", width=120)
        cancel_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color=COLOR_SECONDARY)
        self.status_label.pack(pady=(0, 10))

    def load_plan_info(self):
        plan = get_event_plan_by_id(self.plan_id, self.user_data['id'], self.user_data['role'])
        if not plan:
            show_centered_dialog(self, "Ошибка", "План не найден", "error")
            self.on_back()
            return
        title = plan[1]
        event_date = plan[2]
        start_time = plan[3] or ""
        end_time = plan[4] or ""
        location = plan[5] or ""
        description = plan[6] or ""
        info_text = f"📌 {title}\n📅 {event_date}  {start_time} - {end_time}\n📍 {location}\n📝 {description[:200] + '...' if len(description) > 200 else description}"
        info_label = ctk.CTkLabel(self.info_frame, text=info_text, font=ctk.CTkFont(size=13),
                                  text_color=COLOR_TEXT, justify="left", anchor="w")
        info_label.pack(padx=15, pady=15, anchor="w")

    def generate_news(self):
        self.generate_btn.configure(state="disabled", text="⏳ Генерация...")
        self.save_btn.configure(state="disabled")
        self.status_label.configure(text="Генерация новости, пожалуйста, подождите...")
        thread = threading.Thread(target=self._generate_thread)
        thread.daemon = True
        thread.start()

    def _generate_thread(self):
        try:
            plan_data_raw = get_event_plan_by_id(self.plan_id, self.user_data['id'], self.user_data['role'])
            if not plan_data_raw:
                self.after(0, lambda: show_centered_dialog(self, "Ошибка", "План не найден", "error"))
                self.after(0, self._reset_buttons)
                return
            plan_dict = {
                "title": plan_data_raw[1],
                "event_date": plan_data_raw[2],
                "event_time": plan_data_raw[3],
                "location": plan_data_raw[4],
                "description": plan_data_raw[5],
                "speaker": plan_data_raw[6],
                "audience": plan_data_raw[7],
                "category": plan_data_raw[8] if len(plan_data_raw) > 8 else "",
            }
            start_time = time.time()
            generated_text = self.news_generator.generate_news(plan_dict)
            inference_time = int((time.time() - start_time) * 1000)
            prompt = f"План: {plan_dict['title']}"
            log_generation(self.plan_id, self.user_data['id'], prompt, generated_text, True, None, inference_time)
            self.generated_text = generated_text
            self.after(0, self._display_result)
        except Exception as e:
            error_msg = str(e)
            log_generation(self.plan_id, self.user_data['id'], "", "", False, error_msg, 0)
            self.after(0, lambda: self._show_error(error_msg))

    def _display_result(self):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", self.generated_text)
        self.status_label.configure(text="Генерация завершена")
        self.generate_btn.configure(state="normal", text="🚀 Сгенерировать")
        self.save_btn.configure(state="normal")

    def _show_error(self, error_msg):
        show_centered_dialog(self, "Ошибка", f"Не удалось сгенерировать новость:\n{error_msg}", "error")
        self._reset_buttons()

    def _reset_buttons(self):
        self.generate_btn.configure(state="normal", text="🚀 Сгенерировать")
        self.save_btn.configure(state="disabled")
        self.status_label.configure(text="")

    def save_news(self):
        if not self.generated_text:
            show_centered_dialog(self, "Предупреждение", "Нет текста для сохранения", "warning")
            return
        saved_id = save_generated_news(self.plan_id, self.generated_text, self.user_data['id'], rating=None)
        if saved_id:
            show_centered_dialog(self, "Успех", "Новость сохранена в базу данных", "success")
            self.save_btn.configure(state="disabled")
            self.on_back()
        else:
            show_centered_dialog(self, "Ошибка", "Не удалось сохранить новость", "error")