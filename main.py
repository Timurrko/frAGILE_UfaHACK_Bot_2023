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
    msg = bot.reply_to(message, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(msg, process_surname_step, name, user_id)

def process_surname_step(message, name, user_id):
    surname = message.text
    users[user_id] = {'name': name, 'surname': surname}
    bot.reply_to(message, f'Спасибо, {name} {surname}!')

bot.polling()
