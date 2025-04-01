import configparser
import os

CONFIG_PATH = "config.ini"

default_config = {
    "API": {
        # "provider": "ChatGPT",
        "chatgpt_key": "",
        "gemini_key": "",
        "chatgpt_model": "gpt-4o",
        "gemini_model": "models/gemini-1.5-pro",
        "prompt": "この画像に含まれる英語を日本語に翻訳してください。ゲームテキスト的な文脈を想定してね。",
        "chatgpt_model_list": "",
        "gemini_model_list": "",
    },
    "LOG": {
        "show_timing_logs": "True"
    },
    "UI": {
        "font_size": "10"
    }
}

def load_config():
    config = configparser.ConfigParser()
    config.optionxform = str
    if not os.path.exists(CONFIG_PATH):
        config.read_dict(default_config)
        save_config(config)
    else:
        config.read(CONFIG_PATH, encoding="utf-8")
        
    return config

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)
