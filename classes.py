from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, types, Dispatcher

class FSMContactsPhone(StatesGroup):
    phone = State()

class FSMContactsEmail(StatesGroup):
    email = State()

class FSMAdminEmail(StatesGroup):
    email = State()

class FSMAdminInfo(StatesGroup):
    phone_number = State()
    username = State()

class FSMSpam(StatesGroup):
    spam_message = State()

class FSMSpamEmail(StatesGroup):
    text = State()

class FSMSpamAll(StatesGroup):
    text = State()

class FSMCasinoTOP(StatesGroup):
    name = State()
    description = State()
    link = State()

class FSMCasinoBONUS(StatesGroup):
    name = State()
    description = State()
    link = State()

class FSMCasinoWELCOME(StatesGroup):
    name = State()
    description = State()
    link = State()

class FSMCasinoNODEPOSITE(StatesGroup):
    name = State()
    description = State()
    link = State()
