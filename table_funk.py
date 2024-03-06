import random

from sqlalchemy import func, delete

from Start_tables import session
from models import User, Words, User_Words


# Функция добавление пользователя в Базу данных
def add_user(name, id_tg):
    file = []
    user_info = User(name=name, id_tg=id_tg)
    for i in session.query(User).all():
        file.append(i.id_tg)
    if id_tg not in file:
        session.add(user_info)
        session.commit()
    else:
        print(f'Пользователь {name} приступил к обучению')


# Функция заполнения промежуточной таблицы
def filling_table():
    user = 0
    for user_id in session.query(User).all():
        user = user_id.id
    for words_id in session.query(Words).filter_by(is_public=True).all():
        add_info = User_Words(user_id=user, words_id=words_id.id)
        session.add(add_info)
        session.commit()


# Функция выбора рандомного слова из имеющихся
def random_words(user_id):
    user = session.query(User).filter_by(id_tg=user_id).first()
    qwer = session.query(Words).join(User_Words).filter_by(user_id=user.id).order_by(func.random()).first()
    target_word = (list(str(qwer).split(", ")))[0]
    translate_word = (list(str(qwer).split(", ")))[1]
    return target_word, translate_word


# Функция добавления трех рандомных ответов из Базы данных
def random_answer(t_word):
    answer_list = []
    for i in session.query(Words):
        answer_list.append(((list(str(i).split(", ")))[0]))
    if t_word in answer_list:
        answer_list.remove(t_word)
    others = random.sample(answer_list, 3)
    return others


# Функция добавления слова в базу данных
def add_word_user(eng_word, rus_word, cid):
    file = []
    www = Words(en_word=eng_word, translation=rus_word)
    for i in session.query(Words).all():
        file.append(i.en_word)
    if eng_word in file:
        print('Добавляемая пара слов уже есть в базе')
        return False
    else:
        session.add(www)
        session.commit()
        for user_id in session.query(User).all():
            if user_id.id_tg == cid:
                new_info_user_word = User_Words(user_id=user_id.id, words_id=www.id)
                session.add(new_info_user_word)
                session.commit()
                print('Пара слов добавлена')
        return True


# Функция удаления слова из базы данных
def del_word_user(eng_word, cid):
    file = []
    for i in session.query(Words).all():
        file.append(i.en_word)
    for user_id in session.query(User).filter_by(id_tg=cid).all():
        if eng_word in file:
            www = session.query(Words).filter_by(en_word=eng_word).first()
            if www.is_public is None:
                new_info_user_word = session.query(User_Words).filter_by(words_id=www.id, user_id=user_id.id).first()
                session.delete(new_info_user_word)
                session.commit()
                session.delete(www)
                session.commit()
                print('Слово успешно удалено')
                return True
            else:
                return False
        else:
            print('Данного слова нет в базе')
            return False
