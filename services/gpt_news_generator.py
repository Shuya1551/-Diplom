"""
Модуль для работы с генератором новостей на основе локальной модели ruGPT-3 Medium.
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from services.file_storage import get_setting   # изменён импорт

class GPTNewsGenerator:
    LOCAL_MODEL_PATH = "./finetuned_rugpt3"

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Загрузка ДООБУЧЕННОЙ модели ruGPT-3...")

        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(
                self.LOCAL_MODEL_PATH,
                clean_up_tokenization_spaces=False
            )
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
        title = plan_data.get('title', 'мероприятие')
        location = plan_data.get('location', '')
        description = plan_data.get('description', '')
        speaker = plan_data.get('speaker', '')
        audience = plan_data.get('audience', '')
        organizer = plan_data.get('organizer', '')
        format_type = plan_data.get('format_type', '')
        goal = plan_data.get('goal', '')

        prompt = (
            f"<s>Сгенерируй новостное сообщение о мероприятии по плану:\n"
            f"Название: {title}\n"
            f"Место: {location}\n"
            f"Формат: {format_type}\n"
            f"О чём: {description}\n"
            f"Цель: {goal}\n"
            f"Спикеры: {speaker}\n"
            f"Аудитория: {audience}\n"
            f"Организатор: {organizer}\n"
            f"Новость:"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)

        temperature = float(get_setting("temperature", "0.7"))
        max_new_tokens = int(get_setting("max_new_tokens", "200"))
        top_k = int(get_setting("top_k", "50"))
        top_p = float(get_setting("top_p", "0.9"))
        repetition_penalty = float(get_setting("repetition_penalty", "1.2"))

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=3,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        if "Новость:" in generated_text:
            generated_text = generated_text.split("Новость:")[-1].strip()

        return generated_text