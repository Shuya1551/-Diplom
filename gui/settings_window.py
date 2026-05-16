"""
Окно настроек приложения.
Позволяет изменять параметры генерации, экспорта и просматривать информацию.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from repositories.settings_repository import get_setting, set_setting, get_all_settings

class SettingsWindow:
    def __init__(self, parent, user_data, refresh_callback=None):
        self.parent = parent
        self.user_data = user_data
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки приложения")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Общие"
        self.general_frame = tk.Frame(self.notebook)
        self.notebook.add(self.general_frame, text="Общие")
        self.create_general_tab()
        
        # Вкладка "Генерация новостей"
        self.gen_frame = tk.Frame(self.notebook)
        self.notebook.add(self.gen_frame, text="Генерация")
        self.create_generation_tab()
        
        # Вкладка "Экспорт"
        self.export_frame = tk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Экспорт")
        self.create_export_tab()
        
        # Вкладка "О системе"
        self.about_frame = tk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="О системе")
        self.create_about_tab()
        
        # Кнопки внизу
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        tk.Button(btn_frame, text="Сохранить все", command=self.save_all).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.RIGHT, padx=10)
        
        self.load_settings()
    
    def create_general_tab(self):
        # Место для общих настроек (например, путь к модели, язык)
        row = 0
        tk.Label(self.general_frame, text="Путь к модели (локальный):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.model_path_var = tk.StringVar()
        tk.Entry(self.general_frame, textvariable=self.model_path_var, width=50).grid(row=row, column=1, pady=5, padx=5)
        row += 1
    
    def create_generation_tab(self):
        row = 0
        # Температура
        tk.Label(self.gen_frame, text="Температура (0.1 – 1.0):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.temperature_var = tk.DoubleVar()
        tk.Scale(self.gen_frame, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                 variable=self.temperature_var, length=300).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Max новых токенов
        tk.Label(self.gen_frame, text="Макс. длина новости (токенов):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.max_tokens_var = tk.IntVar()
        tk.Spinbox(self.gen_frame, from_=50, to=500, textvariable=self.max_tokens_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # Top-k
        tk.Label(self.gen_frame, text="Top-k (1-100):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.top_k_var = tk.IntVar()
        tk.Spinbox(self.gen_frame, from_=1, to=100, textvariable=self.top_k_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1
        
        # Top-p
        tk.Label(self.gen_frame, text="Top-p (0.0-1.0):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.top_p_var = tk.DoubleVar()
        tk.Scale(self.gen_frame, from_=0.0, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                 variable=self.top_p_var, length=300).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # repetition_penalty
        tk.Label(self.gen_frame, text="Штраф за повторения (1.0-2.0):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.rep_penalty_var = tk.DoubleVar()
        tk.Spinbox(self.gen_frame, from_=1.0, to=2.0, increment=0.05, textvariable=self.rep_penalty_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
    
    def create_export_tab(self):
        row = 0
        tk.Label(self.export_frame, text="Папка по умолчанию для экспорта:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.export_dir_var = tk.StringVar()
        tk.Entry(self.export_frame, textvariable=self.export_dir_var, width=40).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        tk.Button(self.export_frame, text="Обзор...", command=self.browse_export_dir).grid(row=row, column=2, padx=5)
        row += 1
        
        tk.Label(self.export_frame, text="Формат по умолчанию:").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.default_format_var = tk.StringVar()
        ttk.Combobox(self.export_frame, textvariable=self.default_format_var, values=["docx", "xlsx"], width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
    
    def create_about_tab(self):
        text = tk.Text(self.about_frame, wrap=tk.WORD, height=15)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        info = f"""
Программа: Автоматическая генерация новостей из плана мероприятий
Версия: 1.0
Автор: Головатый И.Н.
Группа: Идс23Б
Год: 2026

Используемые технологии:
- Python 3.11+
- PostgreSQL
- tkinter (GUI)
- transformers + ruGPT-3 Medium
- python-docx, openpyxl

Описание:
Приложение позволяет создавать планы мероприятий, генерировать новостные сообщения с помощью нейросети,
сохранять результаты в БД, экспортировать в Word/Excel, управлять пользователями.
        """
        text.insert(tk.END, info)
        text.config(state=tk.DISABLED)
    
    def browse_export_dir(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory()
        if directory:
            self.export_dir_var.set(directory)
    
    def load_settings(self):
        # Загружаем настройки из БД и заполняем поля
        self.model_path_var.set(get_setting("model_path", "./finetuned_rugpt3"))
        self.temperature_var.set(float(get_setting("temperature", "0.7")))
        self.max_tokens_var.set(int(get_setting("max_new_tokens", "200")))
        self.top_k_var.set(int(get_setting("top_k", "50")))
        self.top_p_var.set(float(get_setting("top_p", "0.9")))
        self.rep_penalty_var.set(float(get_setting("repetition_penalty", "1.2")))
        self.export_dir_var.set(get_setting("export_default_dir", ""))
        self.default_format_var.set(get_setting("default_export_format", "docx"))
    
    def save_all(self):
        # Сохраняем все настройки в БД
        set_setting("model_path", self.model_path_var.get(), self.user_data['id'])
        set_setting("temperature", str(self.temperature_var.get()), self.user_data['id'])
        set_setting("max_new_tokens", str(self.max_tokens_var.get()), self.user_data['id'])
        set_setting("top_k", str(self.top_k_var.get()), self.user_data['id'])
        set_setting("top_p", str(self.top_p_var.get()), self.user_data['id'])
        set_setting("repetition_penalty", str(self.rep_penalty_var.get()), self.user_data['id'])
        set_setting("export_default_dir", self.export_dir_var.get(), self.user_data['id'])
        set_setting("default_export_format", self.default_format_var.get(), self.user_data['id'])
        
        messagebox.showinfo("Успех", "Настройки сохранены")
        if self.refresh_callback:
            self.refresh_callback()
        self.window.destroy()