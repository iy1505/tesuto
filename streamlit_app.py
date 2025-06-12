import streamlit as st
import random
import time

# ゲーム設定
TIME_LIMIT = 30  # 秒
FEEDBACK_DELAY = 0.5  # フィードバック表示後の待機秒数

# セッション状態の初期化
def init_session():
    st.session_state.score = 0
    st.session_state.question_count = 0
    st.session_state.start_time = time.time()
    st.session_state.current_question = generate_problem()
    st.session_state.last_feedback = ""
    st.session_state.waiting = False
    st.session_state.input = ""
    st.session_state.feedback_shown_at = None

# 問題生成
def generate_problem():
    op = random.choice(['*', '/'])
    b = random.randint(1, 10)
    a = b * random.randint(1, 10) if op == '/' else random.randint(1, 10)
    answer = a * b if op == '*' else a // b
    return (a, b, op, answer)

# ゲーム開始ボタン
st.title(" 計算チャレンジ（掛け算・割り算）")
if st.button("ゲーム開始 / リセット"):
    init_session()

# ゲームが開始されていない場合は終了
if "start_time" not in st.session_state:
    st.stop()

# 残り時間チェック
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

# 現在の問題を取得
a, b, op, correct_answer = st.session_state.current_question
st.write(f"### 問題 {st.session_state.question_count + 1}: {a} {op} {b} = ?")

# フィードバック → 次の問題に自動進行
if st.session_state.waiting:
    st.success(st.session_state.last_feedback)
    if time.time() - st.session_state.feedback_shown_at > FEEDBACK_DELAY:
        # 次の問題に進む
        st.session_state.current_question = generate_problem()
        st.session_state.question_count += 1
        st.session_state.input = ""  # 入力状態をクリア
        st.session_state.waiting = False
        st.session_state.last_feedback = ""
        st.session_state.feedback_shown_at = None
        # 再実行ではなく次の問題へ進行
        st.experimental_rerun()
    else:
        st.stop()  # フィードバック待機中は再実行しない

# 入力欄
answer = st.text_input("答えを入力して Enter", value=st.session_state.input, key="answer_input")

# 回答処理（Enterで回答確定）
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

    # フィードバック後、次の問題へ進む準備
    st.session_state.waiting = True
    st.session_state.feedback_shown_at = time.time()  # フィードバック表示時間を記録
    st.experimental_rerun()  # ここで再実行を行う

