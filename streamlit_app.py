import streamlit as st
import time
from datetime import datetime

# --- セッションステート初期化 ---
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "mode" not in st.session_state:
    st.session_state.mode = "作業"  # 作業 or 休憩 or 長休憩
if "log" not in st.session_state:
    st.session_state.log = []
if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0  # 作業完了の回数

# --- 時間設定（秒） ---
WORK_DURATION = 25 * 60       # 25分
SHORT_BREAK = 5 * 60          # 5分
LONG_BREAK = 20 * 60          # 20分（4ポモドーロごと）

# --- 残り時間計算 ---
def get_remaining_time(start_time, duration):
    elapsed = int(time.time() - start_time)
    remaining = max(duration - elapsed, 0)
    return remaining

# --- タイマー表示 ---
def display_timer(remaining):
    minutes = remaining // 60
    seconds = remaining % 60
    st.metric(label="⏳ 残り時間", value=f"{minutes:02}:{seconds:02}")

# --- タイマー制御ボタン ---
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ タイマー開始", disabled=st.session_state.timer_running):
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()

with col2:
    if st.button("🔁 リセット"):
        st.session_state.timer_running = False
        st.session_state.start_time = None
        st.session_state.mode = "作業"
        st.session_state.pomodoro_count = 0

# --- モードに応じた時間取得 ---
def get_current_duration():
    if st.session_state.mode == "作業":
        return WORK_DURATION
    elif st.session_state.mode == "休憩":
        return SHORT_BREAK
    else:
        return LONG_BREAK

# --- タイマー実行 ---
if st.session_state.timer_running and st.session_state.start_time:
    duration = get_current_duration()
    remaining = get_remaining_time(st.session_state.start_time, duration)

    display_timer(remaining)

    if remaining == 0:
        # 終了時ログ記録
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.log.append(
            f"{timestamp} - {st.session_state.mode}セッション完了 ✅"
        )

        # モード遷移
        if st.session_state.mode == "作業":
            st.session_state.pomodoro_count += 1
            if st.session_state.pomodoro_count % 4 == 0:
                st.session_state.mode = "長休憩"
            else:
                st.session_state.mode = "休憩"
        else:
            st.session_state.mode = "作業"

        st.session_state.start_time = time.time()
        st.experimental_rerun()

# --- 表示情報 ---
st.header(f"🕒 現在のモード: {st.session_state.mode}")
st.subheader(f"🍅 ポモドーロ数: {st.session_state.pomodoro_count}")

# --- ログ表示 ---
with st.expander("📚 セッションログ"):
    if st.session_state.log:
        for entry in reversed(st.session_state.log):
            st.markdown(f"- {entry}")
    else:
        st.write("まだ記録がありません。")

st.markdown("---")
st.caption("© 2025 ポモドーロ勉強サポートアプリ")
