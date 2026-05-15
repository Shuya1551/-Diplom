"""
Диалоговое окно для генерации новости из выбранного плана мероприятия.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from repositories.event_plan_repository import get_event_plan_by_id
from repositories.generated_news_repository import save_generated_news
import threading

class GenerationDialog:
    def __init__(self, parent, plan_id, user_data, news_generator):
        self.window = tk.Toplevel(parent)
        self.window.title("Генерация новости")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()

        self.plan_id = plan_id
        self.user_data = user_data
        self.generator = news_generator
        self.generated_text = ""  # сохраним сгенерированный текст

        # Интерфейс
        self.status_label = tk.Label(self.window, text="Подготовка к генерации...")
        self.status_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)

        self.text_area = tk.Text(self.window, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.save_btn = tk.Button(btn_frame, text="💾 Сохранить в БД", command=self.save_to_db, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="❌ Закрыть", command=self.window.destroy).pack(side=tk.RIGHT, padx=10)

        # Запускаем генерацию
        self.window.after(100, self.start_generation)

    def start_generation(self):
        thread = threading.Thread(target=self.generate_news_thread)
        thread.start()

    def generate_news_thread(self):
        def update_status(text, start_progress=False, stop_progress=False):
            self.window.after(0, lambda: self.status_label.config(text=text))
            if start_progress:
                self.window.after(0, self.progress.start)
            if stop_progress:
                self.window.after(0, self.progress.stop)

        try:
            update_status("Получение данных плана...", start_progress=True)

            plan_data_raw = get_event_plan_by_id(self.plan_id)
            if not plan_data_raw:
                update_status("Ошибка: План мероприятия не найден.", stop_progress=True)
                return

            plan_dict = {
                "title": plan_data_raw[1],
                "event_date": plan_data_raw[2],
                "event_time": plan_data_raw[3],
                "location": plan_data_raw[4],
                "description": plan_data_raw[5],
                "speaker": plan_data_raw[6],
                "audience": plan_data_raw[7],
            }

            update_status("Генерация новости... (может занять до минуты)")
            generated_text = self.generator.generate_news(plan_dict)
            self.generated_text = generated_text   # сохраняем для сохранения

            self.window.after(0, lambda: self.display_result(generated_text))
            update_status("Генерация завершена. Нажмите «Сохранить в БД».", stop_progress=True)
            self.window.after(0, lambda: self.save_btn.config(state=tk.NORMAL))

        except Exception as e:
            update_status(f"Ошибка: {str(e)}", stop_progress=True)
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать новость:\n{str(e)}")

    def display_result(self, text):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, text)
        self.text_area.config(state=tk.DISABLED)

    def save_to_db(self):
        if not self.generated_text.strip():
            messagebox.showwarning("Предупреждение", "Нет текста для сохранения")
            return

        try:
            saved_id = save_generated_news(
                event_plan_id=self.plan_id,
                generated_text=self.generated_text,
                user_id=self.user_data['id'],
                rating=None
            )
            if saved_id:
                messagebox.showinfo("Успех", f"Новость сохранена в БД (ID={saved_id})")
                self.save_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить новость (см. консоль)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Исключение при сохранении:\n{str(e)}")