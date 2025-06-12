import streamlit as st
import random
import time

# --- 初期化 ---
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "input_key" not in st.session_state:
    st.session_state.input_key = str(time.time())
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""
if "feedback_time" not in st.session_state:
    st.session_state.feedback_time = None
if "wait_next" not in st.session_state:
    st.session_state.wait_next = False

time_limit = 30  # 秒

# --- 問題生成 ---
def generate_problem():
    op = random.choice(['*', '/'])
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    if op == '*':
        ans = a * b
    else:
        a = a * b
        ans = a // b
    return a, b, op, ans

# --- ゲーム開始 ---
def start_game():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.current_question = generate_problem()
    st.session_state.input_key = str(time.time())
    st.session_state.last_feedback = ""
    st.session_state.feedback_time = None
    st.session_state.wait_next = False

# --- タイムチェック ---
def check_timeout():
    elapsed = time.time() - st.session_state.start_time
    remaining = int(time_limit - elapsed)
    st.write(f"🕒 残り時間: {remaining} 秒")
    if remaining <= 0:
        st.warning("⏰ 時間切れ！")
        st.write(f"あなたのスコアは {st.session_state.score} 点です。")
        if st.button("再挑戦"):
            start_game()
        return True
    return False

# --- アプリ本体 ---
st.title(" 掛け算・割り算チャレンジ")
st.write(f"【制限時間：{time_limit} 秒】できるだけ早く正解しよう！")

if st.button("ゲーム開始 / リセット"):
    start_game()

if st.session_state.start_time and not check_timeout():
    a, b, op, answer = st.session_state.current_question
    st.write(f"### 問題 {st.session_state.question_count + 1}")
    st.write(f"**{a} {op} {b} = ?**")

    # フィードバックが出たあとの自動進行処理
    if st.session_state.wait_next:
        # フィードバック表示時間の管理
        if time.time() - st.session_state.feedback_time > 0.5:
            # 次の問題へ進行
            st.session_state.current_question = generate_problem()
            st.session_state.input_key = str(time.time())  # 新しい入力キーを生成
            st.session_state.last_feedback = ""
            st.session_state.feedback_time = None
            st.session_state.wait_next = False
            st.session_state.question_count += 1
            st.experimental_rerun()  # ここで再描画を実行
        else:
            st.write(st.session_state.last_feedback)
            st.stop()

    # 入力受付
    user_input = st.text_input("答えを入力:", key=st.session_state.input_key)

    if user_input.strip():
        try:
            if int(user_input) == answer:
                st.session_state.score += 1
                st.session_state.last_feedback = "✅ 正解！"
            else:
                st.session_state.last_feedback = f"❌ 不正解。正解は {answer}"
        except ValueError:
            st.session_state.last_feedback = "⚠️ 数字を入力してください"

        st.session_state.feedback_time = time.time()  # フィードバック時間を記録
        st.session_state.wait_next = True  # 次の問題に進む準備
        st.experimental_rerun()  # ここで再描画を実行
