import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from datasets import load_dataset
from trl import SFTTrainer
from accelerate import Accelerator
import logging

# Set up logging to file
logging.basicConfig(
    filename='finetune_courses.txt',  # Log output will be written to this file
    filemode='w',  # 'w' to overwrite the log file each run, use 'a' to append
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

# Initialize the accelerator
accelerator = Accelerator()

# Model and tokenizer names
base_model_name = "meta-llama/Llama-2-7b-chat-hf"
new_model_name = "llama-2-7b-chat-hf-courses"

logging.info("Initializing model and tokenizer.")


# Tokenizer
llama_tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
llama_tokenizer.pad_token = llama_tokenizer.eos_token
llama_tokenizer.padding_side = "right"

# Load the model
base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
base_model.config.use_cache = False
base_model.config.pretraining_tp = 1

# Move model to GPUs using `Accelerator`
model = accelerator.prepare(base_model)

# Data
training_data = load_dataset("json", data_files="/app/data/instruction_dataset.json", split="train")
#training_data = load_dataset(data_name, split="train")

# LoRA Config
peft_parameters = LoraConfig(
    lora_alpha=8,
    lora_dropout=0.1,
    r=8,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(base_model, peft_parameters)
model.print_trainable_parameters()

# Training Params
train_params = TrainingArguments(
    output_dir="./results_modified",
    num_train_epochs=5,
    per_device_train_batch_size=2,  # Batch size per GPU
    gradient_accumulation_steps=1,
    optim="paged_adamw_32bit",
    save_steps=500,
    logging_steps=50,
    learning_rate=1e-5,
    weight_decay=0.001,
    fp16=True,  # Use mixed precision to save memory
    max_grad_norm=0.3,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="constant",
    report_to="tensorboard"
)

logging.info("Starting the training process.")

# Trainer with LoRA configuration and multi-GPU setup
fine_tuning = SFTTrainer(
    model=model,
    train_dataset=training_data,
    peft_config=peft_parameters,
    dataset_text_field="text",
    tokenizer=llama_tokenizer,
    args=train_params
)

# Training
fine_tuning.train()

logging.info("Saving the fine-tuned model.")
# Save Model
fine_tuning.model.save_pretrained(new_model_name)
fine_tuning.tokenizer.save_pretrained(new_model_name)
logging.info("Training completed and model saved successfully.")