import telebot

bot = telebot.TeleBot('6985946769:AAE-bKL3CdkCSAGm068r3v1dCxtowtXrahk')

users = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in users:
        bot.reply_to(message, f'Я тебя помню, {users[user_id]["name"]} {users[user_id]["surname"]}!')
    else:
        msg = bot.reply_to(message, "Привет! Как тебя зовут?")
        bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    name = message.text
    user_id = message.from_user.id
    users[user_id] = {'name': name}
    msg = bot.reply_to(message, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(msg, process_surname_step)


def process_surname_step(message):
    surname = message.text
    user_id = message.from_user.id
    users[user_id]['surname'] = surname
    msg = bot.reply_to(message, 'Какой у тебя email?')
    bot.register_next_step_handler(msg, process_email_step)


def process_email_step(message):
    email = message.text
    user_id = message.from_user.id
    users[user_id]['email'] = email
    msg = bot.reply_to(message, 'Какой у тебя номер телефона?')
    bot.register_next_step_handler(msg, process_phone_step)


def process_phone_step(message):
    phone = message.text
    user_id = message.from_user.id
    users[user_id]['phone'] = phone
    msg = bot.reply_to(message, 'Какие у тебя увлечения?')
    bot.register_next_step_handler(msg, process_hobbies_step)


def process_hobbies_step(message):
    hobbies = message.text
    user_id = message.from_user.id
    users[user_id]['hobbies'] = hobbies
    msg = bot.reply_to(message, 'Сколько тебе лет?')
    bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    age = message.text
    user_id = message.from_user.id
    users[user_id]['age'] = age
    msg = bot.reply_to(message, 'В какой ты учебной группе?')
    bot.register_next_step_handler(msg, process_group_step)


def process_group_step(message):
    group = message.text
    user_id = message.from_user.id
    users[user_id]['group'] = group
    msg = bot.reply_to(message, 'Какие у тебя навыки?')
    bot.register_next_step_handler(msg, process_skills_step)


def process_skills_step(message):
    skills = message.text
    user_id = message.from_user.id
    users[user_id]['skills'] = skills
    bot.reply_to(message, f'Спасибо, {users[user_id]["name"]} {users[user_id]["surname"]}!')


bot.polling()
