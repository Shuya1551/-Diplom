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
        self.running = True

        self.plan_id = plan_id
        self.user_data = user_data
        self.generator = news_generator
        self.generated_text = ""
        self.start_time = None
        self.prompt_text = ""

        # Интерфейс
        self.status_label = ttk.Label(self.window, text="Подготовка к генерации...")
        self.status_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.window, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)

        self.text_area = tk.Text(self.window, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.save_btn = tk.Button(btn_frame, text="💾 Сохранить в БД", command=self.save_to_db, state=tk.DISABLED)
        self.save_btn.pack(side=tk.RIGHT, padx=10)

        tk.Button(btn_frame, text="❌ Закрыть", command=self.close).pack(side=tk.RIGHT, padx=10)

        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.after(100, self.start_generation)

    def close(self):
        self.running = False
        self.window.destroy()

    def start_generation(self):
        thread = threading.Thread(target=self.generate_news_thread)
        thread.daemon = True
        thread.start()

    def generate_news_thread(self):
        def update_status(text, start_progress=False, stop_progress=False):
            if not self.running:
                return
            def _update():
                if not self.running:
                    return
                self.status_label.config(text=text)
                if start_progress:
                    self.progress.start()
                if stop_progress:
                    self.progress.stop()
            self.window.after(0, _update)

        try:
            update_status("Получение данных плана...", start_progress=True)

            plan_data_raw = get_event_plan_by_id(self.plan_id)
            if not plan_data_raw:
                update_status("Ошибка: План мероприятия не найден.", stop_progress=True)
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
            inference_time = int((time.time() - self.start_time) * 1000)

            self.generated_text = generated_text

            log_generation(self.plan_id, self.user_data['id'], self.prompt_text, generated_text, True, None, inference_time)

            def display():
                if not self.running:
                    return
                self.text_area.config(state=tk.NORMAL)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, generated_text)
                self.text_area.config(state=tk.DISABLED)
                self.save_btn.config(state=tk.NORMAL)
                update_status("Генерация завершена. Нажмите «Сохранить в БД».", stop_progress=True)

            self.window.after(0, display)

        except Exception as e:
            error_msg = str(e)
            update_status(f"Ошибка: {error_msg}", stop_progress=True)
            inference_time = int((time.time() - self.start_time) * 1000) if self.start_time else 0
            log_generation(self.plan_id, self.user_data['id'], self.prompt_text, "", False, error_msg, inference_time)
            if self.running:
                self.window.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось сгенерировать новость:\n{error_msg}"))

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