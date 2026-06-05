"""
Окно настроек приложения.
"""

import customtkinter as ctk
from tkinter import filedialog
from services.file_storage import get_setting, set_setting
from utils import show_centered_dialog

COLOR_PRIMARY = "#6C63FF"
COLOR_BG = "#1E1A2E"
COLOR_CARD = "#2A2438"
COLOR_TEXT = "#FFFFFF"
COLOR_SECONDARY = "#00C9A7"
COLOR_GRAY = "#888888"

class SettingsWindow(ctk.CTkFrame):
    def __init__(self, parent, user_data, news_generator, on_back, apply_window_callback=None):
        super().__init__(parent, fg_color=COLOR_BG)
        self.parent = parent
        self.user_data = user_data
        self.news_generator = news_generator
        self.on_back = on_back
        self.apply_window_callback = apply_window_callback
        self.pack(fill="both", expand=True)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        back_btn = ctk.CTkButton(top_frame, text="← На главную", command=self.on_back,
                                 fg_color="transparent", text_color=COLOR_SECONDARY,
                                 font=ctk.CTkFont(size=14), hover_color="#3A3450")
        back_btn.pack(side="left")
        ctk.CTkLabel(top_frame, text="Настройки",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color=COLOR_PRIMARY).pack(side="left", padx=20)

        self.notebook = ctk.CTkTabview(self, fg_color=COLOR_CARD, segmented_button_fg_color=COLOR_BG,
                                       segmented_button_selected_color=COLOR_PRIMARY,
                                       segmented_button_unselected_color=COLOR_CARD,
                                       text_color=COLOR_TEXT)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.generation_tab = self.notebook.add("Генерация")
        self.export_tab = self.notebook.add("Экспорт")
        self.window_tab = self.notebook.add("Окно")

        self.create_generation_tab()
        self.create_export_tab()
        self.create_window_tab()

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        save_btn = ctk.CTkButton(btn_frame, text="Сохранить", command=self.save_all_settings,
                                 fg_color=COLOR_PRIMARY, hover_color=COLOR_SECONDARY, width=120)
        save_btn.pack(side="right", padx=5)
        cancel_btn = ctk.CTkButton(btn_frame, text="Отмена", command=self.on_back,
                                   fg_color="transparent", hover_color="#3A3450", width=120)
        cancel_btn.pack(side="right", padx=5)

        self.load_settings()

    def create_generation_tab(self):
        # Путь к модели
        ctk.CTkLabel(self.generation_tab, text="Путь к модели (локальный):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(15, 0))
        self.model_path_var = ctk.StringVar()
        ctk.CTkEntry(self.generation_tab, textvariable=self.model_path_var, width=400).pack(anchor="w", padx=15, pady=5)

        # Температура
        ctk.CTkLabel(self.generation_tab, text="Температура (0.1 – 1.0):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.temperature_var = ctk.StringVar()
        temp_scale = ctk.CTkSlider(self.generation_tab, from_=0.1, to=1.0, number_of_steps=18, width=300)
        temp_scale.pack(anchor="w", padx=15, pady=5)
        self.temp_label = ctk.CTkLabel(self.generation_tab, text="", font=ctk.CTkFont(size=12), text_color=COLOR_GRAY)
        self.temp_label.pack(anchor="w", padx=15)
        def update_temp(*args):
            try:
                val = float(self.temperature_var.get())
            except:
                val = 0.7
            temp_scale.set(val)
            self.temp_label.configure(text=f"{val:.2f}")
        self.temperature_var.trace_add("write", update_temp)
        def on_scale_change(value):
            self.temperature_var.set(f"{value:.2f}")
            self.temp_label.configure(text=f"{value:.2f}")
        temp_scale.configure(command=on_scale_change)

        # Макс. новых токенов
        ctk.CTkLabel(self.generation_tab, text="Макс. длина новости (токенов):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.max_tokens_var = ctk.StringVar()
        ctk.CTkEntry(self.generation_tab, textvariable=self.max_tokens_var, width=100).pack(anchor="w", padx=15, pady=5)

        # Top-k
        ctk.CTkLabel(self.generation_tab, text="Top-k (1-100):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.top_k_var = ctk.StringVar()
        ctk.CTkEntry(self.generation_tab, textvariable=self.top_k_var, width=100).pack(anchor="w", padx=15, pady=5)

        # Top-p
        ctk.CTkLabel(self.generation_tab, text="Top-p (0.0-1.0):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.top_p_var = ctk.StringVar()
        ctk.CTkEntry(self.generation_tab, textvariable=self.top_p_var, width=100).pack(anchor="w", padx=15, pady=5)

        # repetition_penalty
        ctk.CTkLabel(self.generation_tab, text="Штраф за повторения (1.0-2.0):",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.rep_penalty_var = ctk.StringVar()
        ctk.CTkEntry(self.generation_tab, textvariable=self.rep_penalty_var, width=100).pack(anchor="w", padx=15, pady=5)

    def create_export_tab(self):
        # Папка по умолчанию
        ctk.CTkLabel(self.export_tab, text="Папка для экспорта по умолчанию:",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(15, 0))
        dir_frame = ctk.CTkFrame(self.export_tab, fg_color="transparent")
        dir_frame.pack(anchor="w", padx=15, pady=5, fill="x")
        self.export_dir_var = ctk.StringVar()
        ctk.CTkEntry(dir_frame, textvariable=self.export_dir_var, width=300).pack(side="left", padx=(0, 5))
        ctk.CTkButton(dir_frame, text="Обзор...", command=self.browse_export_dir, width=80).pack(side="left")

        # Формат по умолчанию
        ctk.CTkLabel(self.export_tab, text="Формат по умолчанию:",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.default_format_combo = ctk.CTkComboBox(self.export_tab, values=["docx", "xlsx"], width=100, state="readonly")
        self.default_format_combo.pack(anchor="w", padx=15, pady=5)

    def create_window_tab(self):
        # Разрешение окна
        ctk.CTkLabel(self.window_tab, text="Разрешение окна:",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(15, 0))
        self.resolution_combo = ctk.CTkComboBox(self.window_tab, values=["1000x700", "800x600", "1200x800", "1400x900", "Полноэкранный"], width=150, state="readonly")
        self.resolution_combo.pack(anchor="w", padx=15, pady=5)

        # Режим отображения
        ctk.CTkLabel(self.window_tab, text="Режим отображения:",
                     font=ctk.CTkFont(size=13), text_color=COLOR_TEXT).pack(anchor="w", padx=15, pady=(10, 0))
        self.mode_combo = ctk.CTkComboBox(self.window_tab, values=["Обычный", "Развёрнуто на весь экран", "На весь экран (F11)"], width=150, state="readonly")
        self.mode_combo.pack(anchor="w", padx=15, pady=5)

    def browse_export_dir(self):
        directory = filedialog.askdirectory(title="Выберите папку для экспорта")
        if directory:
            self.export_dir_var.set(directory)

    def load_settings(self):
        self.model_path_var.set(get_setting("model_path", "./finetuned_rugpt3"))
        self.temperature_var.set(get_setting("temperature", "0.7"))
        self.max_tokens_var.set(str(int(get_setting("max_new_tokens", "200"))))
        self.top_k_var.set(str(int(get_setting("top_k", "50"))))
        self.top_p_var.set(get_setting("top_p", "0.9"))
        self.rep_penalty_var.set(get_setting("repetition_penalty", "1.2"))
        self.export_dir_var.set(get_setting("export_default_dir", ""))
        self.default_format_combo.set(get_setting("default_export_format", "docx"))
        self.resolution_combo.set(get_setting("window_resolution", "1000x700"))
        self.mode_combo.set(get_setting("window_mode", "Обычный"))

    def save_all_settings(self):
        set_setting("model_path", self.model_path_var.get(), self.user_data['id'])
        set_setting("temperature", self.temperature_var.get(), self.user_data['id'])
        set_setting("max_new_tokens", self.max_tokens_var.get(), self.user_data['id'])
        set_setting("top_k", self.top_k_var.get(), self.user_data['id'])
        set_setting("top_p", self.top_p_var.get(), self.user_data['id'])
        set_setting("repetition_penalty", self.rep_penalty_var.get(), self.user_data['id'])
        set_setting("export_default_dir", self.export_dir_var.get(), self.user_data['id'])
        set_setting("default_export_format", self.default_format_combo.get(), self.user_data['id'])
        set_setting("window_resolution", self.resolution_combo.get(), self.user_data['id'])
        set_setting("window_mode", self.mode_combo.get(), self.user_data['id'])

        show_centered_dialog(self, "Успех", "Настройки сохранены.", "success")
        if self.apply_window_callback:
            self.apply_window_callback()
        self.on_back()