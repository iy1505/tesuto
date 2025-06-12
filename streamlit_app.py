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
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "feedback_time" not in st.session_state:
    st.session_state.feedback_time = None
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = ""

time_limit = 30  # 制限時間（秒）

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
    st.session_state.user_input = ""
    st.session_state.last_feedback = ""
    st.session_state.feedback_time = None

# --- 時間チェック ---
def check_timeout():
    elapsed = time.time() - st.session_state.start_time
    remaining = int(time_limit - elapsed)
    st.write(f"残り時間: {remaining} 秒")
    if remaining <= 0:
        st.warning("時間切れ！")
        st.write(f"最終スコア: {st.session_state.score} 点")
        if st.button("再挑戦"):
            start_game()
        return True
    return False

# --- アプリ本体 ---
st.title("掛け算・割り算チャレンジ")
st.write(f"{time_limit} 秒以内にできるだけ多く解こう！")

if st.button("ゲーム開始"):
    start_game()

if st.session_state.start_time:
    if not check_timeout():
        q = st.session_state.current_question
        a, b, op, correct = q
        st.write(f"問題 {st.session_state.question_count + 1}: {a} {op} {b} = ?")

        user_input = st.text_input("答えを入力:", value=st.session_state.user_input, key="answer")

        # ユーザーの入力が完了していたら自動判定
        if user_input != st.session_state.user_input and user_input.strip() != "":
            try:
                if int(user_input) == correct:
                    st.session_state.score += 1
                    st.session_state.last_feedback = "✅ 正解！"
                else:
                    st.session_state.last_feedback = f"❌ 不正解。正解は {correct}"
            except ValueError:
                st.session_state.last_feedback = "⚠️ 数字を入力してください"

            st.session_state.feedback_time = time.time()
            st.session_state.user_input = user_input  # 入力確定

        # フィードバック表示
        if st.session_state.feedback_time:
            st.write(st.session_state.last_feedback)

            # 0.5秒後に次の問題へ自動切り替え
            if time.time() - st.session_state.feedback_time > 0.5:
                st.session_state.current_question = generate_problem()
                st.session_state.question_count += 1
                st.session_state.user_input = ""
                st.session_state.feedback_time = None
                st.session_state.last_feedback = ""
                st.experimental_rerun()
