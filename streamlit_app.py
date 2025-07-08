import streamlit as st
import sqlite3
import bcrypt
import time
import random
from datetime import datetime, date
import pandas as pd

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

# --- DB初期化 ---
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
    conn.commit()
    conn.close()

# --- ユーザー登録 ---
def add_user(username, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# --- ログイン認証 ---
def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return bcrypt.checkpw(password.encode(), data[0].encode())
    return False

# --- セッション保存 ---
def record_session(username, count):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute("SELECT completed_pomodoros FROM sessions WHERE username=? AND date=?", (username, today))
    row = c.fetchone()
    if row:
        c.execute("UPDATE sessions SET completed_pomodoros = completed_pomodoros + ? WHERE username=? AND date=?", (count, username, today))
    else:
        c.execute("INSERT INTO sessions (username, date, completed_pomodoros) VALUES (?, ?, ?)", (username, today, count))
    conn.commit()
    conn.close()

# --- 統計取得 ---
def get_user_stats(username):
    conn = sqlite3.connect("users.db")
    df = pd.read_sql_query("SELECT date, completed_pomodoros FROM sessions WHERE username=? ORDER BY date", conn, params=(username,))
    conn.close()
    return df

# --- 音を鳴らす関数 ---
def play_sound():
    st.markdown(
        """
        <audio autoplay>
            <source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg">
        </audio>
        """,
        unsafe_allow_html=True
    )

# --- 初期化 ---
init_db()

# --- セッション変数初期化 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "mode" not in st.session_state:
    st.session_state.mode = "作業"
if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0
if "log" not in st.session_state:
    st.session_state.log = []
if "memo_text" not in st.session_state:
    st.session_state.memo_text = ""
if "motivation_message" not in st.session_state:
    st.session_state.motivation_message = random.choice(MESSAGES)
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True

# --- 時間取得関数 ---
def get_current_duration():
    mode = st.session_state.mode
    return WORK_DURATION if mode == "作業" else LONG_BREAK if mode == "長休憩" else SHORT_BREAK

# --- ログイン画面 ---
if not st.session_state.logged_in:
    st.title("ポモドーロ学習サポートタイマー 　 ログイン")

    page = st.radio("操作を選んでください", ["ログイン", "新規登録"])

    if page == "ログイン":
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        if st.button("ログイン"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("ログインしました")
                st.rerun()
            else:
                st.error("認証失敗")
    else:
        new_username = st.text_input("新しいユーザー名")
        new_email = st.text_input("メールアドレス")
        new_password = st.text_input("パスワード", type="password")
        if st.button("登録"):
            if add_user(new_username, new_email, new_password):
                st.success("登録完了！ログインしてください")
            else:
                st.error("そのユーザー名は既に使われています")

# --- メインアプリ画面 ---
else:
    st.title(f"📚 ポモドーロタイマー - {st.session_state.username} さん")

    if st.button("ログアウト"):
        record_session(st.session_state.username, st.session_state.pomodoro_count)
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # 音あり／音なし切替チェックボックス
    sound_toggle = st.checkbox("🔈 音ありモード", value=st.session_state.sound_on)
    st.session_state.sound_on = sound_toggle

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ 開始", disabled=st.session_state.timer_running):
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
    with col2:
        if st.button("🔁 リセット"):
            record_session(st.session_state.username, st.session_state.pomodoro_count)
            st.session_state.timer_running = False
            st.session_state.start_time = None
            st.session_state.mode = "作業"
            st.session_state.pomodoro_count = 0
            st.session_state.log = []
            st.session_state.memo_text = ""
            st.session_state.motivation_message = random.choice(MESSAGES)

    # タイマー処理
    timer_col, msg_col = st.columns(2)
    with timer_col:
        placeholder = st.empty()
        if st.session_state.timer_running and st.session_state.start_time:
            duration = get_current_duration()
            elapsed = int(time.time() - st.session_state.start_time)
            remaining = max(duration - elapsed, 0)

            minutes = remaining // 60
            seconds = remaining % 60
            placeholder.metric("残り時間", f"{minutes:02}:{seconds:02}")

            if remaining == 0:
                if st.session_state.sound_on:
                    play_sound()

                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.log.append(f"{timestamp} - {st.session_state.mode} セッション終了 ✅")

                if st.session_state.mode == "作業":
                    st.session_state.pomodoro_count += 1
                    st.session_state.mode = "長休憩" if st.session_state.pomodoro_count % 4 == 0 else "休憩"
                else:
                    st.session_state.mode = "作業"

                st.session_state.start_time = time.time()
                st.session_state.motivation_message = random.choice(MESSAGES)
                st.rerun()
            else:
                # 1秒後にページを自動更新して残り時間を更新する
                st.markdown(
                    """
                    <script>
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                    </script>
                    """,
                    unsafe_allow_html=True
                )
        else:
            placeholder.metric("残り時間", "--:--")

    with msg_col:
        st.markdown("###")
        st.success(st.session_state.motivation_message)

    st.header(f"🕒 現在モード：{st.session_state.mode}")
    st.subheader(f"🍅 完了ポモドーロ数：{st.session_state.pomodoro_count}")

    # メモ欄
    st.markdown("### 📝 メモ")
    st.session_state.memo_text = st.text_area("学習中のメモ:", value=st.session_state.memo_text)

    # ログ表示
    with st.expander("📚 セッションログ"):
        if st.session_state.log:
            for entry in reversed(st.session_state.log):
                st.markdown(f"- {entry}")
        else:
            st.write("まだ記録がありません。")

    # 📊 グラフ表示（ユーザー別）
    st.markdown("### 📈 ポモドーロ進捗（過去履歴）")
    stats_df = get_user_stats(st.session_state.username)
    if not stats_df.empty:
        stats_df = stats_df.set_index("date")
        st.bar_chart(stats_df)
    else:
        st.info("まだ記録がありません。ポモドーロを完了させるとここに表示されます。")

    st.markdown("---")
    st.caption("© 2025 ポモドーロ勉強サポートアプリ")
