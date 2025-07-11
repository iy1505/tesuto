import streamlit as st
import sqlite3
import bcrypt
import time
import random
from datetime import datetime, date
import pandas as pd
from streamlit_extras.st_autorefresh import st_autorefresh

# --- 応援メッセージ ---
MESSAGES = [
    "今日も一歩前進！", "集中して、未来の自分を助けよう！",
    "小さな積み重ねが大きな成果に！", "やればできる、今がその時！",
    "知識は力。コツコツ続けよう！", "一歩ずつ、でも確実に前進中！"
]

# --- タイマー設定（秒） ---
WORK_DURATION = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 20 * 60

# --- DB 初期化など（省略せずこのまま同じ） ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    date TEXT,
                    completed_pomodoros INTEGER
                )''')
    conn.commit(); conn.close()

def add_user(username, email, password):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hashed_pw))
        conn.commit(); return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone(); conn.close()
    if data:
        return bcrypt.checkpw(password.encode(), data[0].encode())
    return False

def record_session(username, count):
    conn = sqlite3.connect("users.db"); c = conn.cursor()
    today = date.today().isoformat()
    c.execute("SELECT completed_pomodoros FROM sessions WHERE username=? AND date=?", (username, today))
    row = c.fetchone()
    if row:
        c.execute("UPDATE sessions SET completed_pomodoros = completed_pomodoros + ? WHERE username=? AND date=?",
                  (count, username, today))
    else:
        c.execute("INSERT INTO sessions (username, date, completed_pomodoros) VALUES (?, ?, ?)",
                  (username, today, count))
    conn.commit(); conn.close()

def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query(
        "SELECT date, completed_pomodoros FROM sessions WHERE username=? ORDER BY date",
        conn,
        params=(username,)
    )
    conn.close()
    return df

# 初期化
init_db()
for key, default in {
    "logged_in": False, "username": "", "timer_running": False,
    "start_time": None, "mode": "作業", "pomodoro_count": 0,
    "log": [], "memo_text": "", "motivation_message": random.choice(MESSAGES),
    "sound_on": True
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def get_current_duration():
    mode = st.session_state.mode
    return WORK_DURATION if mode == "作業" else LONG_BREAK if mode == "長休憩" else SHORT_BREAK

# UI
if not st.session_state.logged_in:
    st.title("ポモドーロ学習サポートタイマー")
    page = st.radio("操作を選んでください", ["ログイン", "新規登録"])
    if page == "ログイン":
        u = st.text_input("ユーザー名"); p = st.text_input("パスワード", type="password")
        if st.button("ログイン") and verify_user(u, p):
            st.session_state.logged_in = True; st.session_state.username = u
            st.success("ログインしました"); st.rerun()
        elif st.button("ログイン"):
            st.error("認証失敗")
    else:
        u = st.text_input("新しいユーザー名"); e = st.text_input("メールアドレス"); p = st.text_input("パスワード", type="password")
        if st.button("登録"):
            if add_user(u, e, p):
                st.success("登録完了！ログインしてください")
            else:
                st.error("そのユーザー名は既に使われています")
    st.stop()

st.title(f"📚 ポモドーロタイマー - {st.session_state.username} さん")
if st.button("ログアウト"):
    record_session(st.session_state.username, st.session_state.pomodoro_count)
    st.session_state.logged_in = False; st.rerun()

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    if st.button("▶️ 開始", disabled=st.session_state.timer_running):
        st.session_state.timer_running = True; st.session_state.start_time = time.time()
with c2:
    if st.button("🔁 リセット"):
        record_session(st.session_state.username, st.session_state.pomodoro_count)
        st.session_state.timer_running = False; st.session_state.start_time = None
        st.session_state.mode = "作業"; st.session_state.pomodoro_count = 0
        st.session_state.log = []; st.session_state.memo_text = ""
        st.session_state.motivation_message = random.choice(MESSAGES)
        st.rerun()
with c3:
    st.session_state.sound_on = st.checkbox("🔊 音ありモード", value=st.session_state.sound_on)

# 自動再描画：1秒ごと
st_autorefresh(interval=1000, limit=None, key="timer")

timer_c, msg_c = st.columns([2, 3])
with timer_c:
    placeholder = st.empty()
    if st.session_state.timer_running and st.session_state.start_time:
        dur = get_current_duration()
        elapsed = int(time.time() - st.session_state.start_time)
        rem = max(dur - elapsed, 0)
        placeholder.metric("残り時間", f"{rem // 60:02}:{rem % 60:02}")
        if rem == 0:
            ts = datetime.now().strftime("%H:%M:%S")
            st.session_state.log.append(f"{ts} - {st.session_state.mode} セッション終了 ✅")
            if st.session_state.sound_on:
                st.audio("https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg", format="audio/ogg")
            if st.session_state.mode == "作業":
                st.session_state.pomodoro_count += 1
                st.session_state.mode = "長休憩" if st.session_state.pomodoro_count % 4 == 0 else "休憩"
            else:
                st.session_state.mode = "作業"
            st.session_state.start_time = time.time()
            st.session_state.motivation_message = random.choice(MESSAGES)
    else:
        placeholder.metric("残り時間", "--:--")

with msg_c:
    st.markdown("###")
    st.success(st.session_state.motivation_message)

st.header(f"🕒 現在モード：{st.session_state.mode}")
st.subheader(f"🍅 完了ポモドーロ数：{st.session_state.pomodoro_count}")

# メモとログとグラフ
st.markdown("### 📝 メモ"); st.session_state.memo_text = st.text_area("学習中のメモ:", value=st.session_state.memo_text)
with st.expander("📚 セッションログ"):
    if st.session_state.log:
        for e in reversed(st.session_state.log):
            st.markdown(f"- {e}")
    else:
        st.write("まだ記録がありません。")
st.markdown("### 📈 過去の進捗"); df = get_user_stats(st.session_state.username)
if not df.empty:
    df = df.set_index("date"); st.bar_chart(df)
else:
    st.info("まだ記録がありません。")

st.markdown("---"); st.caption("© 2025 ポモドーロ勉強サポートアプリ")
