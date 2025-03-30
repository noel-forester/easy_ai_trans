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
    api_key = config["API"]["chatgpt_key"]
    client = OpenAI(api_key=api_key)

    t0 = time.time()
    base64_image = encode_image_to_base64(image_path)
    t1 = time.time()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "この画像に含まれる英語を日本語に翻訳してください。ゲームテキスト的な文脈を想定してね。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ],
            }
        ],
        max_tokens=1000
    )
    t2 = time.time()

    result = response.choices[0].message.content

#    print(f"🖼️ エンコード時間: {t1 - t0:.2f}s")
#    print(f"🌐 API応答時間: {t2 - t1:.2f}s")

    # 🔽ここが実行されるように！
    txt_path = image_path.replace(".png", ".txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result)

    return result, t1 - t0, t2 - t1
