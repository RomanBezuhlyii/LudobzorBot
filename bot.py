from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import text, hlink, link
import config as cnfg
import keyboards as kb
import classes as cl
from models.database import create_database, Session
from models.models import User


storage = MemoryStorage()
bot = Bot(token=cnfg.TOKEN)
dp = Dispatcher(bot, storage=storage)
s = Session()

"""@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Ок", reply_markup=types.ReplyKeyboardRemove())"""

async def add_user_to_db(chat_id: str, first_name: str, second_name: str, username: str, phone_number: str, email: str, is_admin: bool):
    user = User(chat_id=chat_id,
                username=username,
                first_name=first_name,
                second_name=second_name,
                phone_number=phone_number,
                email=email,
                is_admin=is_admin)
    s.add(user)
    s.commit()
    s.close()

async def check_is_admin(chat_id: str) -> bool:
    user = s.query(User).filter(User.chat_id==chat_id).first()
    if user == None:
        return False
    return user.is_admin


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    current_user_admin = await check_is_admin(message.from_user.id)
    if current_user_admin == True:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Добро пожаловать в администратувную панель!',
                               reply_markup=kb.admin_menu_kb)
    else:
        r = s.query(User).filter(User.chat_id==message.from_user.id).all()
        if len(r) == 0:
            await message.reply("Для пользования ботом нужно добавить свои "
                                "контактные данные", reply_markup=kb.start_inline_kb)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                                        "тебе лучшие казино для игры и выигрыша",
                                   reply_markup=kb.main_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'back_to_admin_menu')
async def admin_menu(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Добро пожаловать в администратувную панель!',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.admin_menu_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'managing_admin')
async def managing_admin(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        admin_str = ""
        admins = s.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            admin_str += f"Chat id: {admin.chat_id}, Никнейм: {admin.username}, Телефон: {admin.phone_number}\n"
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text=admin_str,
                                    message_id=c.message.message_id,
                                    reply_markup=kb.admin_controls_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'delete_admin')
async def delete_admin_list(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        admins = s.query(User).filter(User.is_admin == True).all()
        admins_delete_kb = InlineKeyboardMarkup()
        admin_str = ""
        for admin in admins:
            if admin.chat_id != str(c.from_user.id):
                print(type(c.from_user.id))
                print(f"Айди из БД: {admin.chat_id}, Мое Айди: {c.from_user.id} не равно")
                admins_delete_kb.add(InlineKeyboardButton(f'{admin.chat_id}', callback_data=f'delete_{admin.chat_id}'))
                admin_str += f"Chat id: {admin.chat_id}, Никнейм: {admin.username}, Телефон: {admin.phone_number}\n"
        admins_delete_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text=admin_str,
                                    message_id=c.message.message_id,
                                    reply_markup=admins_delete_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data.startswith('delete_'))
async def delete_admin(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        split_str = c.data.split('_')
        s.query(User).filter(User.chat_id==split_str[1]).delete()
        s.commit()
        s.close()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Администратор успешно удален!',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.back_to_admin_menu_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'add_admin')
async def add_admin_choice(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Перед добавлением в администраторы, пользователь должен '
                                         'предоставить контактные данные на начальном экране бота. '
                                         'Выберите, как именно хотите добавить администратора.',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.add_admin_choice_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'add_from_username')
async def add_admin_from_username(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMAdminInfo.username.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите никнейм пользователя в Телеграмм без '@'",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMAdminInfo.username)
async def load_username_admin(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['username'] = m.text
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"Username: {data['username']}")
        user = s.query(User).filter(User.username==data['username']).first()
        await state.finish()
        if user == None:
            await m.answer(text="Человека с таким никнеймом нету в базе данных.\n"
                                "1. Проверьте правильность ввода никнейма\n"
                                "2. Убедитесь, что пользователь передал контактную информацию боту",
                           reply_markup=kb.enter_again_admin_username_kb)
        else:
            user.is_admin = True
            s.commit()
            s.close()
            await m.answer(text="Администратор успешно добавлен!",
                           reply_markup=kb.back_to_admin_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'add_from_phone')
async def add_admin_from_phone(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMAdminInfo.phone_number.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите номер телефона пользователя в формате '+380XXXXXXXXX':",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMAdminInfo.phone_number)
async def load_phone_admin(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = m.text
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"Phone number: {data['phone']}")
        user = s.query(User).filter(User.phone_number==data['phone']).first()
        await state.finish()
        if user == None:
            await m.answer(text="Человека с таким номером телефона нету в базе данных.\n"
                                "1. Проверьте правильность ввода номера телефона\n"
                                "2. Убедитесь, что пользователь передал контактную информацию боту",
                           reply_markup=kb.enter_again_admin_phone_kb)
        else:
            user.is_admin = True
            s.commit()
            s.close()
            await m.answer(text="Администратор успешно добавлен!",
                           reply_markup=kb.back_to_admin_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'spam')
async def spam(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Выберите канал расспостранения рассылки:',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.admin_spam_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'spam_to_tg')
async def spam_to_tg(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMSpam.spam_message.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите текст рассылки: ",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMSpam.spam_message)
async def load_spam_admin(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spam'] = m.text
        await bot.send_message(chat_id=m.from_user.id,
                               text='Отправлять данное сообщение как рассылку?')
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"{data['spam']}",
                               reply_markup=kb.admin_spam_confirm_kb)
        await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'confirm_spam')
async def confirm_spam(c: types.CallbackQuery):
    users = s.query(User).filter().all()
    for user in users:
        if user.is_admin == False:
            await bot.send_message(chat_id=user.chat_id,
                                   text=c.message.text)
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Рассылка была отправлена успешно!',
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_admin_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'back_to_menu')
async def telegram_contacts(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                                "тебе лучшие казино для игры и выигрыша",
                                message_id=c.message.message_id,
                                reply_markup=kb.main_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'welcome_bonus')
async def welcome_bonus(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text="Вам, как пользователю нашего сайта, полагается бонус "
                                "в размере XXX YYY! Просто введите промокод LUDOBZOR при "
                                "регистрации в следующих казино:\n "+
                                link('Casino A',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/'),
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'casino_top')
async def welcome_bonus(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text="Сейчас лучшие для выбора казино это:\n "+
                                link('Casino A',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/'),
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'bonus_top')
async def welcome_bonus(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text="Самые большие бонусы:\n "+
                                link('Casino A',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/') + '\n' +
                                link('Casino B',
                                     url='https://ludobzor.com/bonusy/'),
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'telegram_contacts')
async def telegram_contacts(c: types.CallbackQuery, state: FSMContext):
    await cl.FSMContactsPhone.phone.set()
    await bot.send_message(c.from_user.id,
                           text="Отправьте свой номер телефона, который привязан к "
                                "Telegram. Для этого нажмите 'Отправить свой контакт' или "
                                "введите телефон формата: 38ХХХХХХХХХХ",
                           reply_markup=kb.phone_numb_kb)

@dp.message_handler(state=cl.FSMContactsPhone.phone, content_types=['contact','text'])
async def load_tg_phone(m: types.Message, state: FSMContext):
    if m.contact != None:
        async with state.proxy() as data:
            data['phone_number'] = m.contact.phone_number
            await add_user_to_db(chat_id=m.from_user.id,
                                 username=m.from_user.username,
                                 first_name=m.from_user.first_name,
                                 second_name=m.from_user.last_name,
                                 phone_number=data['phone_number'],
                                 email='None',
                                 is_admin=False)
            await bot.send_message(chat_id=m.from_user.id,
                                   text=f"Номер телефона:{data['phone_number']}")
            await state.finish()
    else:
        async with state.proxy() as data:
            data['phone_number'] = m.text
            await add_user_to_db(chat_id=m.from_user.id,
                                 username=m.from_user.username,
                                 first_name=m.from_user.first_name,
                                 second_name=m.from_user.last_name,
                                 phone_number=data['phone_number'],
                                 email='None',
                                 is_admin=False)
            await bot.send_message(chat_id=m.from_user.id,
                                   text=f"Номер телефона:{data['phone_number']}")
            await state.finish()
    await m.answer("Контактные данные успешно отправлены", reply_markup=types.ReplyKeyboardRemove())
    await m.answer(text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                       "тебе лучшие казино для игры и выигрыша",
                   reply_markup=kb.main_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'whatsapp_contacts')
async def whatsapp_contacts(c: types.CallbackQuery, state: FSMContext):
    await cl.FSMContactsPhone.phone.set()
    await bot.send_message(c.from_user.id,
                           text="Отправьте свой номер телефона, который привязан к "
                                "WhatsApp. Для этого нажмите 'Отправить свой контакт' или "
                                "введите телефон формата: 38ХХХХХХХХХХ",
                           reply_markup=kb.phone_numb_kb)

@dp.message_handler(state=cl.FSMContactsPhone.phone, content_types=['contact','text'])
async def load_wapp_phone(m: types.Message, state: FSMContext):
    if m.contact != None:
        async with state.proxy() as data:
            data['phone_number'] = m.contact.phone_number
            await bot.send_message(chat_id=m.from_user.id,
                                   text=f"Номер телефона:{data['phone_number']}")
            await state.finish()
    else:
        async with state.proxy() as data:
            data['phone_number'] = m.text
            await bot.send_message(chat_id=m.from_user.id,
                                   text=f"Номер телефона:{data['phone_number']}")
            await state.finish()
    await m.answer("Контактные данные успешно отправлены", reply_markup=types.ReplyKeyboardRemove())
    await m.answer(text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                       "тебе лучшие казино для игры и выигрыша",
                   reply_markup=kb.main_menu_kb)

@dp.callback_query_handler(lambda call: call.data == 'email_contacts')
async def email_contacts(c: types.CallbackQuery, state: FSMContext):
    await cl.FSMContactsEmail.email.set()
    await bot.send_message(c.from_user.id,
                           text="Отправьте свой адресс email, формата: \nludobzor@ludobzor.com")

@dp.message_handler(state=cl.FSMContactsEmail.email)
async def load_email(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = m.text
        await add_user_to_db(chat_id=m.from_user.id,
                             username=m.from_user.username,
                             first_name=m.from_user.first_name,
                             second_name=m.from_user.last_name,
                             phone_number='No',
                             email=data['email'],
                             is_admin=False)
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"Email:{data['email']}")
        await state.finish()
    await m.answer("Контактные данные успешно отправлены")
    await m.answer(text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                       "тебе лучшие казино для игры и выигрыша",
                   reply_markup=kb.main_menu_kb)

'''@dp.message_handler(text="Telegram")
async def telegram_contacts(message: types.Message):
    await message.reply('Введите свой номер телефона Telegram')'''

if __name__ == "__main__":
    #create_database()
    executor.start_polling(dp)