"""LoRA fine-tuning TEMPLATE. NOT RUN in this project's sandbox (no GPU). Run it on a GPU machine (e.g. a free Colab/Kaggle T4
for a 1-4B model with 4-bit loading, or a rented A100 for 12B):
    pip install transformers peft trl datasets bitsandbytes accelerate
    python training/build_dataset.py
    python training/lora_finetune.py --base <HF model id> --out training/out/lora
Check the base model's licence first. A *base* model (not "-it"/"instruct") must be instruction-tuned like this before it can chat.
Library APIs change between versions; treat this as a starting point and read the current TRL docs."""
import argparse, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Hugging Face model id of the open model to tune")
    ap.add_argument("--data", default=os.path.join(os.path.dirname(__file__), "out", "train.jsonl"))
    ap.add_argument("--val", default=os.path.join(os.path.dirname(__file__), "out", "val.jsonl"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "out", "lora"))
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=16)
    a = ap.parse_args()

    import torch
    from datasets import load_dataset
    from peft import LoraConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    tok = AutoTokenizer.from_pretrained(a.base)
    model = AutoModelForCausalLM.from_pretrained(
        a.base, device_map="auto",
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16))
    ds = load_dataset("json", data_files={"train": a.data, "validation": a.val})
    trainer = SFTTrainer(
        model=model, tokenizer=tok, train_dataset=ds["train"], eval_dataset=ds["validation"],
        peft_config=LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05, task_type="CAUSAL_LM", target_modules="all-linear"),
        args=SFTConfig(output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr, per_device_train_batch_size=4,
                       gradient_accumulation_steps=4, logging_steps=20, eval_strategy="epoch", save_strategy="epoch", bf16=True))
    trainer.train()
    trainer.save_model(a.out)
    print("LoRA adapter saved to", a.out, "- merge it, serve it with vLLM, then evaluate with eval/run_eval.py --live")


if __name__ == "__main__":
    main()
