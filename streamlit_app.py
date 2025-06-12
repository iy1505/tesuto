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
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "last_correct" not in st.session_state:
    st.session_state.last_correct = False

time_limit = 30  # 制限時間（秒）

# --- 問題生成 ---
def generate_problem():
    operation = random.choice(['*', '/'])
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    if operation == '*':
        answer = num1 * num2
    else:
        num1 = num1 * num2  # 整数割りになるよう調整
        answer = num1 // num2
    return num1, num2, operation, answer

# --- ゲーム開始 ---
def start_game():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.current_question = generate_problem()
    st.session_state.show_result = False

# --- 問題表示と解答処理 ---
def show_question():
    num1, num2, op, answer = st.session_state.current_question
    st.write(f"問題 {st.session_state.question_count + 1}: {num1} {op} {num2} = ?")

    user_input = st.text_input("答えを入力してください:", key=st.session_state.question_count)

    if st.button("送信"):
        if user_input.strip() == "":
            st.warning("答えを入力してください。")
            return

        try:
            if int(user_input) == answer:
                st.session_state.score += 1
                st.session_state.last_correct = True
                st.success("正解！")
            else:
                st.session_state.last_correct = False
                st.error(f"不正解。正しい答えは {answer} です。")
        except ValueError:
            st.error("数値で入力してください。")
            return

        st.session_state.show_result = True
        st.session_state.question_count += 1

# --- 次の問題 ---
def next_step():
    if st.button("次の問題へ"):
        st.session_state.current_question = generate_problem()
        st.session_state.show_result = False

# --- 時間チェック ---
def check_timeout():
    if st.session_state.start_time:
        elapsed = time.time() - st.session_state.start_time
        remaining = int(time_limit - elapsed)
        st.write(f"残り時間: {remaining} 秒")
        if remaining <= 0:
            st.warning("時間切れ！ゲーム終了")
            st.write(f"あなたのスコアは {st.session_state.score} 点です。")
            st.button("再挑戦", on_click=start_game)
            return True
    return False

# --- アプリ本体 ---
st.title("掛け算・割り算チャレンジ")
st.write(f"{time_limit} 秒以内にできるだけ多く解こう！")

if st.button("ゲーム開始"):
    start_game()

if st.session_state.start_time:
    if not check_timeout():
        if not st.session_state.show_result:
            show_question()
        else:
            next_step()
