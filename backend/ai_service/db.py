import mysql.connector
import os

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wishplay"
    )

def save_history(user_id, category, question, answer_text):
    conn = get_db()
    cursor = conn.cursor()

    sql = """
        INSERT INTO conversation_history (user_id, category, question, answer_text)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (user_id, category, question, answer_text))
    conn.commit()

    cursor.close()
    conn.close()

def get_history(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT id, category, question, answer_text, created_at
        FROM conversation_history
        WHERE user_id = %s
        ORDER BY created_at DESC
    """

    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
