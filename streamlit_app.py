import time
import os
import platform

# 時間設定（秒）
WORK_TIME = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60
CYCLES_BEFORE_LONG_BREAK = 4

def notify(title, message):
    system = platform.system()
    if system == "Darwin":  # macOS
        os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')
    elif system == "Linux":
        os.system(f'notify-send "{title}" "{message}"')
    elif system == "Windows":
        # Windowsの通知はPython標準では難しいので、printで代替
        print(f"\n🔔 {title}: {message}")
    else:
        print(f"\n🔔 {title}: {message}")

def countdown(seconds):
    while seconds:
        mins, secs = divmod(seconds, 60)
        print(f"\r⏳ {mins:02d}:{secs:02d}", end="")
        time.sleep(1)
        seconds -= 1
    print("\r⏰ 00:00")

def pomodoro_cycle():
    cycle = 0
    while True:
        cycle += 1
        print(f"\n🍅 ポモドーロ {cycle} 開始！（25分）")
        notify("ポモドーロ開始", f"{cycle} 回目の作業を始めましょう！")
        countdown(WORK_TIME)

        if cycle % CYCLES_BEFORE_LONG_BREAK == 0:
            print("\n🛌 長い休憩（15分）")
            notify("休憩時間", "15分の長い休憩を取りましょう！")
            countdown(LONG_BREAK)
        else:
            print("\n☕ 短い休憩（5分）")
            notify("休憩時間", "5分の短い休憩を取りましょう！")
            countdown(SHORT_BREAK)

        # 繰り返すか確認
        cont = input("\n➡️ 続けますか？（y/n）: ").strip().lower()
        if cont != 'y':
            print("👋 お疲れ様でした！")
            break

if __name__ == "__main__":
    print("=== 🎓 ポモドーロ勉強補助システム ===")
    pomodoro_cycle()
