from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URI = 'postgresql://postgres:Atlas@localhost/Atlas'

# Tworzenie silnika bazy danych
engine = create_engine(DATABASE_URI)

# Tworzenie sesji
Session = sessionmaker(bind=engine)
session = Session()

# Podstawowa klasa deklaratywna
Base = declarative_base()

class Language(Base):
    __tablename__ = 'languages'
    language_id = Column(Integer, primary_key=True)
    language_name = Column(String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Language {self.language_name}>'

class TextModel(Base):
    __tablename__ = 'texts'
    text_id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)

    def __repr__(self):
        return f'<Text {self.text_id}>'

class Translation(Base):
    __tablename__ = 'translations'
    translation_id = Column(Integer, primary_key=True, autoincrement=True)
    text_id = Column(Integer, ForeignKey('texts.text_id'), nullable=False)
    language_id = Column(Integer, ForeignKey('languages.language_id'), nullable=False)
    translation_text = Column(Text, nullable=False)

    text = relationship('TextModel', backref='translations')
    language = relationship('Language', backref='translations')

    __table_args__ = (UniqueConstraint('text_id', 'language_id', name='uix_text_language'),)

    def __repr__(self):
        return f'<Translation {self.translation_id}>'