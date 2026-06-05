"""
Модуль для работы с генератором новостей на основе локальной модели ruGPT-3 Medium.
"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from services.file_storage import get_setting

class GPTNewsGenerator:
    def __init__(self, initial_model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.current_model_path = None
        self.tokenizer = None
        self.model = None
        if initial_model_path:
            self.load_model(initial_model_path)

    def load_model(self, model_path):
        """Загружает модель и токенизатор из указанной папки."""
        print(f"Загрузка модели из {model_path}...")
        self.tokenizer = GPT2Tokenizer.from_pretrained(
            model_path,
            clean_up_tokenization_spaces=False
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = GPT2LMHeadModel.from_pretrained(
            model_path,
            torch_dtype=torch.float32
        ).to(self.device)
        self.model.eval()
        self.current_model_path = model_path
        print(f"Модель успешно загружена: {model_path}")

    def switch_model(self, new_model_path):
        """Переключает модель, если путь изменился."""
        if self.current_model_path == new_model_path:
            return
        self.load_model(new_model_path)

    def generate_news(self, plan_data: dict) -> str:
        from datetime import datetime
        import re

        parts = []

        if plan_data.get('title'):
            parts.append(f"Название мероприятия: {plan_data['title']}")
        if plan_data.get('event_date'):
            try:
                date_obj = datetime.strptime(plan_data['event_date'], "%Y-%m-%d")
                date_str = date_obj.strftime("%d.%m.%Y")
            except:
                date_str = plan_data['event_date']
            parts.append(f"Дата: {date_str}")
        if plan_data.get('event_time'):
            time_str = plan_data['event_time']
            if len(time_str) > 5:
                time_str = time_str[:5]
            parts.append(f"Время: {time_str}")
        if plan_data.get('event_end_time'):
            end_str = plan_data['event_end_time']
            if len(end_str) > 5:
                end_str = end_str[:5]
            parts.append(f"Окончание: {end_str}")
        if plan_data.get('location'):
            parts.append(f"Место проведения: {plan_data['location']}")
        if plan_data.get('format_type'):
            parts.append(f"Формат: {plan_data['format_type']}")
        if plan_data.get('category'):
            parts.append(f"Категория: {plan_data['category']}")
        if plan_data.get('participants_count'):
            parts.append(f"Количество участников: {plan_data['participants_count']}")
        if plan_data.get('description'):
            parts.append(f"Описание: {plan_data['description']}")
        if plan_data.get('goal'):
            parts.append(f"Цель: {plan_data['goal']}")
        if plan_data.get('speaker'):
            parts.append(f"Спикер(ы): {plan_data['speaker']}")
        if plan_data.get('audience'):
            parts.append(f"Аудитория: {plan_data['audience']}")
        if plan_data.get('organizer'):
            parts.append(f"Организатор: {plan_data['organizer']}")

        if not parts:
            return "Недостаточно данных."

        prompt = ". ".join(parts) + ". Новость:"

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)

        temperature = float(get_setting("temperature", "0.3"))
        max_new_tokens = int(get_setting("max_new_tokens", "150"))
        top_k = int(get_setting("top_k", "50"))
        top_p = float(get_setting("top_p", "0.9"))
        repetition_penalty = float(get_setting("repetition_penalty", "1.1"))

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

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "Новость:" in generated:
            generated = generated.split("Новость:")[-1].strip()
        if generated.endswith(".Новость:"):
            generated = generated[:-9].strip()

        # ========== РАСШИРЕННАЯ ПОСТОБРАБОТКА ==========

        # 1. Извлечение правильных значений из промпта
        correct_participants = None
        participants_match = re.search(r'Количество участников: (\d+)', prompt)
        if participants_match:
            correct_participants = participants_match.group(1)

        correct_date = None
        date_match = re.search(r'Дата: (\d{2}\.\d{2}\.\d{4})', prompt)
        if date_match:
            correct_date = date_match.group(1)

        correct_start = None
        start_match = re.search(r'Время: (\d{2}:\d{2})', prompt)
        if start_match:
            correct_start = start_match.group(1)

        correct_end = None
        end_match = re.search(r'Окончание: (\d{2}:\d{2})', prompt)
        if end_match:
            correct_end = end_match.group(1)

        # 2. Замена участников
        if correct_participants:
            generated = re.sub(r'\b\d+\s*участников?', f'{correct_participants} участников', generated)
            generated = re.sub(r'\b\d+\s*человек(?:а)?', f'{correct_participants} человек', generated)

        # 3. Замена даты
        if correct_date:
            generated = re.sub(r'\b\d{1,2}\.\d{1,2}\.\d{2,4}\b', correct_date, generated)

        # 4. Умная замена времени: первое время -> начало, последнее -> окончание
        all_times = list(re.finditer(r'\b(\d{2}:\d{2})\b', generated))
        if correct_start and correct_end:
            # Если есть оба времени
            if len(all_times) >= 2:
                # Заменяем первое на начало, последнее на окончание
                generated = generated[:all_times[0].start()] + correct_start + generated[all_times[0].end():]
                generated = re.sub(r'\b\d{2}:\d{2}\b', correct_start, generated, count=1)
                # Ищем последнее вхождение времени (после замены первого)
                times_after = list(re.finditer(r'\b\d{2}:\d{2}\b', generated))
                if times_after:
                    last = times_after[-1]
                    generated = generated[:last.start()] + correct_end + generated[last.end():]
            elif len(all_times) == 1:
                # Одно время — если в промпте есть окончание, но модель его пропустила, подставим окончание
                if correct_end and correct_start != correct_end:
                    generated = re.sub(r'\b\d{2}:\d{2}\b', correct_end, generated)
        elif correct_start and not correct_end:
            # Только начало
            if all_times:
                generated = re.sub(r'\b\d{2}:\d{2}\b', correct_start, generated, count=1)
        elif correct_end and not correct_start:
            # Только окончание (заменяем последнее)
            if all_times:
                last = all_times[-1]
                generated = generated[:last.start()] + correct_end + generated[last.end():]

        # 5. Удаление повторов предложений (сохраняем порядок, убираем дубли)
        sentences = re.split(r'(?<=[.!?])\s+', generated)
        unique_sentences = []
        for sent in sentences:
            if sent and sent not in unique_sentences:
                unique_sentences.append(sent)
        generated = ' '.join(unique_sentences).strip()

        # 6. Финальная чистка
        generated = re.sub(r'\.{2,}', '.', generated)
        generated = re.sub(r'\s+', ' ', generated).strip()
        if generated and generated[-1] not in '.!?':
            generated += '.'

        return generated