from PIL import ImageGrab
import mss
import os
from PIL import Image
from datetime import datetime
import base64
import time
import openai
from openai import OpenAI
from config import load_config



def capture_screen(mode="full", region=None, monitor_index=1):
    now = datetime.now()
    filename = now.strftime("history/%Y%m%d-%H%M%S.png")

    if not os.path.exists("history"):
        os.makedirs("history")

    with mss.mss() as sct:
        monitor = sct.monitors[monitor_index]  # 0=仮想全体, 1=メイン, 2=サブ
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        if region:
            x, y, w, h = region
            # Crop region 相対にする
            crop_box = (x - monitor["left"], y - monitor["top"],
                        x - monitor["left"] + w, y - monitor["top"] + h)
            cropped = img.crop(crop_box)
            cropped.save(filename)
        else:
            img.save(filename)

    return filename
    
def encode_image_to_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def translate_image(image_path):
    config = load_config()
    provider = config["API"].get("provider", "ChatGPT")
    prompt = config["API"].get("prompt", "この画像に含まれる英語を日本語に翻訳してください。ゲームテキスト的な文脈を想定してね。")

    t0 = time.time()
    base64_image = encode_image_to_base64(image_path)
    t1 = time.time()

    results = []
    api_time_total = 0

    if provider in ("ChatGPT", "Both"):
        try:
            chat_model = config["API"].get("chatgpt_model", "gpt-4o")
            api_key = config["API"].get("chatgpt_key", "")
            if not api_key:
                raise ValueError("ChatGPT APIキーが設定されていません。設定画面から入力してください。")

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=chat_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ],
                    }
                ],
                max_tokens=1000
            )
            chat_result = response.choices[0].message.content
            results.append(f"🔵 ChatGPT（{chat_model}）:\n{chat_result}")
            api_time_total += response.usage.total_tokens / 1000  # 適当な見積もり
        except Exception as e:
            results.append(f"❌ ChatGPTエラー: {e}")

    if provider in ("Gemini", "Both"):
        try:
            from google.generativeai import configure, GenerativeModel
            gemini_model = config["API"].get("gemini_model", "models/gemini-1.5-pro")
            gemini_key = config["API"].get("gemini_key", "")
            if not gemini_key:
                raise ValueError("Gemini APIキーが設定されていません。設定画面から入力してください。")

            configure(api_key=gemini_key)
            model = GenerativeModel(gemini_model)
            response = model.generate_content([
                prompt,
                {
                    "mime_type": "image/png",
                    "data": base64.b64decode(base64_image)
                }
            ])
            gemini_result = response.text
            results.append(f"🟢 Gemini（{gemini_model}）:\n{gemini_result}")
        except Exception as e:
            results.append(f"❌ Geminiエラー: {e}")

    t2 = time.time()
    combined_result = "\n\n".join(results)

    # 保存
    txt_path = image_path.replace(".png", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(combined_result)

    return combined_result, t1 - t0, t2 - t1

