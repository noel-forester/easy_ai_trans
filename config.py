import configparser
import os

CONFIG_PATH = "config.ini"

default_config = {
    "API": {
        "provider": "ChatGPT",
        "chatgpt_key": "",
        "gemini_key": ""
    },
    "Shortcut": {
        "hotkey": "ctrl+alt+t"
    }
}

def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        config.read_dict(default_config)
        save_config(config)
    else:
        config.read(CONFIG_PATH, encoding="utf-8")
    return config

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        config.write(f)
