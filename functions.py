import re
import sqlite3 as sql
import json
import sys

def remove_minecraft_color_codes(text):
    return re.sub(r"§[0-9a-fk-or]", "", text)

def check_empty_users(filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    tgid INTEGER PRIMARY KEY,
    level TEXT NOT NULL)
    ''')

    conn.commit()
    cursor.execute("SELECT * FROM Users WHERE level = ?", ("super",))
    users = cursor.fetchall()
    if not users:
        print("В базе данных не зарегистрировано ни одного super-пользователя.")
        tgid = input("Введите Telegram-ID для выдачи прав super-админа: ")
        cursor.execute("SELECT * FROM Users")
        all_users = cursor.fetchall()
        for user in all_users[0]:
            if int(tgid) == user:
                print("Этот пользователь уже зарегистрирован. Перезапустите бота и введите другой Telegram-ID.")
                sys.exit()
        cursor.execute("INSERT INTO Users (tgid, level) VALUES (?, ?)", (int(tgid), "super"))
        conn.commit()
        conn.close()

def check_user_in_db(tgid: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Users WHERE tgid = ?", (tgid, ))
    data = cursor.fetchone()
    conn.close()

    return data if data else 0

def is_command_allowed(cmd: str, tgid: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE tgid = ?", (tgid,))
    data = cursor.fetchone()

    if data[1] == "super":
        return 1

    groups = json.load(open("groups.json", 'r'))
    try:
        group = groups[data[1]]
        cmd_list = cmd.split()
        allowed_commands = group["allowed_commands"]
        if '*' in allowed_commands:
            return 1
        if cmd_list[0] not in allowed_commands:
            return 0

        ban_words_for_command = group.get("ban_words_for_commands", {}).get(cmd_list[0], [])

        # Если в команде есть запрещённые слова — команда запрещена
        for word in cmd_list:
            if word in ban_words_for_command:
                return 0  # Команда содержит запрещённое слово

        # Если команда прошла все проверки, она разрешена
        return 1
    except KeyError:
        print(f"{tgid} в базе данных имеет группу {data[1]}, но в groups.json она не зарегистрирована!")
        return Exception
    finally:
        conn.close()

def register(tgid: int, level: str, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Users (tgid, level) VALUES (?, ?)", (tgid, level))
    conn.commit()
    conn.close()

def unregister(tgid: int, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Users WHERE tgid = ?", (tgid,))
    conn.commit()
    conn.close()

def set_group(tgid: int, level: str, filename = "data.db"):
    conn = sql.connect(filename)
    cursor = conn.cursor()

    cursor.execute("UPDATE Users SET level = ? WHERE tgid = ?", (level, tgid))
    conn.commit()
    conn.close()