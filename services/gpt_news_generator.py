"""
Модуль для работы с генератором новостей на основе локальной модели ruGPT-3 Medium.
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from repositories.settings_repository import get_setting

class GPTNewsGenerator:
    # загружаем дообученную модель
    LOCAL_MODEL_PATH = "./finetuned_rugpt3"

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Загрузка ДООБУЧЕННОЙ модели ruGPT-3...")

        try:
            # Загружаем токенизатор и модель из локальной папки
            self.tokenizer = GPT2Tokenizer.from_pretrained(self.LOCAL_MODEL_PATH)
            # Для GPT-2 моделей нужно добавить паддинг
            self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = GPT2LMHeadModel.from_pretrained(
                self.LOCAL_MODEL_PATH,
                torch_dtype=torch.float32
            ).to(self.device)

            self.model.eval()
            print("Модель ruGPT-3 Medium успешно загружена!")

        except Exception as e:
            print(f"Критическая ошибка при загрузке модели: {e}")
            raise

    def generate_news(self, plan_data: dict) -> str:
        """
        Генерирует текст новости на основе данных плана.
        """
        title = plan_data.get('title', 'мероприятие')
        location = plan_data.get('location', '')
        description = plan_data.get('description', '')
        speaker = plan_data.get('speaker', '')

        # Формируем "запрос" (промпт) для GPT-модели
        prompt = (
            f"<s>Сгенерируй новостное сообщение о мероприятии по плану:\n"
            f"Название: {title}\nМесто: {location}\nО чём: {description}\nСпикер: {speaker}\n"
            f"Новость:"
        )

        # Токенизируем запрос
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)

            # Получаем настройки из БД (с значениями по умолчанию)
        temperature = float(get_setting("temperature", "0.7"))
        max_new_tokens = int(get_setting("max_new_tokens", "200"))
        top_k = int(get_setting("top_k", "50"))
        top_p = float(get_setting("top_p", "0.9"))
        repetition_penalty = float(get_setting("repetition_penalty", "1.2"))

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=True,               # Включаем вариативность
                temperature=temperature,              # Контролируем "смелость" модели
                top_k=top_k,                     # Ограничиваем выбор самых вероятных токенов
                top_p=top_p,                    # Используем nucleus sampling
                repetition_penalty=repetition_penalty,       # Штрафуем за повторения
                no_repeat_ngram_size=3,       # Запрещаем повторять 3-граммы
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Декодируем сгенерированный текст
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Извлекаем только часть после "Новость:"
        if "Новость:" in generated_text:
            generated_text = generated_text.split("Новость:")[-1].strip()

        return generated_text