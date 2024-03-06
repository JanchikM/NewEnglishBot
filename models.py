import sqlalchemy as sq
from sqlalchemy import Boolean, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User_Words(Base):
    __tablename__ = 'user_words'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer(), sq.ForeignKey('user.id'))
    words_id = sq.Column(sq.Integer(), sq.ForeignKey('words.id'))

    def __str__(self):
        return f'{self.user_id}, {s}'



class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40))
    id_tg = sq.Column(sq.BigInteger, unique=True)
    words = relationship('User_Words', backref='users')
    # words = relationship('User_Words', secondary=User_Words, backref='uuser')

    def __str__(self):
        return f'{self.name}'


class Words(Base):
    __tablename__ = 'words'

    id = sq.Column(sq.Integer, primary_key=True)
    en_word = sq.Column(sq.String(length=40), unique=True)
    translation = sq.Column(sq.String(length=40), unique=True)
    is_public = sq.Column(Boolean)
    user = relationship('User_Words', backref='wordss')
    # user = relationship('User_Words', secondary=User_Words, backref='wwords')

    def __str__(self):
        return f'{self.en_word}, {self.translation}'


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

