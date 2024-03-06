import json

import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

from models import create_tables, Words

DSN = 'postgresql://postgres:Dental_67@localhost:5432/NewEnglishbotdb'
engine = sq.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


with open("start_words.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for record in data:
        model = {
            "words": Words
        }[record.get('model')]
        session.add(model(**record.get('fields')))
session.commit()


