import time
import random
import requests
from PIL import Image, ImageDraw, ImageFont
import os
import json

# === CONFIGURATION ===

# Set Facebook Page ID, Access Token
PAGE_ID = os.getenv("FB_PAGE_ID")
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN")

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Background images
QURAN_BG_DIR = os.path.join(BASE_DIR, "assets", "quranbg")
HADITH_BG_DIR = os.path.join(BASE_DIR, "assets", "hadithbg")
QA_BG_DIR = os.path.join(BASE_DIR, "assets", "qabg")

# fonts
HADITH_FILE = os.path.join(BASE_DIR, "data", "hadiths_bn_fixed.json")
POSTED_TRACKER_FILE = os.path.join(BASE_DIR, "data", "hadith_posted_tracker.json")

FONT_AYAH = os.path.join(BASE_DIR, "assets", "fonts", "Tinos-Bold.ttf")
FONT_FOOTER = os.path.join(BASE_DIR, "assets", "fonts", "Tinos-Bold.ttf")
FONT_ARABIC = os.path.join(BASE_DIR, "assets", "fonts", "Tinos-Bold.ttf")


# === Telegram Config ===
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Replace with your actual bot token
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")  # Replace with your actual channel username or chat ID

# Create Hadith tracker file to prevent reposting the same hadith

if not os.path.exists(POSTED_TRACKER_FILE):
    with open(POSTED_TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

with open(HADITH_FILE, "r", encoding="utf-8") as f:
    all_hadiths = json.load(f)

english_surah_names = {
    1: "Al-Fatiha", 2: "Al-Baqara", 3: "Aal-E-Imran", 4: "An-Nisa", 5: "Al-Ma'idah", 6: "Al-An'am",
    7: "Al-A'raf", 8: "Al-Anfal", 9: "At-Tawbah", 10: "Yunus", 11: "Hud", 12: "Yusuf",
    13: "Ar-Ra'd", 14: "Ibrahim", 15: "Al-Hijr", 16: "An-Nahl", 17: "Al-Isra", 18: "Al-Kahf",
    19: "Maryam", 20: "Taha", 21: "Al-Anbiya", 22: "Al-Hajj", 23: "Al-Mu’minun", 24: "An-Nur",
    25: "Al-Furqan", 26: "Ash-Shu’ara", 27: "An-Naml", 28: "Al-Qasas", 29: "Al-Ankabut",
    30: "Ar-Rum", 31: "Luqman", 32: "As-Sajda", 33: "Al-Ahzab", 34: "Saba", 35: "Fatir",
    36: "Ya-Sin", 37: "As-Saffat", 38: "Sad", 39: "Az-Zumar", 40: "Ghafir", 41: "Fussilat",
    42: "Ash-Shura", 43: "Az-Zukhruf", 44: "Ad-Dukhan", 45: "Al-Jathiya", 46: "Al-Ahqaf",
    47: "Muhammad", 48: "Al-Fath", 49: "Al-Hujurat", 50: "Qaf", 51: "Adh-Dhariyat",
    52: "At-Tur", 53: "An-Najm", 54: "Al-Qamar", 55: "Ar-Rahman", 56: "Al-Waqi'a",
    57: "Al-Hadid", 58: "Al-Mujadila", 59: "Al-Hashr", 60: "Al-Mumtahanah",
    61: "As-Saff", 62: "Al-Jumu’a", 63: "Al-Munafiqoon", 64: "At-Taghabun",
    65: "At-Talaq", 66: "At-Tahrim", 67: "Al-Mulk", 68: "Al-Qalam", 69: "Al-Haqqah",
    70: "Al-Ma'arij", 71: "Nuh", 72: "Al-Jinn", 73: "Al-Muzzammil", 74: "Al-Muddaththir",
    75: "Al-Qiyamah", 76: "Al-Insan", 77: "Al-Mursalat", 78: "An-Naba", 79: "An-Nazi'at",
    80: "Abasa", 81: "At-Takwir", 82: "Al-Infitar", 83: "Al-Mutaffifin", 84: "Al-Inshiqaq",
    85: "Al-Buruj", 86: "At-Tariq", 87: "Al-Ala", 88: "Al-Ghashiyah", 89: "Al-Fajr",
    90: "Al-Balad", 91: "Ash-Shams", 92: "Al-Lail", 93: "Ad-Duhaa", 94: "Ash-Sharh",
    95: "At-Tin", 96: "Al-Alaq", 97: "Al-Qadr", 98: "Al-Bayyina", 99: "Az-Zalzalah",
    100: "Al-Adiyat", 101: "Al-Qari'a", 102: "At-Takathur", 103: "Al-Asr", 104: "Al-Humazah",
    105: "Al-Fil", 106: "Quraish", 107: "Al-Ma'un", 108: "Al-Kawthar", 109: "Al-Kafiroon",
    110: "An-Nasr", 111: "Al-Masad", 112: "Al-Ikhlas", 113: "Al-Falaq", 114: "An-Nas"
}
surah_ayah_counts = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206,
    10: 109, 12: 111, 14: 52, 15: 99, 16: 128, 17: 111,
    18: 110, 19: 98, 20: 135, 21: 112, 23: 118, 24: 64,
    25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 33: 73, 35: 45, 36: 83, 37: 182, 39: 75,
    40: 85, 41: 54, 42: 53, 43: 89, 44: 59, 45: 37,
    46: 35, 48: 29, 49: 18, 50: 45, 51: 60, 52: 49,
    53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22,
    59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18,
    65: 12, 66: 12, 67: 30
}
# Bangla Surah Name Mapping
bangla_surah_names = {
    1: "সূরা ফাতিহা",
    2: "সূরা বাকারা",
    3: "সূরা আলে ইমরান",
    4: "সূরা নিসা",
    5: "সূরা মায়িদা",
    6: "সূরা আনআম",
    7: "সূরা আরাফ",
    8: "সূরা আনফাল",
    9: "সূরা তাওবা",
    10: "সূরা ইউনুস",
    11: "সূরা হুদ",
    12: "সূরা ইউসুফ",
    13: "সূরা রাদ",
    14: "সূরা ইব্রাহীম",
    15: "সূরা হিজর",
    16: "সূরা নাহল",
    17: "সূরা বনী ইসরাইল",
    18: "সূরা কাহফ",
    19: "সূরা মারিয়াম",
    20: "সূরা ত্ব-হা",
    21: "সূরা আম্বিয়া",
    22: "সূরা হাজ্জ",
    23: "সূরা মু’মিনূন",
    24: "সূরা নূর",
    25: "সূরা ফুরকান",
    26: "সূরা আশ-শুআরা",
    27: "সূরা নমল",
    28: "সূরা কাসাস",
    29: "সূরা আনকাবুত",
    30: "সূরা রূম",
    31: "সূরা লোকমান",
    32: "সূরা সাজদা",
    33: "সূরা আহযাব",
    34: "সূরা সাবা",
    35: "সূরা ফাতির",
    36: "সূরা ইয়াসিন",
    37: "সূরা সাফফাত",
    38: "সূরা ছোয়াদ",
    39: "সূরা জুমার",
    40: "সূরা গাফির",
    41: "সূরা ফুসসিলাত",
    42: "সূরা আশ-শুরা",
    43: "সূরা যুখরুফ",
    44: "সূরা দুখান",
    45: "সূরা জাসিয়া",
    46: "সূরা আহকাফ",
    47: "সূরা মুহাম্মদ",
    48: "সূরা ফাতহ",
    49: "সূরা হুজুরাত",
    50: "সূরা কাফ",
    51: "সূরা যারিয়াত",
    52: "সূরা তুর",
    53: "সূরা নাজম",
    54: "সূরা ক্বামার",
    55: "সূরা আর রহমান",
    56: "সূরা ওয়াকিয়া",
    57: "সূরা হাদীদ",
    58: "সূরা মুজাদালাহ",
    59: "সূরা হাশর",
    60: "সূরা মুমতাহিনা",
    61: "সূরা আস-সাফ",
    62: "সূরা জুমা",
    63: "সূরা মুনাফিকুন",
    64: "সূরা তাগাবুন",
    65: "সূরা তালাক",
    66: "সূরা তাহরিম",
    67: "সূরা মুলক",
    68: "সূরা কলম",
    69: "সূরা হাক্কাহ",
    70: "সূরা মাআরিজ",
    71: "সূরা নূহ",
    72: "সূরা জিন",
    73: "সূরা মুযযাম্মিল",
    74: "সূরা মুদ্দাসসির",
    75: "সূরা কেয়ামাহ",
    76: "সূরা ইনসান",
    77: "সূরা মুরসালাত",
    78: "সূরা আন-নাবা",
    79: "সূরা নাযিয়াত",
    80: "সূরা আবাসা",
    81: "সূরা তাকভীর",
    82: "সূরা ইনফিতার",
    83: "সূরা মুতাফফিফিন",
    84: "সূরা ইনশিকাক",
    85: "সূরা বুরূজ",
    86: "সূরা তারিক",
    87: "সূরা আ’লা",
    88: "সূরা গাশিয়াহ",
    89: "সূরা ফজর",
    90: "সূরা বালাদ",
    91: "সূরা শামস",
    92: "সূরা লাইল",
    93: "সূরা দুহা",
    94: "সূরা ইনশিরাহ",
    95: "সূরা ত্বীন",
    96: "সূরা আলাক",
    97: "সূরা কদর",
    98: "সূরা বাইয়্যিনা",
    99: "সূরা জিলযাল",
    100: "সূরা আদিয়াত",
    101: "সূরা ক্বারিয়া",
    102: "সূরা তাকাসুর",
    103: "সূরা আসর",
    104: "সূরা হুমাযাহ",
    105: "সূরা ফীল",
    106: "সূরা কুরাইশ",
    107: "সূরা মাউন",
    108: "সূরা কাওসার",
    109: "সূরা কাফিরুন",
    110: "সূরা নাসর",
    111: "সূরা লাহাব",
    112: "সূরা ইখলাস",
    113: "সূরা ফালাক",
    114: "সূরা নাস"
}

import os

def share_to_telegram(caption, media_path, telegram_token, telegram_chat_id):
    try:
        url = None
        files = {}
        if media_path.lower().endswith((".jpg", ".jpeg", ".png")):
            url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
            files = {'photo': open(media_path, 'rb')}
            data = {'chat_id': telegram_chat_id, 'caption': caption}
        elif media_path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            url = f"https://api.telegram.org/bot{telegram_token}/sendVideo"
            files = {'video': open(media_path, 'rb')}
            data = {'chat_id': telegram_chat_id, 'caption': caption}
        else:
            print("❌ Unsupported media format for Telegram.")
            return

        r = requests.post(url, files=files, data=data)
        print("📤 Telegram Status:", r.status_code)

    except Exception as e:
        print("❌ Telegram error:", e)

    finally:
        try:
            if os.path.exists(media_path):
                os.remove(media_path)
                print(f"🗑️ Deleted: {media_path}")
        except Exception as e:
            print("⚠️ Could not delete media file:", e)


# === Fetch Random Quran Ayah ===
# Uses Al-Quran API (http://api.alquran.cloud) to fetch ayah in Bengali

def get_random_ayah():
    surah = random.choice(list(surah_ayah_counts.keys()))
    ayah_number = random.randint(1, surah_ayah_counts[surah])
    url = f"http://api.alquran.cloud/v1/ayah/{surah}:{ayah_number}/bn.bengali"
    try:
        res = requests.get(url)
        data = res.json()
        if data["status"] == "OK":
            return {
                "ayah": data["data"]["text"],
                "surah": bangla_surah_names.get(data["data"]["surah"]["number"]),
                "surah_id": data["data"]["surah"]["number"],
                "ayah_number": data["data"]["numberInSurah"],
                "surah_en": data["data"]["surah"]["englishName"],
                "surah_ar": data["data"]["surah"]["name"]
            }
    except Exception as e:
        print("Error fetching ayah:", e)
        return None
from bs4 import BeautifulSoup

import json
import os

USED_HADITH_FILE = "used_hadiths.json"

# Ensures no hadith is posted twice before the list resets

def get_random_hadith():
    total = len(all_hadiths)

    # Load used indexes
    if os.path.exists(USED_HADITH_FILE):
        with open(USED_HADITH_FILE, "r", encoding="utf-8") as f:
            used_indexes = json.load(f)
    else:
        used_indexes = []

    # Reset if all used
    if len(used_indexes) >= total:
        print("✅ All hadiths used once. Resetting list...")
        used_indexes = []

    # Pick a new hadith not used yet
    while True:
        idx = random.randint(0, total - 1)
        if idx not in used_indexes:
            break

    used_indexes.append(idx)
    with open(USED_HADITH_FILE, "w", encoding="utf-8") as f:
        json.dump(used_indexes, f, ensure_ascii=False, indent=2)

    return all_hadiths[idx]

# === Image Generation ===
# Creates an image with footer text overlay for ayah/hadith

def create_quran_image(ayah_text, surah_name_en, ayah_number):
    try:
        bg_file = random.choice(os.listdir(QURAN_BG_DIR))
        img_path = os.path.join(QURAN_BG_DIR, bg_file)
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)

        font_footer = ImageFont.truetype(FONT_FOOTER, size=250)
        footer_text = f"{surah_name_en}, Ayah {ayah_number}"

        footer_w = draw.textlength(footer_text, font=font_footer)
        footer_x = (img.width - footer_w) // 2
        footer_y = (img.height - 450) // 2

        draw.text((footer_x, footer_y), footer_text, font=font_footer, fill="white")

        output_path = f"quran_ayah_{random.randint(1000,9999)}.jpg"
        img.save(output_path)
        return output_path
    except Exception as e:
        print("❌ Error generating image:", e)
        return None

def create_hadith_image(book, number, book_en):
    try:
        bg_file = random.choice(os.listdir(HADITH_BG_DIR))
        img_path = os.path.join(HADITH_BG_DIR, bg_file)
        img = Image.open(img_path)
        draw = ImageDraw.Draw(img)

        font_footer = ImageFont.truetype(FONT_FOOTER, size=200)
        footer_text = f"{book_en}, Hadith {number}"

        footer_w = draw.textlength(footer_text, font=font_footer)
        footer_x = (img.width - footer_w) // 2
        footer_y = (img.height - 450) // 2

        draw.text((footer_x, footer_y), footer_text, font=font_footer, fill="white")

        output_path = f"hadith{random.randint(1000,9999)}.jpg"
        img.save(output_path)
        return output_path
    except Exception as e:
        print("❌ Error generating image:", e)
        return None
# === Post to Facebook and Telegram ===
# Uploads media with published=false → gets media ID → posts with caption and auto comment → shares to Telegram

def post_quran_ayah(index):
    ayah = get_random_ayah()
    if not ayah:
        print("❌ Could not fetch ayah.")
        return

    image_path = create_quran_image(
        ayah_text=ayah["ayah"],
        surah_name_en=english_surah_names[ayah["surah_id"]],
        ayah_number=ayah["ayah_number"]
    )

    if not image_path or not os.path.exists(image_path):
        print("❌ Could not generate image.")
        return

    caption = f"""
✅ Daily Quran Ayah:

'{ayah['ayah']}'

{ayah['surah']}, আয়াত {ayah['ayah_number']}

✅ প্রতিদিন কুরআনের আয়াত পড়ুন।
✅ Like the page: হিদায়াহ

#Quran #IslamicReminder #DailyAyah #হিদায়াত  #IslamicQuotes #দীন  #তাকওয়া #hidayah
""".strip()

# === Upload image with published=false and capture media_id ===
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()  # Read the file into memory

    #Step-1: Upload image with published=false

        upload_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        files = {"source": ("quran.jpg", image_data)}
        upload_params = {
            "access_token": ACCESS_TOKEN,
            "published": "false"
        }
        upload_response = requests.post(upload_url, params=upload_params, files=files)
        upload_data = upload_response.json()
        media_id = upload_data.get("id")

        if not media_id:
            print("❌ Could not upload image.")
            return

    #Step-2: Now post to feed using attached_media

        post_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        post_params = {
            "message": caption,
            "attached_media": json.dumps([{"media_fbid": media_id}]),
            "access_token": ACCESS_TOKEN
        }
        post_response = requests.post(post_url, data=post_params)
        response_data = post_response.json()
        print("🔁 Post response:", response_data)

    # Get post_id
        post_id = response_data.get("id") or response_data.get("post_id")
        if not post_id:
            print("❌ Could not get post ID to comment.")
            return

    #Step-3: Comment
        comment_text = "🤍 আপনার প্রিয় আয়াত কোনটি? কমেন্টে জানিয়ে দিন! 📩\n#QuranDaily #IslamInspiration\n ✅ Join us:\n🔻X (ex-twiiter): x.com/0019hidayah\n🔻Telegram: https://t.me/hidayah019\n🔻Intagram: instagram.com/0019hidayah\n🔻Thread: thread.com/0019hidayah"
        comment_url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        comment_params = {
            "message": comment_text,
            "access_token": ACCESS_TOKEN
        }
        comment_response = requests.post(comment_url, data=comment_params)
        print("💬 Comment Status:", comment_response.status_code)
        print("🗨️ Comment Response:", comment_response.json())

    #Step-4: Share to Telegram — now that everything is done
        share_to_telegram(caption, image_path, telegram_token, telegram_chat_id)

    #Step-5: Finally, delete the file 
        time.sleep(2)  # Small delay to ensure Telegram API is done with the file
        try:
            os.remove(image_path)
            print(f"🗑️ Deleted image file: {image_path}")
        except Exception as e:
            print(f"⚠️ Could not delete media file: {e}")

    except Exception as e:
        print(f"❌ Facebook post/comment error:", e)

# === Post to Facebook and Telegram ===
# Uploads media with published=false → gets media ID → posts with caption and auto comment → shares to Telegram

def post_hadith(index):
    hadith = get_random_hadith()
    if not hadith:
        print("❌ Could not fetch hadith.")
        return

    image_path = create_hadith_image(hadith["book"], hadith["number"], hadith["book_en"])
    if not image_path or not os.path.exists(image_path):
        print("❌ Could not generate hadith image.")
        return

    caption = f"""
✅ Daily Hadith
{hadith['text']}

📚 {hadith['book']}, হাদিস {hadith['number']}

✅ প্রতিদিন একটি হাদিস পড়ুন।
✅ Like the page: Hidayah

#dailyHadith #Hadith #হাদিস #দীন #হিদায়াহ
""".strip()

# === Upload image with published=false and capture media_id ===
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()  # Read the file into memory

    #Step-1: Upload image with published=false
        upload_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        files = {"source": ("quran.jpg", image_data)}
        upload_params = {
            "access_token": ACCESS_TOKEN,
            "published": "false"
        }
        upload_response = requests.post(upload_url, params=upload_params, files=files)
        upload_data = upload_response.json()
        media_id = upload_data.get("id")

        if not media_id:
            print("❌ Could not upload image.")
            return

    #Step-2: Now post to feed using attached_media
        post_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        post_params = {
            "message": caption,
            "attached_media": json.dumps([{"media_fbid": media_id}]),
            "access_token": ACCESS_TOKEN
        }
        post_response = requests.post(post_url, data=post_params)
        response_data = post_response.json()
        print("🔁 Post response:", response_data)

    # Get post_id
        post_id = response_data.get("id") or response_data.get("post_id")
        if not post_id:
            print("❌ Could not get post ID to comment.")
            return

    #Step-3: Comment
        comment_text = "🤲 আল্লাহ আমাদের হাদীস অনুযায়ী জীবন পরিচালনার তাওফিক দিন। আমিন। \n#HadithDaily #IslamInspiration\n ✅ Join us:\n🔻X (ex-twiiter): x.com/0019hidayah\n🔻Telegram: https://t.me/hidayah019\n🔻Intagram: instagram.com/0019hidayah\n🔻Thread: thread.com/0019hidayah"
        comment_url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        comment_params = {
            "message": comment_text,
            "access_token": ACCESS_TOKEN
        }
        comment_response = requests.post(comment_url, data=comment_params)
        print("💬 Comment Status:", comment_response.status_code)
        print("🗨️ Comment Response:", comment_response.json())

    #Step-4: Share to Telegram — now that everything is done
        share_to_telegram(caption, image_path, telegram_token, telegram_chat_id)

    #Step-5: Finally, delete the file
        time.sleep(2)  # Small delay to ensure Telegram API is done with the file
        try:
            os.remove(image_path)
            print(f"🗑️ Deleted image file: {image_path}")
        except Exception as e:
            print(f"⚠️ Could not delete media file: {e}")

    except Exception as e:
        print(f"❌ Facebook post/comment error:", e)

# === Load Q&A Data and Posting ===
# Similar random-selection logic used for Q&A like hadith


QA_FILE = os.path.join(BASE_DIR, "data", "ifatwa_data_cleaned.json")
USED_QA_FILE = os.path.join(BASE_DIR, "data", "used_qa.json")

# Load QAs
with open(QA_FILE, "r", encoding="utf-8") as f:
    all_qas = json.load(f)

# Create tracker file if it doesn't exist
if not os.path.exists(USED_QA_FILE):
    with open(USED_QA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def get_random_qa():
    total = len(all_qas)
    used_indexes = []
    if os.path.exists(USED_QA_FILE):
        with open(USED_QA_FILE, "r", encoding="utf-8") as f:
            used_indexes = json.load(f)
    if len(used_indexes) >= total:
        print("✅ All QAs used. Resetting list...")
        used_indexes = []

    while True:
        idx = random.randint(0, total - 1)
        if idx not in used_indexes:
            break

    used_indexes.append(idx)
    with open(USED_QA_FILE, "w", encoding="utf-8") as f:
        json.dump(used_indexes, f, ensure_ascii=False, indent=2)

    return all_qas[idx]

# === Post to Facebook and Telegram ===
# Uploads media with published=false → gets media ID → posts with caption and auto comment → shares to Telegram

def post_qa(index):
    qa = get_random_qa()
    if not qa:
        print("❌ Could not fetch QA.")
        return

    bg_file = random.choice(os.listdir(QA_BG_DIR))
    img_path = os.path.join(QA_BG_DIR, bg_file)

    if not os.path.exists(img_path):
        print("❌ Image not found:", img_path)
        return

    img = Image.open(img_path)

    caption = f"""
✅ জিজ্ঞাসা ও জবাব:

❓ প্রশ্ন: {qa['question']}

📝 উত্তর: {qa['answer']}

✍️ {qa.get('author', 'অজানা লেখক')}

✅ প্রতিদিন নির্বাচিত প্রশ্নোত্তর পড়ুন
✅ Like the page: Hidayah

#দীন #হিদায়াহ #জিজ্ঞাসা #জবাব #ইসলামি_প্রশ্ন #hidayah
""".strip()

# === Upload image with published=false and capture media_id ===
    try:
        with open(img_path, "rb") as f:
            image_data = f.read()  # Read the file into memory

    #Step-1: Upload image with published=false
        upload_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/photos"
        files = {"source": ("quran.jpg", image_data)}
        upload_params = {
            "access_token": ACCESS_TOKEN,
            "published": "false"
        }
        upload_response = requests.post(upload_url, params=upload_params, files=files)
        upload_data = upload_response.json()
        media_id = upload_data.get("id")

        if not media_id:
            print("❌ Could not upload image.")
            return

    #Step-2: Now post to feed using attached_media
        post_url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
        post_params = {
            "message": caption,
            "attached_media": json.dumps([{"media_fbid": media_id}]),
            "access_token": ACCESS_TOKEN
        }
        post_response = requests.post(post_url, data=post_params)
        response_data = post_response.json()
        print("🔁 Post response:", response_data)

    # Get post_id
        post_id = response_data.get("id") or response_data.get("post_id")
        if not post_id:
            print("❌ Could not get post ID to comment.")
            return

    #Step-3: Comment
        comment_text = "🗨️ আপনার প্রশ্ন থাকলে কমেন্টে লিখুন বা ইনবক্স করুন। \n#QADaily #IslamInspiration\n ✅ Join us:\n🔻X (ex-twiiter): x.com/0019hidayah\n🔻Telegram: https://t.me/hidayah019\n🔻Intagram: instagram.com/0019hidayah\n🔻Thread: thread.com/0019hidayah"
        comment_url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
        comment_params = {
            "message": comment_text,
            "access_token": ACCESS_TOKEN
        }
        comment_response = requests.post(comment_url, data=comment_params)
        print("💬 Comment Status:", comment_response.status_code)
        print("🗨️ Comment Response:", comment_response.json())

    #Step-4: Share to Telegram — now that everything is done
        share_to_telegram(caption, img_path, telegram_token, telegram_chat_id)

    #Step-5: Finally, delete the file 
        time.sleep(2)  # Small delay to ensure Telegram API is done with the file
        try:
            os.remove(img_path)
            print(f"🗑️ Deleted image file: {img_path}")
        except Exception as e:
            print(f"⚠️ Could not delete media file: {e}")

    except Exception as e:
        print(f"❌ Facebook post/comment error:", e)

index = 1

while True:
    print(f"\n🔁 Posting Index: {index}")
    try:
        if index % 3 == 1:
            print("❓ Posting QA")
            post_qa(index)
        elif index % 3 == 2:
            print("📜 Posting Hadith")
            post_hadith(index)
        else:
            print("🕋 Posting Quran Ayah")
            post_quran_ayah(index)

    except Exception as e:
        print("Global Post Error:", e)

    index += 1
    time.sleep(3600)







