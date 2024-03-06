import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from table_funk import add_user, random_words, random_answer, filling_table, add_word_user, del_word_user

print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = '6915568621:AAGeOLp_dBvY_BHqVeT21BaIu_-UoGU4mKo'
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        userStep[cid] = 0
        add_user(message.from_user.first_name, cid)
        bot.send_message(cid, "Hello, stranger, let study English...")
        filling_table()
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    target_word, translate = random_words(cid)
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = random_answer(target_word)  # брать из БД
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n🇷🇺 {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid, "Введите слово на английском языке для удаления:")
    bot.register_next_step_handler(message, process_user_deleteinput)


def process_user_deleteinput(message):
    cid = message.chat.id
    words = str(message.text)
    if del_word_user(words, cid):
        bot.send_message(cid, "Пара слов успешно удалена")
        create_cards(message)
    else:
        bot.send_message(cid, "Данное слово не подлежит удалению, либо его нет в списке слов")
        create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid, "Введите слово на английском и русском языках, "
                          "для добавления в таблицу слов. "
                          "Ввод осуществляется через пробел. "
                          "Перед отправкой убедитесь в правильности введенных слов. "
                          "Вводить слова рекомендуется с заглавной буквы")
    bot.register_next_step_handler(message, user_input_word)


def user_input_word(message):
    cid = message.chat.id
    words = str(message.text).split()
    if len(words) == 2:
        word_add_eng, word_add_rus = words
        if add_word_user(word_add_eng, word_add_rus, cid):
            bot.send_message(cid, "Добавлена новая пара слов")
            create_cards(message)
        else:
            bot.send_message(cid, "Слово уже было добавлено")
            create_cards(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
