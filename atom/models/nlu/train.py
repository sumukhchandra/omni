import os
import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import torch
from datasets import load_dataset
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer,
    Trainer,
    TrainingArguments,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "t5-small"
DATA_FILE = os.path.join("data", "nlu", "nlu_dataset_50k.jsonl")
OUTPUT_DIR = os.path.join("models", "nlu", "saved_model")
MAX_SOURCE_LENGTH = 128
MAX_TARGET_LENGTH = 128

def preprocess_function(examples, tokenizer):
    inputs = examples["text"]
    targets = []
    
    # Format target: "INTENT: PLAY_MUSIC | ENTITIES: song=baby, app=spotify"
    for intent, entities_dict in zip(examples["intent"], examples["entities"]):
        entity_str = ", ".join([f"{k}={v}" for k, v in entities_dict.items()])
        target_str = f"INTENT: {intent}"
        if entity_str:
            target_str += f" | ENTITIES: {entity_str}"
        targets.append(target_str)

    model_inputs = tokenizer(inputs, max_length=MAX_SOURCE_LENGTH, truncation=True, padding="max_length")
    labels = tokenizer(targets, max_length=MAX_TARGET_LENGTH, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

def train():
    logger.info("Loading tokenizer...")
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)

    logger.info(f"Loading dataset from {DATA_FILE}...")
    dataset = load_dataset("json", data_files=DATA_FILE, split="train")

    # Split dataset
    dataset = dataset.train_test_split(test_size=0.1)
    train_dataset = dataset["train"]
    val_dataset = dataset["test"]

    logger.info("Preprocessing dataset...")
    train_dataset = train_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)
    val_dataset = val_dataset.map(lambda x: preprocess_function(x, tokenizer), batched=True)

    logger.info("Loading model...")
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        evaluation_strategy="epoch",
        learning_rate=2e-4,
        per_device_train_batch_size=8, # Small batch size for standard laptops
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_dir='./logs',
        logging_steps=100,
        use_cpu=not torch.cuda.is_available(), # Auto-detect GPU
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )

    logger.info("Starting training...")
    trainer.train()

    logger.info(f"Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    logger.info("Training complete.")

if __name__ == "__main__":
    train()
