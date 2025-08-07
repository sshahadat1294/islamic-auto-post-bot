import subprocess

print("✅ Starting Islamic Auto Post Bot...")

try:
    subprocess.run(["python3", "main_bot.py"])
except Exception as e:
    print("❌ Error running main_bot.py:", e)
