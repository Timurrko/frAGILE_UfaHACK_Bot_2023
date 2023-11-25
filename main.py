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
             (id INTEGER PRIMARY KEY, name TEXT, age TEXT, contact_data TEXT, hobbies TEXT)''')
conn.commit()

# Создание очереди сообщений
message_queue = queue.Queue()


def handle_messages():
    while True:
        message = message_queue.get()
        if message.text == "/start":
            send_welcome(message)
        elif message.text == "/search":
            search(message)


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
        name = user[1]
        if name:
            bot.reply_to(message, f'Я тебя помню, {name}!')
        else:
            bot.reply_to(message, f'Я тебя помню!')
    else:
        bot.reply_to(message, "Привет! Это MeetMe, я помогу тебе найти друзей по интересам. Давай я задам тебе "
                              "несколько вопросов")
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
        msg = bot.send_message(user_id, "Как тебя зовут?")
        bot.register_next_step_handler(msg, set_name)
    elif not user[2]:
        msg = bot.send_message(user_id, "Сколько тебе лет?")
        bot.register_next_step_handler(msg, set_age)
    elif not user[3]:
        msg = bot.send_message(user_id, "Как с тобой можно связаться? Ты можешь оставить ссылку на ВК или WhatsApp")
        bot.register_next_step_handler(msg, set_contact_data)
    elif not user[4]:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtns = [types.KeyboardButton(hobby) for hobby in hobbies_set]
        itembtns.append(types.KeyboardButton("завершить"))
        markup.add(*itembtns)
        msg = bot.send_message(user_id,
                               "Чем ты увлекаешься? Выбери хобби из списка или введи свои #вот_так. Можешь ввести несколько через пробел. Как закончишь, нажми \"завершить\" в меню",
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


def set_age(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    age = message.text
    c.execute("UPDATE users SET age=? WHERE id=?", (age, message.from_user.id))
    conn.commit()
    conn.close()
    process_user(message)


def set_contact_data(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    contact_data = message.text
    c.execute("UPDATE users SET contact_data=? WHERE id=?", (contact_data, message.from_user.id))
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
        print(c.execute("SELECT * FROM users WHERE id=?", message.from_user.id).fetchone())
    else:
        global hobbies_set
        new_hobbies = set(message.text.lower().split())
        hobbies_set = set(list(hobbies_set)[:max(20 - len(new_hobbies), 0)])

        new_hobbies = set(list(new_hobbies)[:20])
        hobbies.update(new_hobbies)
        hobbies_set.update(new_hobbies)
        with open(hobbies_file, "wb") as f:
            pickle.dump(hobbies_set, f)

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtns = [types.KeyboardButton(hobby) for hobby in hobbies_set]
        itembtns.append(types.KeyboardButton("завершить"))
        markup.add(*itembtns)
        msg = bot.send_message(message.from_user.id,
                               "Можешь продолжить список своих увлечений",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, set_hobbies)
    c.execute("UPDATE users SET hobbies=? WHERE id=?", (' '.join(hobbies), message.from_user.id))
    conn.commit()
    conn.close()


def search(message):
    msg = bot.send_message(message.from_user.id, "По каким хобби вы хотите найти единомышленников?")
    bot.register_next_step_handler(msg, return_people_by_hobbies)


def return_people_by_hobbies(message):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hobbies = message.text.split()
    formatted_string_of_hobbies = f"WHERE NOT id = \'{message.from_user.id}\' AND " + "(" + " OR ".join(
        [f"hobbies LIKE \'%{hobby}%\'" for hobby in hobbies]) + ")"
    print(formatted_string_of_hobbies)
    c.execute("SELECT name, age, contact_data FROM users " + formatted_string_of_hobbies)
    people_of_interest = c.fetchall()
    print(people_of_interest)
    text = "Вот, кого я нашел:\n" + ";\n".join(", ".join(person) for person in people_of_interest)
    bot.send_message(message.from_user.id, text)
    conn.close()


bot.polling()
