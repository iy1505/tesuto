import streamlit as st
import random
import time

# ゲームの状態を保持するために session_state を使う
if "score" not in st.session_state:
    st.session_state.score = 0
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# タイマーの設定
time_limit = 30  # 制限時間（秒）

# 問題を生成する関数
def generate_problem():
    operation = random.choice(['*', '/'])
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    if operation == '*':
        answer = num1 * num2
    else:
        # 割り算の場合は答えが整数になるように調整
        num1 = num1 * num2
        answer = num1 // num2
    return num1, num2, operation, answer

# ゲーム開始の処理
def start_game():
    st.session_state.start_time = time.time()  # ゲーム開始時間を記録
    st.session_state.score = 0
    st.session_state.question_count = 0

# ゲームの進行処理
def next_question():
    num1, num2, operation, correct_answer = generate_problem()

    # 問題表示
    question_text = f"問題 {st.session_state.question_count + 1}: {num1} {operation} {num2} = ?"
    st.write(question_text)

    # ユーザーの入力
    user_answer = st.text_input(f"答えを入力してください（問題 {st.session_state.question_count + 1}）:", key=st.session_state.question_count)

    # 入力があった場合に解答をチェック
    if user_answer:
        if user_answer.isdigit():
            if int(user_answer) == correct_answer:
                st.session_state.score += 1
                st.write("正解！")
            else:
                st.write(f"不正解。正しい答えは {correct_answer} です。")

        # 問題の数をカウントして次の問題に進む
        st.session_state.question_count += 1
        st.session_state.start_time = time.time()  # 新しい問題を出題するたびにタイマーをリセット

# ゲーム終了の処理
def check_game_over():
    elapsed_time = time.time() - st.session_state.start_time
    if elapsed_time > time_limit:
        st.write("時間切れです！ゲーム終了！")
        st.write(f"最終スコアは {st.session_state.score} です。")
        return True
    return False

# 初期画面設定
st.title("掛け算・割り算ゲーム")
st.write(f"制限時間は {time_limit} 秒です！")

# ゲーム開始ボタン
if st.button("ゲーム開始"):
    start_game()

# ゲーム進行中の処理
if st.session_state.start_time:
    if check_game_over():
        st.button("再挑戦", on_click=start_game)  # ゲーム終了後の再挑戦ボタン
    else:
        next_question()

