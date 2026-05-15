"""
Диалог выбора новостей для экспорта в Word или Excel.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from repositories.generated_news_repository import get_all_generated_news, get_news_by_id
from services.document_exporter import export_to_docx, export_to_xlsx

class ExportDialog:
    def __init__(self, parent, user_data, format_type):
        """
        format_type: 'docx' или 'xlsx'
        """
        self.parent = parent
        self.user_data = user_data
        self.format_type = format_type  # 'docx' или 'xlsx'
        self.window = tk.Toplevel(parent)
        self.window.title(f"Экспорт новостей в {format_type.upper()}")
        self.window.geometry("800x500")
        self.window.transient(parent)
        self.window.grab_set()

        self.news_data = []  # список словарей {id, title, date, text, ...}
        self.selected_indices = set()

        self.create_widgets()
        self.load_news()

    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.window)
        top_frame.pack(pady=5, fill=tk.X, padx=10)
        tk.Label(top_frame, text="Выберите новости для экспорта (клик + Ctrl/Shift):").pack(side=tk.LEFT)

        # Список новостей с возможностью множественного выбора
        self.listbox = tk.Listbox(self.window, selectmode=tk.MULTIPLE, height=20)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Нижняя панель с кнопками
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        tk.Button(btn_frame, text="📄 Экспортировать выбранные", command=self.export_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Отмена", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)

    def load_news(self):
        all_news = get_all_generated_news()
        # all_news: (id, text, gen_date, approved, rating, plan_id, plan_title)
        self.news_data = []
        for news in all_news:
            news_id, text, gen_date, approved, rating, plan_id, plan_title = news
            self.news_data.append({
                'id': news_id,
                'plan_title': plan_title,
                'date': str(gen_date),
                'text': text,
                'approved': approved,
                'rating': rating
            })
            display_text = f"{news_id} | {plan_title} | {gen_date} | {'✅' if approved else '🟡'}"
            self.listbox.insert(tk.END, display_text)

        if not self.news_data:
            self.listbox.insert(tk.END, "Нет сохранённых новостей")

    def export_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну новость")
            return

        export_items = []
        for idx in selected:
            if idx < len(self.news_data):
                export_items.append(self.news_data[idx])

        if not export_items:
            return

        # Предложить сохранить файл
        default_ext = ".docx" if self.format_type == 'docx' else ".xlsx"
        initial_file = f"news_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"
        filepath = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[("Word documents", "*.docx")] if self.format_type == 'docx' else [("Excel files", "*.xlsx")],
            initialfile=initial_file
        )
        if not filepath:
            return

        try:
            if self.format_type == 'docx':
                export_to_docx(export_items, filepath)
            else:
                export_to_xlsx(export_items, filepath)
            messagebox.showinfo("Успех", f"Экспортировано {len(export_items)} новостей в {filepath}")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{e}")