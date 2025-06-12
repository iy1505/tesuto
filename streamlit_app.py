import streamlit as st
import random
import time

# スコアの初期化
score = 0
question_count = 0

# タイマーの設定
time_limit = 30  # 制限時間（秒）
start_time = None

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

# 画面の初期設定
st.title("掛け算・割り算ゲーム")
st.write(f"制限時間は {time_limit} 秒です！")

# ゲーム開始ボタン
if st.button("ゲーム開始"):
    start_time = time.time()
    score = 0
    question_count = 0

    # 問題を出し続けるループ
    while True:
        num1, num2, operation, correct_answer = generate_problem()

        # 問題表示
        question_text = f"問題 {question_count + 1}: {num1} {operation} {num2} = ?"
        st.write(question_text)

        # ユーザーの入力
        user_answer = st.text_input(f"答えを入力してください（問題 {question_count + 1}）:", key=question_count)

        # 時間チェック
        elapsed_time = time.time() - start_time
        if elapsed_time > time_limit:
            st.write("時間切れです！ゲーム終了！")
            break

        # 答えをチェック
        if user_answer.isdigit():
            if int(user_answer) == correct_answer:
                score += 1
                st.write("正解！")
            else:
                st.write(f"不正解。正しい答えは {correct_answer} です。")
            question_count += 1

        # 制限時間内に問題を出す
        if elapsed_time > time_limit:
            break

    st.write(f"ゲーム終了！ あなたのスコアは {score} です。")
