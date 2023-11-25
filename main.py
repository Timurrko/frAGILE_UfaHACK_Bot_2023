import pickle

import telebot
from telebot import types
import os
import sqlite3
import queue
import threading

TOKEN = '6985946769:AAE-bKL3CdkCSAGm068r3v1dCxtowtXrahk'
bot = telebot.TeleBot(TOKEN)

hobbies_file = "hobbies_set.pkl"

if os.path.exists(hobbies_file):
    with open(hobbies_file, "rb") as f:
        hobbies_set = pickle.load(f)
else:
    hobbies_set = {"#плавание", "#чтение", "#путешествия", "#музыка", "#кино", "#спорт"}

# Создание базы данных, если она не существует
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, surname TEXT, phone TEXT, hobbies TEXT)''')
conn.commit()

# Создание очереди сообщений
message_queue = queue.Queue()


def handle_messages():
    while True:
        message = message_queue.get()
        if message.text == "/start":
            send_welcome(message)
        else:
            process_user(message)


# Запуск потока обработки сообщений
threading.Thread(target=handle_messages, daemon=True).start()


@bot.message_handler(func=lambda message: True)
def enqueue_message(message):
    message_queue.put(message)


def send_welcome(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user:
        print(user)
        name, surname = user[1], user[2]
        if name and surname:
            bot.reply_to(message, f'Я тебя помню, {name} {surname}!')
        elif not name and not surname:
            bot.reply_to(message, f'Я тебя помню!')
        else:
            bot.reply_to(message, f'Я тебя помню, {name + surname}!')
    else:
        bot.reply_to(message, "Привет!")
        c.execute("INSERT INTO users VALUES (?, '', '', '', '')", (user_id,))
        conn.commit()
        process_user(message)
    conn.close()


def process_user(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    user_id = message.from_user.id
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if not user[1]:
        msg = bot.send_message(user_id, "Какое у тебя имя?")
        bot.register_next_step_handler(msg, set_name)
    elif not user[2]:
        msg = bot.send_message(user_id, "Какая у тебя фамилия?")
        bot.register_next_step_handler(msg, set_surname)
    elif not user[3]:
        msg = bot.send_message(user_id, "Какой у тебя номер телефона?")
        bot.register_next_step_handler(msg, set_phone)
    elif not user[4]:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtns = [types.KeyboardButton(hobby) for hobby in hobbies_set]
        itembtns.append(types.KeyboardButton("завершить"))
        markup.add(*itembtns)
        msg = bot.send_message(user_id, "Какие у тебя увлечения? Выбери из списка или введи свои, используя хэштеги.",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, set_hobbies)
    conn.close()


def set_name(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    name = message.text
    c.execute("UPDATE users SET name=? WHERE id=?", (name, message.from_user.id))
    conn.commit()
    conn.close()
    process_user(message)


def set_surname(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    surname = message.text
    c.execute("UPDATE users SET surname=? WHERE id=?", (surname, message.from_user.id))
    conn.commit()
    conn.close()
    process_user(message)


def set_phone(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    phone = message.text
    c.execute("UPDATE users SET phone=? WHERE id=?", (phone, message.from_user.id))
    conn.commit()
    conn.close()
    process_user(message)


def set_hobbies(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT hobbies FROM users WHERE id=?", (message.from_user.id,))
    hobbies = c.fetchone()
    hobbies = set(hobbies[0].split())
    if message.text == "завершить":
        bot.send_message(message.from_user.id, "Увлечения сохранены.")
        c.execute("UPDATE users SET hobbies=? WHERE id=?", (' '.join(hobbies), message.from_user.id))
        conn.commit()
    else:
        new_hobbies = set(message.text.split())
        hobbies_set.update(new_hobbies)
        hobbies.update(new_hobbies)
        with open(hobbies_file, "wb") as f:
            pickle.dump(hobbies_set, f)

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtns = [types.KeyboardButton(hobby) for hobby in hobbies_set]
        itembtns.append(types.KeyboardButton("завершить"))
        markup.add(*itembtns)
        msg = bot.send_message(message.from_user.id,
                               "Есть еще увлечения? Выбери из списка или введи свои, используя хэштеги.",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, set_hobbies)
    c.execute("UPDATE users SET hobbies=? WHERE id=?", (' '.join(hobbies), message.from_user.id))
    conn.commit()
    conn.close()


bot.polling()
