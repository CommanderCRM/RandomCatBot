import sqlite3

db = sqlite3.connect("pusha.db", check_same_thread=False)


def db_creation():
    db.execute(
        "CREATE TABLE IF NOT EXISTS user_ids (user_id TEXT PRIMARY KEY, chat_id TEXT)"
    )


# if user id is not in DB
def add_user_id(user_id, chat_id):
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM user_ids WHERE user_id = ?", (user_id,))
    existing_user_id = cursor.fetchone()
    if existing_user_id is None:
        cursor.execute(
            "INSERT INTO user_ids (user_id, chat_id) VALUES (?, ?)", (user_id, chat_id)
        )
        db.commit()
        return True
    else:
        return False


# if user id is in the DB
def update_chat_id(user_id, chat_id):
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM user_ids WHERE user_id = ?", (user_id,))
    existing_user_id = cursor.fetchone()
    if existing_user_id is not None:
        cursor.execute(
            "UPDATE user_ids SET chat_id = ? WHERE user_id = ?", (chat_id, user_id)
        )
        db.commit()
        return True
    else:
        return False
