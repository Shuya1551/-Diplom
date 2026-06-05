import pandas as pd
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

# === ПАРАМЕТРЫ ===
BASE_MODEL_PATH = "./ruGPT3_finetuned_advanced"
MANUAL_CSV = "manual_pairs.csv"
OUTPUT_DIR = "./ruGPT3_manual_finetuned"

# === ЗАГРУЗКА ДАННЫХ ===
df = pd.read_csv(MANUAL_CSV)
df["text"] = df["input_text"] + " Новость: " + df["output_text"]
print(f"Загружено {len(df)} примеров")

# === ТОКЕНИЗАТОР ===
tokenizer = GPT2Tokenizer.from_pretrained(BASE_MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token

# === ДАТАСЕТ ===
dataset = Dataset.from_pandas(df[["text"]])

def tokenize_function(examples):
    tokenized = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=256,                   
    )
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# === МОДЕЛЬ ===
model = GPT2LMHeadModel.from_pretrained(BASE_MODEL_PATH)
model.gradient_checkpointing_enable()

# === ОБУЧЕНИЕ  ===
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,                # папка для чекпоинтов и финальной модели
    num_train_epochs=10,                  # Количество эпох (полных проходов по всему датасету)                 
    per_device_train_batch_size=1,        # Размер батча на одном устройстве (GPU/CPU)
    gradient_accumulation_steps=4,        # Аккумулирование градиентов: обработаем 4 маленьких батча (по 1 примеру) и потом сделаем одно обновление весов
    learning_rate=5e-5,                   # Скорость обучения (learning rate) – насколько сильно меняем веса на каждом шаге
    warmup_steps=10,                      # первые 10 шагов LR растёт от 0 до заданного (плавный старт)
    logging_steps=5,                      # каждые 5 шагов выводим значение функции потерь (loss)
    save_steps=50,                        # каждые 50 шагов сохраняем временную модель (чекпоинт)
    save_total_limit=2,                   # храним не более 2 последних чекпоинтов (экономит место)
    fp16=torch.cuda.is_available(),       # автоматически используем смешанную точность (float16) если есть GPU – ускоряет и экономит память
    report_to="none",                     # не отправляем логи на внешние сервисы (wandb и т.п.)
)
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"✅ Модель сохранена в {OUTPUT_DIR}")