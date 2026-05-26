"""
Фрейм для выбора новостей для экспорта (множественный выбор).
"""

import customtkinter as ctk
from tkinter import filedialog
from functools import partial
from datetime import datetime

from repositories.generated_news_repository import get_all_generated_news
from services.document_exporter import export_to_docx, export_to_xlsx
from utils import show_centered_dialog

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class ExportSelectionFrame(ctk.CTkFrame):
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
        ctk.CTkLabel(top_frame, text="Экспорт новостей",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 10))
        select_all_btn = ctk.CTkButton(ctrl_frame, text="✓ Выбрать всё", command=self.select_all,
                                       fg_color="transparent", hover_color="#3A3450", width=120)
        select_all_btn.pack(side="left", padx=5)
        clear_all_btn = ctk.CTkButton(ctrl_frame, text="✗ Снять выделение", command=self.clear_all,
                                      fg_color="transparent", hover_color="#3A3450", width=140)
        clear_all_btn.pack(side="left", padx=5)
        export_btn = ctk.CTkButton(ctrl_frame, text="📄 Экспорт", command=self.export_selected,
                                   fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=120)
        export_btn.pack(side="right", padx=5)

        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=20, pady=10)

        self.checkboxes = []
        self.load_news()

    def load_news(self):
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        self.checkboxes.clear()
        news_list = get_all_generated_news(self.user_data['id'], self.user_data['role'])
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

            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(info_frame, text="", variable=var, width=20, fg_color=COLOR_PRIMARY)
            cb.grid(row=0, column=0, sticky="nw", padx=(0, 10))
            self.checkboxes.append((var, news_id))

            text_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            text_frame.grid(row=0, column=1, sticky="w")

            status_text = f"✅ Утверждена" if approved else "🟡 Не утверждена"
            header = f"{gen_date} | {status_text} | Рейтинг: {rating or 'нет'} | План: {plan_title}"
            ctk.CTkLabel(text_frame, text=header, font=ctk.CTkFont(size=12), text_color=COLOR_GRAY).pack(anchor="w")
            short_text = text[:200] + "..." if len(text) > 200 else text
            ctk.CTkLabel(text_frame, text=short_text, font=ctk.CTkFont(size=13),
                         text_color=COLOR_TEXT, anchor="w", justify="left", wraplength=500).pack(anchor="w", pady=(5, 0))

            view_btn = ctk.CTkButton(card, text="👁️ Просмотреть", width=100,
                                     command=partial(self.view_news, text, news_id, plan_id))
            view_btn.pack(side="right", padx=10, pady=10)

    def view_news(self, text, news_id, plan_id):
        self.parent.switch_to_frame("news_view", news_id=news_id, news_text=text, plan_id=plan_id,
                                    on_back_callback=self.return_to_export)

    def return_to_export(self):
        self.parent.switch_to_frame("export")

    def select_all(self):
        for var, _ in self.checkboxes:
            var.set(True)

    def clear_all(self):
        for var, _ in self.checkboxes:
            var.set(False)

    def export_selected(self):
        selected = [news_id for var, news_id in self.checkboxes if var.get()]
        if not selected:
            show_centered_dialog(self, "Предупреждение", "Не выбрано ни одной новости", "warning")
            return

        all_news = get_all_generated_news(self.user_data['id'], self.user_data['role'])
        news_dict = {n[0]: n for n in all_news}
        export_data = []
        for news_id in selected:
            n = news_dict[news_id]
            export_data.append({
                'id': n[0],
                'plan_title': n[6] if len(n) > 6 else f"План #{n[5]}",
                'date': str(n[2]),
                'text': n[1],
                'approved': n[3],
                'rating': n[4]
            })

        choice = show_centered_dialog(self, "Выбор формата", "Выберите формат экспорта:", "question",
                                      ("Word (.docx)", "Excel (.xlsx)", "Отмена"))
        if not choice or choice == "Отмена":
            return

        format_type = 'docx' if choice == "Word (.docx)" else 'xlsx'
        default_ext = ".docx" if format_type == 'docx' else ".xlsx"
        filetypes = [("Word documents", "*.docx")] if format_type == 'docx' else [("Excel files", "*.xlsx")]
        initial_file = f"news_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"

        filepath = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=initial_file
        )
        if not filepath:
            return

        try:
            if format_type == 'docx':
                export_to_docx(export_data, filepath)
            else:
                export_to_xlsx(export_data, filepath)
            show_centered_dialog(self, "Успех", f"Экспортировано {len(export_data)} новостей", "success")
        except Exception as e:
            show_centered_dialog(self, "Ошибка", f"Не удалось экспортировать:\n{e}", "error")