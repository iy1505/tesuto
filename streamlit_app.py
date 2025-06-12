import streamlit as st
import random
import time

# ゲーム設定
TIME_LIMIT = 30  # 秒
FEEDBACK_DELAY = 0.5  # フィードバック表示後の待機秒数

def init_session():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.current_question = generate_problem()
    st.session_state.last_feedback = ""
    st.session_state.waiting = False
    st.session_state.input = ""
    st.session_state.feedback_shown_at = None

def generate_problem():
    op = random.choice(['*', '/'])
    b = random.randint(1, 10)
    a = b * random.randint(1, 10) if op == '/' else random.randint(1, 10)
    answer = a * b if op == '*' else a // b
    return (a, b, op, answer)

st.title(" 計算チャレンジ（掛け算・割り算）")

if st.button(" ゲーム開始 / リセット"):
    init_session()

if "start_time" not in st.session_state:
    st.stop()

elapsed = time.time() - st.session_state.start_time
remaining = TIME_LIMIT - elapsed
if remaining <= 0:
    st.warning("⏰ 時間切れ！")
    st.write(f"スコア: {st.session_state.score} 点（{st.session_state.question_count} 問中）")
    if st.button("🔄 再挑戦"):
        init_session()
    st.stop()

st.write(f"⏳ 残り時間: {int(remaining)} 秒")
st.write(f"得点: {st.session_state.score} 点")

a, b, op, correct_answer = st.session_state.current_question
st.write(f"### 問題 {st.session_state.question_count + 1}: {a} {op} {b} = ?")

if st.session_state.waiting:
    st.success(st.session_state.last_feedback)
    # フィードバック表示してから一定時間経ったら次の問題へ
    if time.time() - st.session_state.feedback_shown_at > FEEDBACK_DELAY:
        st.session_state.current_question = generate_problem()
        st.session_state.question_count += 1
        st.session_state.input = ""
        st.session_state.waiting = False
        st.session_state.last_feedback = ""
        st.session_state.feedback_shown_at = None
    else:
        st.stop()

answer = st.text_input("答えを入力して Enter", value=st.session_state.input, key="answer_input")

if answer.strip() and not st.session_state.waiting:
    st.session_state.input = answer
    try:
        if int(answer) == correct_answer:
            st.session_state.score += 1
            st.session_state.last_feedback = "✅ 正解！"
        else:
            st.session_state.last_feedback = f"❌ 不正解。正解は {correct_answer} でした"
    except ValueError:
        st.session_state.last_feedback = "⚠️ 数字で入力してください"

    st.session_state.waiting = True
    st.session_state.feedback_shown_at = time.time()
