"""
Окно просмотра ВСЕХ сгенерированных новостей.
Поддерживает множественный выбор, удаление, экспорт в DOCX/XLSX.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from repositories.generated_news_repository import get_all_generated_news, delete_generated_news, get_news_by_id
from services.document_exporter import export_to_docx, export_to_xlsx

class NewsViewWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Все сгенерированные новости")
        self.window.geometry("1100x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.load_news()
    
    def create_widgets(self):
        # Таблица со всеми новостями (множественный выбор)
        columns = ("ID", "План", "Дата генерации", "Утверждено", "Рейтинг", "Текст (начало)")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID")
        self.tree.heading("План", text="План мероприятия")
        self.tree.heading("Дата генерации", text="Дата генерации")
        self.tree.heading("Утверждено", text="Утверждено")
        self.tree.heading("Рейтинг", text="Рейтинг")
        self.tree.heading("Текст (начало)", text="Текст (начало)")
        self.tree.column("ID", width=50)
        self.tree.column("План", width=200)
        self.tree.column("Дата генерации", width=140)
        self.tree.column("Утверждено", width=80)
        self.tree.column("Рейтинг", width=60)
        self.tree.column("Текст (начало)", width=500)
        
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Панель кнопок
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="🗑 Удалить выбранные новости", command=self.delete_selected_news).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📄 Экспорт выбранных в DOCX", command=lambda: self.export_selected('docx')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📊 Экспорт выбранных в XLSX", command=lambda: self.export_selected('xlsx')).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Обновить", command=self.load_news).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Закрыть", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_news(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        news_list = get_all_generated_news()
        # each row: (id, text, gen_date, approved, rating, plan_id, plan_title)
        for news in news_list:
            news_id, text, gen_date, approved, rating, plan_id, plan_title = news
            short_text = (text[:120] + '...') if len(text) > 120 else text
            self.tree.insert("", tk.END, values=(
                news_id, plan_title, gen_date, "Да" if approved else "Нет", rating or "", short_text
            ), tags=(news_id,))
    
    def get_selected_news_ids(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну новость")
            return []
        ids = []
        for item in selected:
            values = self.tree.item(item, "values")
            ids.append(values[0])
        return ids
    
    def delete_selected_news(self):
        ids = self.get_selected_news_ids()
        if not ids:
            return
        if messagebox.askyesno("Подтверждение", f"Удалить выбранные новости ({len(ids)} шт.)?"):
            for nid in ids:
                delete_generated_news(nid)
            self.load_news()
            messagebox.showinfo("Успех", f"Удалено {len(ids)} новостей")
    
    def export_selected(self, format_type):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите новости для экспорта")
            return
        
        export_data = []
        for item in selected_items:
            values = self.tree.item(item, "values")
            news_id = values[0]
            plan_title = values[1]
            gen_date = values[2]
            approved = values[3] == "Да"
            rating = values[4] if values[4] else None
            # Получаем полный текст новости из БД
            full_news = get_news_by_id(news_id)
            text = full_news[1] if full_news else ""
            export_data.append({
                'id': news_id,
                'plan_title': plan_title,
                'date': gen_date,
                'text': text,
                'approved': approved,
                'rating': rating
            })
        
        if not export_data:
            return
        
        default_ext = ".docx" if format_type == 'docx' else ".xlsx"
        initial_file = f"news_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"
        filepath = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=[("Word documents", "*.docx")] if format_type == 'docx' else [("Excel files", "*.xlsx")],
            initialfile=initial_file
        )
        if not filepath:
            return
        try:
            if format_type == 'docx':
                export_to_docx(export_data, filepath)
            else:
                export_to_xlsx(export_data, filepath)
            messagebox.showinfo("Успех", f"Экспортировано {len(export_data)} новостей в {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{e}")