from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from models.database import Base

class Casino(Base):
    __tablename__ = 'casino'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    casino_name = Column(String)
    casino_description = Column(String)
    link = Column(String)

    def __init__(self, type: str, casino_name: str, casino_description: str, link: str):
        self.type = type
        self.casino_name = casino_name
        self.casino_description = casino_description
        self.link = link

    def __repr__(self):
        info: str = f'Казино: {self.casino_name}, Ссылка: {self.link}'
        return info

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String)
    first_name = Column(String)
    second_name = Column(String)
    username = Column(String)
    phone_number = Column(String)
    email = Column(String)
    is_admin = Column(Boolean)


    def __init__(self, chat_id: str, first_name: str, second_name: str, username: str, phone_number: str, email: str, is_admin: bool):
        self.chat_id = chat_id
        self.first_name = first_name
        self.second_name = second_name
        self.username = username
        self.phone_number = phone_number
        self.email = email
        self.is_admin = is_admin

    def __repr__(self):
        info: str = f'Пользователь: {self.username}, Номер телефона: {self.phone_number}, Email: {self.email}, Администратор: {self.is_admin}'
        return info

