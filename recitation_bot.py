import os
import time
import random
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip, VideoFileClip, concatenate_videoclips,
    CompositeVideoClip, ImageClip
)
import numpy as np

# === CONFIG ===
PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")
FONT_PATH = "Tinos-Bold.ttf"
AUDIO_FOLDER = "quran_audio"
VIDEO1 = "r1.mp4"
VIDEO2 = "r2.mp4"
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")  # Replace with real ID


# Utility: Share to Telegram and delete after

def share_to_telegram(caption, media_path, telegram_token, telegram_chat_id):
    try:
        url = None
        files = {}
        if media_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
            files = {'photo': open(media_path, 'rb')}
        elif media_path.lower().endswith(('.mp4', '.mov')):
            url = f"https://api.telegram.org/bot{telegram_token}/sendVideo"
            files = {'video': open(media_path, 'rb')}
        else:
            print("Unsupported format")
            return

        data = {'chat_id': telegram_chat_id, 'caption': caption}
        r = requests.post(url, files=files, data=data)
        print("Telegram Status:", r.status_code)

    except Exception as e:
        print("Telegram error:", e)
    finally:
        try:
            if os.path.exists(media_path):
                os.remove(media_path)
                print("Deleted:", media_path)
        except Exception as e:
            print("Could not delete media:", e)

# Helper: Create text image overlay

def create_text_image(text, size, font_size=150, font_path=FONT_PATH):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[1] - bbox[0]
    text_height = bbox[2] - bbox[1]
    x = (size[0] - text_width) // 2 - bbox[0]
    y = (size[1] - text_height) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill="white")
    return np.array(img)


# === Quran Recitation Video Posting ===
# Picks a random short MP3 from audio folder and creates a video overlayed with Surah & Reciter name

def post_quran_recitation(index):
    # === Audio selection ===

    valid_audio_files = []
    for root, _, files in os.walk(AUDIO_FOLDER):
        for file in files:
            if file.endswith(".mp3"):
                path = os.path.join(root, file)
                try:
                    clip = AudioFileClip(path)
                    if clip.duration <= 1200:
                        valid_audio_files.append(path)
                    clip.close()
                except:
                    continue

    if not valid_audio_files:
        print("❌ No valid audio files found.")
        return

    selected_audio = random.choice(valid_audio_files)
    audio_clip = AudioFileClip(selected_audio)

    filename = os.path.basename(selected_audio).replace(".mp3", "")
    parts = selected_audio.replace("\\", "/").split("/")
    reciter = parts[-3] if "Juzz" in parts[-2] else parts[-2]
    surah = filename.replace("-", " ")

    # === Video Creation ===
        # Concatenate r1.mp4 and r2.mp4, then add audio and text overlay

    clip1 = VideoFileClip(VIDEO1).without_audio()
    clip2 = VideoFileClip(VIDEO2).without_audio()
    combined_video = concatenate_videoclips([clip1, clip2]).set_audio(audio_clip)
    final_video = combined_video.subclip(0, audio_clip.duration)

    text_image = create_text_image(f"Surah: {surah}  |  Reciter: {reciter}", (final_video.w, 80))
    text_clip = ImageClip(text_image).set_position("center").set_duration(audio_clip.duration)

    output = CompositeVideoClip([final_video, text_clip])
    output_path = f"final_quran_video_{random.randint(1000,9999)}.mp4"
    output.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

    caption = f"""
🎵 কুরআন তিলাওয়াত ভিডিও

📖 সূরা: {surah}
🎤 {reciter}

📍 প্রতিদিন শুনুন কুরআনের আয়াত
📌 আমাদের পেজে লাইক দিন: হিদায়াহ

#QuranRecitation #হিদায়াহ #QuranVideo #IslamicReminder #DailyQuran
""".strip()

    try:
        # === Step 1: Upload video with published=false
        with open(output_path, "rb") as video_file:
            upload_url = f"https://graph-video.facebook.com/v18.0/{PAGE_ID}/videos"
            upload_params = {
                "access_token": ACCESS_TOKEN,
                "published": "false"
            }
            upload_files = {
                "source": ("recitation.mp4", video_file, "video/mp4")
            }
            upload_response = requests.post(upload_url, params=upload_params, files=upload_files)
            upload_data = upload_response.json()
            media_id = upload_data.get("id")

        if not media_id:
            print("❌ Could not upload video:", upload_data)
            return

        # === Step 2: Post to feed using attached_media
        post_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        post_params = {
            "access_token": ACCESS_TOKEN,
            "attached_media": json.dumps([{"media_fbid": media_id}]),
            "message": caption
        }
        post_response = requests.post(post_url, data=post_params)
        print(f"✅ Posted Recitation #{index} — Status: {post_response.status_code}")
        print("🟩 Response:", post_response.json())

        # === Step 3: Share to Telegram and Delete
            # After posting, clean up local video file to save disk space

        share_to_telegram(caption, output_path, telegram_token, telegram_chat_id)
        time.sleep(2)
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"🗑️ Deleted video file: {output_path}")

    except Exception as e:
        print("❌ Post Recitation Error:", e)

# === POST LOOP ===
# Posts every hour in this order: Recitation → Hadith → QA → Ayah → (repeat)

from main_bot import post_quran_ayah, post_hadith, post_qa  # move these to the top!

index = 1  # always begin with 1 if not defined

while True:
    print(f"\n🔁 Posting Index: {index}")
    try:
        if index % 4 == 1:
            print("🎧 Posting Quran Recitation")
            post_quran_recitation(index)

        elif index % 4 == 2:
            print("📜 Posting Hadith")
            post_hadith(index)

        elif index % 4 == 3:
            print("❓ Posting QA")
            post_qa(index)
        else:
            print("🕋 Posting Quran Ayah")
            post_quran_ayah(index)

    except Exception as e:
        print("Global Post Error:", e)

    index += 1
    time.sleep(3600)
