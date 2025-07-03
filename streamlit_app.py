import streamlit as st
import time
from datetime import datetime

# --- セッションステートの初期化 ---
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "mode" not in st.session_state:
    st.session_state.mode = "作業"  # 作業／休憩／長休憩
if "log" not in st.session_state:
    st.session_state.log = []
if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0  # 作業回数カウント

# --- 時間設定（秒） ---
WORK_DURATION = 25 * 60        # 25分
SHORT_BREAK = 5 * 60           # 5分
LONG_BREAK = 20 * 60           # 20分

# --- タイマー時間の取得 ---
def get_current_duration():
    if st.session_state.mode == "作業":
        return WORK_DURATION
    elif st.session_state.mode == "休憩":
        return SHORT_BREAK
    elif st.session_state.mode == "長休憩":
        return LONG_BREAK

# --- タイマー開始ボタン ---
col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ タイマー開始", disabled=st.session_state.timer_running):
        st.session_state.timer_running = True
        st.session_state.start_time = time.time()

# --- タイマーリセットボタン ---
with col2:
    if st.button("🔁 リセット"):
        st.session_state.timer_running = False
        st.session_state.start_time = None
        st.session_state.mode = "作業"
        st.session_state.pomodoro_count = 0
        st.session_state.log = []

# --- タイマーの動作 ---
if st.session_state.timer_running and st.session_state.start_time:
    duration = get_current_duration()
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(duration - elapsed, 0)

    minutes = remaining // 60
    seconds = remaining % 60
    st.metric(label="⏳ 残り時間", value=f"{minutes:02}:{seconds:02}")

    if remaining == 0:
        # タイマー終了処理
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.log.append(
            f"{timestamp} - {st.session_state.mode}セッション完了 ✅"
        )

        if st.session_state.mode == "作業":
            st.session_state.pomodoro_count += 1
            if st.session_state.pomodoro_count % 4 == 0:
                st.session_state.mode = "長休憩"
            else:
                st.session_state.mode = "休憩"
        else:
            st.session_state.mode = "作業"

        # 次のセッションを即開始
        st.session_state.start_time = time.time()
        st.experimental_rerun()
    else:
        # 毎秒更新
        time.sleep(1)
        st.experimental_rerun()

# --- 現在のモードとポモドーロ数の表示 ---
st.header(f"🕒 現在のモード: {st.session_state.mode}")
st.subheader(f"🍅 完了したポモドーロ数: {st.session_state.pomodoro_count}")

# --- セッションログ表示 ---
with st.expander("📚 セッションログ"):
    if st.session_state.log:
        for entry in reversed(st.session_state.log):
            st.markdown(f"- {entry}")
    else:
        st.write("まだ記録がありません。")

st.markdown("---")
st.caption("© 2025 ポモドーロ勉強サポートアプリ")
