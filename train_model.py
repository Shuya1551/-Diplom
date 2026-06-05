"""
train_model.py
Дообучение ruGPT-3 Medium на датасете advanced_dataset.jsonl
Формат датасета: {"prompt": "...", "completion": "..."}
Промпт содержит поля с точками в конце, завершается словом "Новость:".
"""

import os
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2TokenizerFast,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

def main():
    # ================== ПУТИ И ПАРАМЕТРЫ ==================
    MODEL_PATH = "./ruGPT3medium_based_on_gpt2"   # путь к исходной модели
    DATASET_FILE = "advanced_dataset.jsonl"       # сгенерированный датасет
    OUTPUT_DIR = "./ruGPT3_finetuned_advanced"    # папка для сохранения дообученной модели
    
    # Гиперпараметры
    EPOCHS = 3                     # Количество полных проходов по датасету
    BATCH_SIZE = 1                 # Количество примеров за один шаг
    GRAD_ACCUM = 4                 # Аккумулируем градиенты 4 шага → эффективный батч = 4
    MAX_LENGTH = 384               # Максимальная длина в токенах
    LEARNING_RATE = 3e-5           # Скорость обучения (3*10^-5)
    WARMUP_STEPS = 100             # Шаги прогрева (learning_rate плавно возрастает)
    LOGGING_STEPS = 50             # Каждые 50 шагов выводим loss (функция потерь) в консоль
    SAVE_STEPS = 500               # Каждые 500 шагов сохраняем промежуточную модель

    # ================== ЗАГРУЗКА ДАТАСЕТА ==================
    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(f"Датасет {DATASET_FILE} не найден.")
    print(f"📥 Загрузка датасета из {DATASET_FILE}...")
    dataset = Dataset.from_json(DATASET_FILE)
    print(f"✅ Загружено {len(dataset)} примеров.")

    # ================== ТОКЕНИЗАТОР ==================
    print("🔧 Загрузка токенизатора...")
    tokenizer = GPT2TokenizerFast.from_pretrained(MODEL_PATH)
    # заполняет пустые места в тексте, чтобы модель могла обработать целый пакет за раз
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # ================== ФУНКЦИЯ ТОКЕНИЗАЦИИ ==================
    def tokenize_function(examples):
        full_texts = [p + " " + c for p, c in zip(examples["prompt"], examples["completion"])]
        model_inputs = tokenizer(
            full_texts,
            truncation=True, #обрезание текста до заданной максимальной длины
            max_length=MAX_LENGTH,
            padding="max_length"
        )
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs

    print("⚙️ Токенизация...")
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        num_proc=1                     # для Windows
    )
    print("✅ Токенизация завершена.")

    # ================== МОДЕЛЬ ==================
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🤖 Загрузка модели на {device}...")
    model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)
    model.to(device)
    model.gradient_checkpointing_enable()   # экономия памяти

    # ================== НАСТРОЙКИ ОБУЧЕНИЯ ==================
    # TrainingArguments – главный объект, управляющий процессом обучения
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,                # куда сохранять чекпоинты
        num_train_epochs=EPOCHS,              # число эпох
        per_device_train_batch_size=BATCH_SIZE,   # батч на одно устройство (GPU/CPU)
        gradient_accumulation_steps=GRAD_ACCUM,   # аккумулируем градиенты, эмулируя больший батч
        learning_rate=LEARNING_RATE,          # шаг градиентного спуска
        warmup_steps=WARMUP_STEPS,            # шагов прогрева learning rate
        logging_steps=LOGGING_STEPS,          # как часто логировать loss
        save_steps=SAVE_STEPS,                # как часто сохранять промежуточные модели
        save_total_limit=2,                   # хранить только 2 последних чекпоинта
        fp16=torch.cuda.is_available(),       # смешанная точность (ускоряет на GPU, поддерживающем fp16)
        dataloader_num_workers=0,             # число процессов для загрузки данных (0 – основной процесс)
        report_to="none",                     # не отправлять логи на внешние сервисы
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False) # преобразует батчи в формат, понятный модели

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # ================== ЗАПУСК ОБУЧЕНИЯ ==================
    print("\n Начало обучения...")
    trainer.train()

    # ================== СОХРАНЕНИЕ МОДЕЛИ ==================
    print(f"\n💾 Сохранение модели в {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("✅ Дообучение завершено!")

    # ================== БЫСТРЫЙ ТЕСТ ==================
    print("\n🧪 Тестовая генерация...")
    test_model = GPT2LMHeadModel.from_pretrained(OUTPUT_DIR).to(device)
    test_tokenizer = GPT2TokenizerFast.from_pretrained(OUTPUT_DIR)
    test_tokenizer.pad_token = test_tokenizer.eos_token

    # Пример промпта
    test_prompt = "Название мероприятия: Хакатон по искусственному интеллекту. Дата: 15.06.2025. Время: 10:00. Место проведения: Москва. Категория: Хакатон. Описание: Участники создадут прототипы нейросетей. Новость:"
    inputs = test_tokenizer(test_prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
    with torch.no_grad():
        outputs = test_model.generate(
            inputs.input_ids,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=test_tokenizer.eos_token_id
        )
    generated = test_tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Промпт: {test_prompt}\nСгенерировано: {generated}\n")

if __name__ == "__main__":
    main()