import streamlit as st
import numpy as np
import time
import random

# ボードサイズ
ROWS = 20
COLS = 10

# テトリスブロックの定義
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'L': [[1, 0, 0],
          [1, 1, 1]],
    'J': [[0, 0, 1],
          [1, 1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]]
}

# 現在の形状を落とす
def place_shape(board, shape, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell and 0 <= pos[0]+i < ROWS and 0 <= pos[1]+j < COLS:
                board[pos[0]+i][pos[1]+j] = 1
    return board

# 描画
def draw_board(board):
    st.write("⬛ = 空白、🟩 = ブロック")
    board_display = ""
    for row in board:
        for cell in row:
            board_display += "🟩" if cell else "⬛"
        board_display += "\n"
    st.text(board_display)

def main():
    st.title("🧱 簡易テトリス (Streamlit版)")
    if 'board' not in st.session_state:
        st.session_state.board = np.zeros((ROWS, COLS), dtype=int)
        st.session_state.shape = random.choice(list(SHAPES.values()))
        st.session_state.pos = [0, COLS // 2 - len(st.session_state.shape[0]) // 2]

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ 左"):
            st.session_state.pos[1] = max(0, st.session_state.pos[1] - 1)
    with col2:
        if st.button("⬇️ 下"):
            st.session_state.pos[0] += 1
    with col3:
        if st.button("➡️ 右"):
            st.session_state.pos[1] = min(COLS - len(st.session_state.shape[0]), st.session_state.pos[1] + 1)

    board_copy = np.copy(st.session_state.board)
    place_shape(board_copy, st.session_state.shape, st.session_state.pos)
    draw_board(board_copy)

    if st.button("🔄 固定 & 新しいブロック"):
        place_shape(st.session_state.board, st.session_state.shape, st.session_state.pos)
        st.session_state.shape = random.choice(list(SHAPES.values()))
        st.session_state.pos = [0, COLS // 2 - len(st.session_state.shape[0]) // 2]

    if st.button("🔁 リセット"):
        st.session_state.clear()

if __name__ == "__main__":
    main()
