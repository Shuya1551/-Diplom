"""
Фрейм для генерации новостей: список планов (карточки), и отдельно список ВСЕХ сгенерированных новостей.
"""

import customtkinter as ctk
from functools import partial

from repositories.event_plan_repository import get_all_event_plans
from repositories.generated_news_repository import get_all_generated_news, delete_generated_news
from utils import show_centered_dialog

# ---------- ЦВЕТА ----------
COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class GenerationFrame(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back, selected_plan_id=None):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.selected_plan_id = selected_plan_id
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← На главную", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Генерация новостей",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        plans_label = ctk.CTkLabel(self.main_frame, text="📋 Список планов мероприятий",
                                   font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY)
        plans_label.pack(anchor="w", pady=(0, 5))
        self.plans_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", height=300)
        self.plans_list.pack(fill="x", pady=(0, 15))

        news_label = ctk.CTkLabel(self.main_frame, text="📰 Все сгенерированные новости",
                                  font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY)
        news_label.pack(anchor="w", pady=(5, 5))
        self.news_list = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", height=250)
        self.news_list.pack(fill="both", expand=True)

        self.load_plans()
        self.load_all_news()

    def load_plans(self):
        for widget in self.plans_list.winfo_children():
            widget.destroy()
        plans = get_all_event_plans(self.user_data['id'], self.user_data['role'])
        if not plans:
            lbl = ctk.CTkLabel(self.plans_list, text="Нет планов. Создайте план в разделе «Планы».",
                               text_color=COLOR_GRAY)
            lbl.pack(pady=20)
            return
        for plan in plans:
            plan_id = plan[0]
            title = plan[1]
            event_date = plan[2]
            start_time = plan[3] or ""
            end_time = plan[4] or ""
            location = plan[5] or ""
            description = plan[6] or ""

            card = ctk.CTkFrame(self.plans_list, fg_color=COLOR_CARD, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=16, weight="bold"),
                         text_color=COLOR_PRIMARY).pack(anchor="w")
            date_str = event_date.strftime("%d.%m.%Y") if event_date else "дата не указана"
            time_str = f"{start_time} - {end_time}" if start_time or end_time else ""
            details = f"{date_str}  {time_str}  •  {location}" if location else f"{date_str}  {time_str}"
            ctk.CTkLabel(info_frame, text=details, text_color=COLOR_GRAY).pack(anchor="w", pady=(2, 2))
            if description:
                short_desc = description[:150] + "..." if len(description) > 150 else description
                ctk.CTkLabel(info_frame, text=short_desc, text_color=COLOR_TEXT, anchor="w",
                             justify="left", wraplength=500).pack(anchor="w", pady=(5, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)
            gen_btn = ctk.CTkButton(btn_frame, text="✨ Сгенерировать", width=140,
                                    command=partial(self.generate_for_plan, plan_id),
                                    fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY)
            gen_btn.pack()

    def load_all_news(self):
        for widget in self.news_list.winfo_children():
            widget.destroy()
        news_list = get_all_generated_news(self.user_data['id'], self.user_data['role'])
        if not news_list:
            lbl = ctk.CTkLabel(self.news_list, text="Нет сгенерированных новостей",
                               text_color=COLOR_GRAY)
            lbl.pack(anchor="w", pady=5)
            return
        for news in news_list:
            news_id = news[0]
            text = news[1]
            gen_date = news[2]
            approved = news[3]
            rating = news[4]
            plan_id = news[5]
            plan_title = news[6] if len(news) > 6 else f"План #{plan_id}"

            card = ctk.CTkFrame(self.news_list, fg_color=COLOR_CARD, corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=5)

            status_text = f"✅ Утверждена" if approved else "🟡 Не утверждена"
            ctk.CTkLabel(info_frame, text=f"{gen_date} | {status_text} | Рейтинг: {rating or 'нет'} | План: {plan_title}",
                         font=ctk.CTkFont(size=11), text_color=COLOR_GRAY).pack(anchor="w")

            short_text = text[:150] + "..." if len(text) > 150 else text
            ctk.CTkLabel(info_frame, text=short_text, font=ctk.CTkFont(size=12),
                         text_color=COLOR_TEXT, anchor="w", justify="left", wraplength=500).pack(anchor="w", pady=(2, 0))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=5)

            view_btn = ctk.CTkButton(btn_frame, text="Просмотреть", width=100,
                                     command=partial(self.view_news, text, news_id, plan_id))
            view_btn.pack(side="left", padx=2)

            delete_btn = ctk.CTkButton(btn_frame, text="🗑 Удалить", width=80,
                                       fg_color="transparent", hover_color="#cc3333",
                                       command=partial(self.delete_news, news_id))
            delete_btn.pack(side="left", padx=2)

    def view_news(self, text, news_id, plan_id):
        if hasattr(self.parent, 'switch_to_frame'):
            self.parent.switch_to_frame("news_view", news_id=news_id, news_text=text, plan_id=plan_id)
        else:
            show_centered_dialog(self, "Ошибка", "Не удалось открыть просмотр новости", "error")

    def generate_for_plan(self, plan_id):
        if hasattr(self.parent, 'switch_to_frame'):
            self.parent.switch_to_frame("generation_process", plan_id=plan_id, return_to_main=False)
        else:
            show_centered_dialog(self, "Ошибка", "Не удалось перейти к генерации", "error")

    def delete_news(self, news_id):
        result = show_centered_dialog(self, "Подтверждение", "Удалить выбранную новость?", "question", ("Да", "Нет"))
        if result == "Да":
            if delete_generated_news(news_id):
                show_centered_dialog(self, "Успех", "Новость удалена", "success")
                self.load_all_news()
            else:
                show_centered_dialog(self, "Ошибка", "Не удалось удалить новость", "error")