import streamlit as st
import sqlite3
import pandas as pd

# ------------------ ЧТЕНИЕ ВОПРОСОВ ------------------
@st.cache_data
def load_questions():
    df = pd.read_csv("questions.csv")
    return df

# ------------------ СОЗДАНИЕ БАЗЫ ------------------
def init_db():
    conn = sqlite3.connect("results.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        category TEXT,
        score INTEGER
    )
    """)
    conn.commit()
    conn.close()

def save_result(user, category, score):
    conn = sqlite3.connect("results.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO results (user, category, score) VALUES (?, ?, ?)", 
                (user, category, score))
    conn.commit()
    conn.close()

# ------------------ ЛОГИКА ПРИЛОЖЕНИЯ ------------------
st.title("🎓 Тренажёр для студентов")

init_db()
df = load_questions()

# Имя пользователя
username = st.text_input("Введите своё имя:")

# Выбор категории
categories = df["category"].unique().tolist()
category = st.selectbox("Выберите категорию:", categories)

# Фильтруем вопросы по категории
q_list = df[df["category"] == category].to_dict("records")

# Состояния
if "index" not in st.session_state:
    st.session_state.index = 0
if "score" not in st.session_state:
    st.session_state.score = 0

# Получаем текущий вопрос
if st.session_state.index < len(q_list):
    q = q_list[st.session_state.index]
    st.subheader(f"Вопрос {st.session_state.index + 1} из {len(q_list)}")
    st.write(q["question"])
    
    options = [q["option1"], q["option2"], q["option3"], q["option4"]]
    choice = st.radio("Выберите ответ:", options)

    if st.button("Проверить"):
        if choice == q["answer"]:
            st.success("✅ Правильно!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Неправильно. Верный ответ: {q['answer']}")

    if st.button("Следующий вопрос"):
        st.session_state.index += 1
else:
    st.info(f"Тест завершён! Ваш результат: {st.session_state.score} из {len(q_list)}")
    if username:
        save_result(username, category, st.session_state.score)
        st.success("✅ Результат сохранён в базе данных!")
    # Сброс для новой попытки
    st.session_state.index = 0
    st.session_state.score = 0

# ------------------ ПОКАЗ СТАТИСТИКИ ------------------
st.markdown("---")
if st.checkbox("📊 Показать таблицу результатов"):
    conn = sqlite3.connect("results.db")
    df_results = pd.read_sql("SELECT * FROM results", conn)
    st.dataframe(df_results)
    conn.close()
