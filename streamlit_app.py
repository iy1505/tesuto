import streamlit as st
import time
from datetime import datetime

# セッションステートの初期化
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "mode" not in st.session_state:
    st.session_state.mode = "作業"  # 作業 or 休憩
if "log" not in st.session_state:
    st.session_state.log = []

# 時間設定（分単位）
WORK_DURATION = 25 * 60  # 25分
BREAK_DURATION = 5 * 60  # 5分

# 残り時間の計算
def get_remaining_time(start_time, duration):
    elapsed = int(time.time() - start_time)
    remaining = max(duration - elapsed, 0)
    return remaining

# タイマー表示関数
def display_timer(remaining):
    minutes = remaining // 60
    seconds = remaining % 60
    st.metric(label="⏳ 残り時間", value=f"{minutes:02}:{seconds:02}")

# スタート・リセットボタン
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

# タイマー処理
if st.session_state.timer_running and st.session_state.start_time:
    duration = WORK_DURATION if st.session_state.mode == "作業" else BREAK_DURATION
    remaining = get_remaining_time(st.session_state.start_time, duration)

    display_timer(remaining)

    if remaining == 0:
        # ログに記録
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.log.append(
            f"{timestamp} - {st.session_state.mode}セッション完了 ✅"
        )

        # モード切り替え
        if st.session_state.mode == "作業":
            st.session_state.mode = "休憩"
        else:
            st.session_state.mode = "作業"

        # タイマー再起動
        st.session_state.start_time = time.time()

    # 自動更新
    st.experimental_rerun()

st.header(f"🕒 現在のモード: {st.session_state.mode}")

# ログ表示
with st.expander("📚 セッションログ"):
    if st.session_state.log:
        for entry in reversed(st.session_state.log):
            st.markdown(f"- {entry}")
    else:
        st.write("まだ記録がありません。")

st.markdown("---")
st.caption("© 2025 ポモドーロ勉強サポートアプリ")
