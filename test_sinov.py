import telebot
from dotenv import load_dotenv
import os
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the environment variable
TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(token=TOKEN)

# Dictionary to store user data temporarily
user_data = {}

# Load address data
with open("address.json", "r") as f:
    address_data = json.load(f)

# Define admin chat ID
ADMIN_CHAT_ID = 5655769857  # Admin chat ID should be an integer

# Load user info data
try:
    with open("user_info.json", "r") as f:
        stored_user_data = json.load(f)
except FileNotFoundError:
    stored_user_data = []

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if message.chat.id == ADMIN_CHAT_ID:
        # Admin buttons
        button1 = KeyboardButton("Yangi test yuklash")
        button2 = KeyboardButton("Natijalarni ko'rish")
        button3 = KeyboardButton("Foydalanuvchilarni ko'rish")
        markup.add(button1, button2, button3)
        bot.send_message(message.chat.id, "Xush kelibsiz admin", reply_markup=markup)
    else:
        user_info = next((user for user in stored_user_data if user["chat_id"] == message.chat.id), None)
        if user_info:
            bot.send_message(message.chat.id, f"{message.from_user.username} Botga xush kelibsiz", reply_markup=markup)
        else:
            # Regular user buttons
            button1 = KeyboardButton("Ma'lumotlarni ko'rish")
            button2 = KeyboardButton("O'rinni ko'rish")
            button3 = KeyboardButton("Test boshlash")
            button4 = KeyboardButton("Ma'lumotlarni o'zgartirish")
            markup.add(button1, button2, button3, button4)
            bot.send_message(message.chat.id, f"{message.from_user.username} Botga xush kelibsiz", reply_markup=markup)
            bot.send_message(message.chat.id, "Ism familiyangizni kiriting")
            bot.register_next_step_handler(message, process_name_step)

def process_name_step(message):
    chat_id = message.chat.id
    if len(message.text.split()) == 2:
        name, last_name = message.text.split()
        if len(name) > 3 and len(last_name) > 3:
            user_data[chat_id] = {"chat_id": chat_id, "name": name, "last_name": last_name}
            bot.send_message(chat_id, "Viloyatingizni kiriting")
            bot.register_next_step_handler(message, process_city_step)
        else:
            bot.send_message(chat_id, "Ism va familiya uchun kamida 4 belgidan ko'p bo'lishi kerak. Iltimos, qayta kiriting.")
            bot.register_next_step_handler(message, process_name_step)
    else:
        bot.send_message(chat_id, "Iltimos, ism va familiyangizni to'liq kiriting. Masalan: Shohjahon O'rinboyev")
        bot.register_next_step_handler(message, process_name_step)

def process_city_step(message):
    chat_id = message.chat.id
    city = message.text.lower().capitalize().replace("ʼ", "'").replace("ʻ", "'")
    if city in address_data:
        user_data[chat_id]["city"] = city
        bot.send_message(chat_id, "Tumaningizni kiriting")
        bot.register_next_step_handler(message, process_tuman_step)
    else:
        bot.send_message(chat_id, "Bunday viloyat yo'q. Iltimos, qayta kiriting.")
        bot.register_next_step_handler(message, process_city_step)

def process_tuman_step(message):
    chat_id = message.chat.id
    tuman = message.text.lower().capitalize().replace("ʼ", "'").replace("ʻ", "'")
    city = user_data[chat_id]["city"]
    tuman1 = tuman + " tumani"
    if tuman in address_data[city] or tuman1 in address_data[city]:
        user_data[chat_id]["tuman"] = tuman
        bot.send_message(chat_id, "Sinfingizni kiriting")
        bot.register_next_step_handler(message, process_group_step)
    else:
        bot.send_message(chat_id, "Bunday tuman yo'q. Iltimos, qayta kiriting.")
        bot.register_next_step_handler(message, process_tuman_step)

def process_group_step(message):
    chat_id = message.chat.id
    sinf = message.text
    if sinf.isdigit() and 1 <= int(sinf) <= 12:
        user_data[chat_id]["group"] = sinf
        try:
            with open("user_info.json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []

        data.append(user_data[chat_id])

        with open("user_info.json", "w") as f:
            json.dump(data, f, indent=4)

        bot.send_message(chat_id, "Ma'lumotlaringiz saqlandi!")
    else:
        bot.send_message(chat_id, "Sinfni to'liq kiriting (raqam, 1-12 oralig'ida). Iltimos, qayta kiriting.")
        bot.register_next_step_handler(message, process_group_step)

@bot.message_handler(func=lambda message: message.text == "Ma'lumotlarni ko'rish")
def view_data(message):
    chat_id = message.chat.id
    try:
        with open("user_info.json", "r") as f:
            data = json.load(f)
            user_info = next((user for user in data if user["chat_id"] == chat_id), None)
            if user_info:
                info = f"Ism familiya: {user_info['name']} {user_info['last_name']}, Viloyat: {user_info['city']}, Tuman: {user_info['tuman']}, Sinf: {user_info['group']}"
                bot.send_message(message.chat.id, info)
            else:
                bot.send_message(message.chat.id, "Sizning ma'lumotlaringiz topilmadi.")
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Hech qanday ma'lumot yo'q.")

@bot.message_handler(func=lambda message: message.text == "O'rinni ko'rish")
def view_ranking(message):
    bot.send_message(message.chat.id, "O'rinni ko'rish")

@bot.message_handler(func=lambda message: message.text == "Test boshlash")
def start_test(message):
    bot.send_message(message.chat.id, "Test raqamingizni kiriting")
    bot.register_next_step_handler(message, get_test_number)

def get_test_number(message):
    test_number = message.text
    chat_id = message.chat.id
    try:
        with open("test_data.json", "r") as f:
            test_data = json.load(f)
    except FileNotFoundError:
        bot.send_message(chat_id, "Test ma'lumotlari yuklanmagan.")
        return

    try:
        with open("user_info.json", "r") as f:
            data = json.load(f)
            user_info = next((user for user in data if user["chat_id"] == chat_id), None)
            if user_info:
                sinf = user_info["group"]
            else:
                bot.send_message(chat_id, "Sinfingizga oid test topilmodi.")
                return
    except FileNotFoundError:
        bot.send_message(chat_id, "Foydalanuvchi ma'lumotlari yuklanmagan.")
        return

    test_sinflari = list(test_data.keys())
    if sinf not in test_sinflari:
        bot.send_message(chat_id, "Sizning sinfingizga oid test yo'q")
        return

    try:
        exam_questions = test_data[sinf][test_number]["Test"]
    except KeyError:
        bot.send_message(chat_id, "Bunday raqamda test topilmadi.")
        return

    user_answers = []

    def ask_question(question_index):
        if question_index < len(exam_questions):
            bot.send_message(chat_id, exam_questions[question_index])
            bot.register_next_step_handler(message, lambda m: receive_answer(m, question_index))
        else:
            bot.send_message(chat_id, "Test yakunlandi!")
            # Natijalarni saqlash yoki ko'rsatish uchun qo'shimcha kodlarni yozishingiz mumkin
            print("Test yakunlandi, natijalar saqlandi")

    def receive_answer(message, question_index):
        user_answers.append(message.text)
        ask_question(question_index + 1)

    ask_question(0)

@bot.message_handler(func=lambda message: message.text == "Ma'lumotlarni o'zgartirish")
def modify_data(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Ismni o'zgartirish")
    button2 = KeyboardButton("Viloyatni o'zgartirish")
    button3 = KeyboardButton("Tumanni o'zgartirish")
    button4 = KeyboardButton("Sinfni o'zgartirish")
    button5 = KeyboardButton("Orqaga")
    markup.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, "O'zgartirish uchun bo'limni tanlang", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Ismni o'zgartirish")
def change_name(message):
    bot.send_message(message.chat.id, "Yangi ismingizni kiriting")
    bot.register_next_step_handler(message, process_name_step)

@bot.message_handler(func=lambda message: message.text == "Viloyatni o'zgartirish")
def change_city(message):
    bot.send_message(message.chat.id, "Yangi viloyatingizni kiriting")
    bot.register_next_step_handler(message, process_city_step)

@bot.message_handler(func=lambda message: message.text == "Tumanni o'zgartirish")
def change_tuman(message):
    bot.send_message(message.chat.id, "Yangi tumaningizni kiriting")
    bot.register_next_step_handler(message, process_tuman_step)

@bot.message_handler(func=lambda message: message.text == "Sinfni o'zgartirish")
def change_group(message):
    bot.send_message(message.chat.id, "Yangi sinfingizni kiriting")
    bot.register_next_step_handler(message, process_group_step)

@bot.message_handler(func=lambda message: message.text == "Orqaga")
def go_back(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == "Yangi test yuklash")
def upload_test(message):
    bot.send_message(message.chat.id, "Test yuklanmoqda")
    # Admin uchun test yuklash kodini shu yerda yozishingiz mumkin

@bot.message_handler(func=lambda message: message.text == "Natijalarni ko'rish")
def view_results(message):
    bot.send_message(message.chat.id, "Natijalarni ko'rish")
    # Admin uchun natijalarni ko'rish kodini shu yerda yozishingiz mumkin

@bot.message_handler(func=lambda message: message.text == "Foydalanuvchilarni ko'rish")
def view_users(message):
    bot.send_message(message.chat.id, "Foydalanuvchilarni ko'rish")
    # Admin uchun foydalanuvchilarni ko'rish kodini shu yerda yozishingiz mumkin

bot.polling()
