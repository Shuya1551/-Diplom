# train_model.py
"""
Скрипт для дообучения ruGPT-3 Medium локально (VS Code).
Требования: установлены библиотеки transformers, torch, datasets, pandas.
Для ускорения желательно наличие GPU (CUDA).
"""

import os
import sys
import argparse
import pandas as pd
import torch
from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune ruGPT-3 Medium for news generation")
    parser.add_argument("--data_file", type=str, default="train_data.csv", 
                        help="Path to CSV file with columns 'input_text' and 'output_text'")
    parser.add_argument("--output_dir", type=str, default="./finetuned_rugpt3", 
                        help="Directory to save fine-tuned model")
    parser.add_argument("--model_name", type=str, default="sberbank-ai/rugpt3medium_based_on_gpt2", 
                        help="Base model name")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per device batch size (reduce if OOM)")
    parser.add_argument("--grad_accum", type=int, default=2, help="Gradient accumulation steps")
    parser.add_argument("--max_length", type=int, default=128, help="Max token length for truncation/padding")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Learning rate")
    parser.add_argument("--warmup_steps", type=int, default=100, help="Warmup steps")
    return parser.parse_args()

def create_prompt_and_response(row):
    """Формирует строку для обучения: 'input_text + Новость: + output_text'"""
    prompt = row['input_text'] + " Новость:"
    full_text = prompt + " " + row['output_text']
    return full_text

def main():
    args = parse_args()
    
    # Проверка наличия файла данных
    if not os.path.exists(args.data_file):
        print(f"Ошибка: файл данных {args.data_file} не найден.")
        sys.exit(1)
    
    # Определение устройства
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Используется устройство: {device}")
    if device.type == "cpu":
        print("ВНИМАНИЕ: Обучение на CPU будет очень медленным. Рекомендуется использовать GPU (CUDA).")
        print("Если у вас нет GPU, рассмотрите уменьшение batch_size и max_length.")
    
    # Загрузка датасета
    print(f"Загрузка данных из {args.data_file}...")
    df = pd.read_csv(args.data_file)
    if not {'input_text', 'output_text'}.issubset(df.columns):
        print("Ошибка: CSV файл должен содержать колонки 'input_text' и 'output_text'.")
        sys.exit(1)
    
    # Формирование текстов для обучения
    df['text'] = df.apply(create_prompt_and_response, axis=1)
    print(f"Загружено {len(df)} примеров. Пример:")
    print(df['text'].iloc[0][:200] + "...")
    
    dataset = Dataset.from_pandas(df[['text']])
    
    # Загрузка модели и токенизатора
    print(f"Загрузка модели {args.model_name}...")
    tokenizer = GPT2Tokenizer.from_pretrained(args.model_name)
    model = GPT2LMHeadModel.from_pretrained(args.model_name)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Токенизация
    def tokenize_function(examples):
        tokenized = tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=args.max_length,
            return_tensors="pt"
        )
        tokenized["labels"] = tokenized["input_ids"].clone()
        return tokenized
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])
    
    # Настройки обучения
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_steps=args.warmup_steps,
        learning_rate=args.learning_rate,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=50,
        save_strategy="epoch",
        save_total_limit=2,
        fp16=torch.cuda.is_available(),  # автоматическое использование fp16 если есть GPU
        report_to="none",
    )
    
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
    )
    
    # Обучение
    print("Начинаем обучение...")
    trainer.train()
    
    # Сохранение модели
    print(f"Сохраняем модель в {args.output_dir}")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    
    print("Обучение завершено!")

if __name__ == "__main__":
    main()