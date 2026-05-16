"""
Диалоговое окно для генерации новости из выбранного плана мероприятия.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
from repositories.event_plan_repository import get_event_plan_by_id
from repositories.generated_news_repository import save_generated_news
from repositories.log_repository import log_generation

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
        self.generated_text = ""
        self.start_time = None
        self.prompt_text = ""

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
                # Логируем ошибку
                log_generation(self.plan_id, self.user_data['id'], "", "", False, "План не найден", 0)
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

            # Формируем промпт (как в генераторе)
            title = plan_dict.get('title', 'мероприятие')
            location = plan_dict.get('location', '')
            description = plan_dict.get('description', '')
            speaker = plan_dict.get('speaker', '')
            self.prompt_text = (
                f"<s>Сгенерируй новостное сообщение о мероприятии по плану:\n"
                f"Название: {title}\nМесто: {location}\nО чём: {description}\nСпикер: {speaker}\n"
                f"Новость:"
            )

            update_status("Генерация новости... (может занять до минуты)")
            self.start_time = time.time()
            generated_text = self.generator.generate_news(plan_dict)
            inference_time = int((time.time() - self.start_time) * 1000)  # в мс

            self.generated_text = generated_text

            # Логируем успех
            log_generation(self.plan_id, self.user_data['id'], self.prompt_text, generated_text, True, None, inference_time)

            self.window.after(0, lambda: self.display_result(generated_text))
            update_status("Генерация завершена. Нажмите «Сохранить в БД».", stop_progress=True)
            self.window.after(0, lambda: self.save_btn.config(state=tk.NORMAL))

        except Exception as e:
            error_msg = str(e)
            update_status(f"Ошибка: {error_msg}", stop_progress=True)
            inference_time = int((time.time() - self.start_time) * 1000) if self.start_time else 0
            log_generation(self.plan_id, self.user_data['id'], self.prompt_text, "", False, error_msg, inference_time)
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать новость:\n{error_msg}")

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