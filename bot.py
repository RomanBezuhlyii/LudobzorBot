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
from models.models import User, Casino
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


storage = MemoryStorage()
bot = Bot(token=cnfg.TOKEN)
dp = Dispatcher(bot, storage=storage)
s = Session()



"""@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Ок", reply_markup=types.ReplyKeyboardRemove())"""

#region functions with db
###Add user to database
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
    #s.close()

###Add information about casino to database
async def add_casino_to_db(type: str, name: str, description: str, link: str):
    casino = Casino(type=type,
                    casino_name=name,
                    casino_description=description,
                    link=link)
    s.add(casino)
    s.commit()

###Check admin permission on current user
async def check_is_admin(chat_id: str) -> bool:
    user = s.query(User).filter(User.chat_id==chat_id).first()
    if user == None:
        return False
    return user.is_admin

#endregion

#Admin panel
###Back to general admin page
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

#region managing admins
###Search and dispaly list of admins, without current user
@dp.callback_query_handler(lambda call: call.data == 'managing_admin')
async def managing_admin(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        admin_str = ""
        counter = 0
        admins = s.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            counter += 1
            admin_str += f"{counter}. Chat id: {admin.chat_id}, Никнейм: {admin.username}, Телефон: {admin.phone_number}\n"
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text=admin_str,
                                    message_id=c.message.message_id,
                                    reply_markup=kb.admin_controls_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Search and display all admins with chat id
@dp.callback_query_handler(lambda call: call.data == 'delete_admin')
async def delete_admin_list(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        admins = s.query(User).filter(User.is_admin == True).all()
        admins_delete_kb = InlineKeyboardMarkup()
        admin_str = ""
        counter = 0
        for admin in admins:
            if admin.chat_id != str(c.from_user.id):
                print(type(c.from_user.id))
                print(f"Айди из БД: {admin.chat_id}, Мое Айди: {c.from_user.id} не равно")
                admins_delete_kb.add(InlineKeyboardButton(f'{admin.chat_id}', callback_data=f'delete_{admin.chat_id}'))
                counter += 1
                admin_str += f"{counter}. Chat id: {admin.chat_id}, Никнейм: {admin.username}, Телефон: {admin.phone_number}\n"
        admins_delete_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text=admin_str,
                                    message_id=c.message.message_id,
                                    reply_markup=admins_delete_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)


###Delete admin which choose current user(admin)
@dp.callback_query_handler(lambda call: call.data.startswith('delete_'))
async def delete_admin(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        split_str = c.data.split('_')
        s.query(User).filter(User.chat_id==split_str[1]).delete()
        s.commit()
        #s.close()
        await bot.send_message(chat_id=int(split_str[1]),
                               text='Вы лишены прав администратора!\n Введите команду '
                                    '/start чтобы заново зайти в меню бота')
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Администратор успешно удален!',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.back_to_admin_menu_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Pae with add user variants
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

###Add user with username
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
            #s.close()
            await bot.send_message(chat_id=int(user.chat_id),
                                   text='Теперь у вас есть права администратора! /nВведите команду '
                                        '/start, чтобы открыть панель администратора')
            await m.answer(text="Администратор успешно добавлен!",
                           reply_markup=kb.back_to_admin_menu_kb)

###Add user with phone number
@dp.callback_query_handler(lambda call: call.data == 'add_from_phone')
async def add_admin_from_phone(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMAdminInfo.phone_number.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите номер телефона пользователя в формате '380XXXXXXXXX':",
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
            #s.close()
            await bot.send_message(chat_id=int(user.chat_id),
                                   text='Теперь у вас есть права администратора! /nВведите команду '
                                        '/start, чтобы открыть панель администратора')
            await m.answer(text="Администратор успешно добавлен!",
                           reply_markup=kb.back_to_admin_menu_kb)
#endregion

#Managing casino
###General page in Managin Casino submenu
@dp.callback_query_handler(lambda call: call.data == 'managing_casino')
async def managing_casino(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Сделайте выбор',
                                message_id=c.message.message_id,
                                reply_markup=kb.managing_casino_kb)

#region delete casino
###Search and display list of casino with label such as: top, bonus, welcome
@dp.callback_query_handler(lambda call: call.data.startswith('casinodel_'))
async def delete_top_casino_list(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        split_str = c.data.split('_')
        top_casino = s.query(Casino).filter(Casino.type == split_str[1]).all()
        print(top_casino)
        if(len(top_casino) == 0):
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text='В списке отсутствуют казино',
                                        message_id=c.message.message_id,
                                        reply_markup=kb.back_to_admin_menu_kb)
        else:
            top_casino_delete_kb = InlineKeyboardMarkup()
            casino_str = ""
            for casino in top_casino:
                top_casino_delete_kb.add(InlineKeyboardButton(f'{casino.id}. {casino.casino_name}', callback_data=f'cas_{split_str[1]}_{casino.id}'))
                casino_str += f"ID: {casino.id}. Название: {casino.casino_name}, Описание: {casino.casino_description}, Ссылка: {casino.link}\n"
            top_casino_delete_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text=casino_str,
                                        message_id=c.message.message_id,
                                        reply_markup=top_casino_delete_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Delete casino with id, which choose user
@dp.callback_query_handler(lambda call: call.data.startswith('cas_'))
async def delete_casino(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        split_str = c.data.split('_')
        print(split_str[2])
        del_numb = int(split_str[2])
        s.query(Casino).filter(Casino.id==int(split_str[2])).delete()
        s.commit()
        #s.close()
        if split_str[1]=='top':
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text='Казино успешно удалено!',
                                        message_id=c.message.message_id,
                                        reply_markup=kb.top_del_else_kb)
        elif split_str[1]=='bonus':
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text='Казино успешно удалено!',
                                        message_id=c.message.message_id,
                                        reply_markup=kb.bonus_del_else_kb)
        elif split_str[1]=='welcome':
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text='Казино успешно удалено!',
                                        message_id=c.message.message_id,
                                        reply_markup=kb.welcome_del_else_kb)
        elif split_str[1]=='nodeposite':
            await bot.edit_message_text(chat_id=c.from_user.id,
                                        text='Казино успешно удалено!',
                                        message_id=c.message.message_id,
                                        reply_markup=kb.no_deposite_del_else_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)
#endregion

#region work with top casino
###Variants of work with top casino list
@dp.callback_query_handler(lambda call: call.data == 'top_casino_a')
async def top_casino(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Что хотите сделать?',
                                message_id=c.message.message_id,
                                reply_markup=kb.top_casino_kb)

###Add top casino to list
@dp.callback_query_handler(lambda call: call.data == 'add_top')
async def add_top_casino(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMCasinoTOP.name.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите название казино",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMCasinoTOP.name)
async def load_casino_name(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = m.text
    await cl.FSMCasinoTOP.next()
    await m.reply(text='Введите описание бонусов')

@dp.message_handler(state=cl.FSMCasinoTOP.description)
async def load_casino_description(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = m.text
    await cl.FSMCasinoTOP.next()
    await m.reply(text='Введите ссылку на казино')

@dp.message_handler(state=cl.FSMCasinoTOP.link)
async def load_casino_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
    await add_casino_to_db(type='top',
                           name=data['name'],
                           description=data['description'],
                           link=data['link'])
    await m.reply(text='Казино добавлено успешно!',
                  reply_markup=kb.top_add_else_kb)
    await state.finish()
#endregion

#region work with top bonus casino
###Variants of work with top bonus in casino list
@dp.callback_query_handler(lambda call: call.data == 'top_bonus_a')
async def top_bonus(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Что хотите сделать?',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.top_bonus_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Add casino with top bonus
@dp.callback_query_handler(lambda call: call.data == 'add_bonus')
async def add_bonus_casino(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMCasinoBONUS.name.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите название казино",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMCasinoBONUS.name)
async def load_bonus_casino_name(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = m.text
    await cl.FSMCasinoBONUS.next()
    await m.reply(text='Введите описание бонусов')

@dp.message_handler(state=cl.FSMCasinoBONUS.description)
async def load_bonus_casino_description(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = m.text
    await cl.FSMCasinoBONUS.next()
    await m.reply(text='Введите ссылку на казино')

@dp.message_handler(state=cl.FSMCasinoBONUS.link)
async def load_bonus_casino_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
    await add_casino_to_db(type='bonus',
                           name=data['name'],
                           description=data['description'],
                           link=data['link'])
    await m.reply(text='Казино добавлено успешно!',
                  reply_markup=kb.bonus_add_else_kb)
    await state.finish()
#endregion

#region work with welcome bonus
###Variants of work with welcome bonus list
@dp.callback_query_handler(lambda call: call.data == 'welcome_bonus_a')
async def welcome_bonus(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Что хотите сделать?',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.welcome_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Add casino with welcome bonus
@dp.callback_query_handler(lambda call: call.data == 'add_welcome')
async def add_welcome_casino(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMCasinoWELCOME.name.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите название казино",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMCasinoWELCOME.name)
async def load_welcome_casino_name(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = m.text
    await cl.FSMCasinoWELCOME.next()
    await m.reply(text='Введите описание бонусов')

@dp.message_handler(state=cl.FSMCasinoWELCOME.description)
async def load_welcome_casino_description(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = m.text
    await cl.FSMCasinoWELCOME.next()
    await m.reply(text='Введите ссылку на казино')

@dp.message_handler(state=cl.FSMCasinoWELCOME.link)
async def load_welcome_casino_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
    await add_casino_to_db(type='welcome',
                           name=data['name'],
                           description=data['description'],
                           link=data['link'])
    await m.reply(text='Казино добавлено успешно!',
                  reply_markup=kb.welcome_add_else_kb)
    await state.finish()
#endregion

#region work with no deposite bonus
###Variants of work with no deposite bonus list
@dp.callback_query_handler(lambda call: call.data == 'nodeposite_a')
async def welcome_bonus(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text='Что хотите сделать?',
                                    message_id=c.message.message_id,
                                    reply_markup=kb.no_deposite_kb)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

###Add casino with welcome bonus
@dp.callback_query_handler(lambda call: call.data == 'add_nodeposite')
async def add_welcome_casino(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMCasinoNODEPOSITE.name.set()
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите название казино",
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMCasinoNODEPOSITE.name)
async def load_welcome_casino_name(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = m.text
    await cl.FSMCasinoNODEPOSITE.next()
    await m.reply(text='Введите описание бонусов')

@dp.message_handler(state=cl.FSMCasinoNODEPOSITE.description)
async def load_welcome_casino_description(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = m.text
    await cl.FSMCasinoNODEPOSITE.next()
    await m.reply(text='Введите ссылку на казино')

@dp.message_handler(state=cl.FSMCasinoNODEPOSITE.link)
async def load_welcome_casino_link(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = m.text
    await add_casino_to_db(type='nodeposite',
                           name=data['name'],
                           description=data['description'],
                           link=data['link'])
    await m.reply(text='Казино добавлено успешно!',
                  reply_markup=kb.no_deposite_add_else_kb)
    await state.finish()
#endregion

#Work with spam
###Spam general page
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

#region spam in telegram
###Start page to spam in telegram
@dp.callback_query_handler(lambda call: call.data == 'spam_to_tg')
async def spam_to_tg(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMSpam.spam_message.set()
        template_text = f"Не сбавляем обороты!🎰  \n" \
                        f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
                        f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на ТУТ БУДЕТ ВСТАВЛЕН ВАШ ТЕКСТ\n" \
                        f"💰Проходи и забирай свои подарки"
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите текст рассылки, который будет вставлен в шаблон: " + "\n" + template_text,
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

###Confirm message text
@dp.callback_query_handler(lambda call: call.data == 'confirm_spam_tg')
async def confirm_spam(c: types.CallbackQuery):
    users = s.query(User).filter(User.phone_number!='No').all()
    msg_text = f"Не сбавляем обороты!🎰  \n" \
               f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
               f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на {c.message.text}\n" \
               f"💰Проходи и забирай свои подарки"
    for user in users:
        if user.is_admin == False:
            await bot.send_message(chat_id=user.chat_id,
                                   text=msg_text)
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Рассылка была отправлена успешно!',
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_admin_menu_kb)
#endregion

#region spam in email
###Start spam in email
@dp.callback_query_handler(lambda call: call.data == 'spam_to_email')
async def spam_to_tg(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMSpamEmail.text.set()
        template_text = f"Не сбавляем обороты!🎰  \n" \
               f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
               f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на ТУТ БУДЕТ ВСТАВЛЕН ВАШ ТЕКСТ\n" \
               f"💰Проходи и забирай свои подарки"
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите текст рассылки, который будет вставлен в шаблон: " + "\n" + template_text,
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMSpamEmail.text)
async def load_spam_admin(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spam'] = m.text
        await bot.send_message(chat_id=m.from_user.id,
                               text='Данный текст рассылки верен?')
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"{data['spam']}",
                               reply_markup=kb.admin_email_spam_confirm_kb)
        await state.finish()

###Confirm email message text
@dp.callback_query_handler(lambda call: call.data == 'confirm_spam_email')
async def confirm_spam(c: types.CallbackQuery):

    password = cnfg.password
    users = s.query(User).filter(User.email!='No').all()
    msg_text = f"Не сбавляем обороты!🎰  \n" \
               f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
               f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на {c.message.text}\n" \
               f"💰Проходи и забирай свои подарки"

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(cnfg.sender, password)
    for user in users:
        if user.is_admin == False:
            msg = MIMEMultipart()
            msg['Subject'] = cnfg.subject
            msg['From'] = cnfg.sender
            msg.attach(MIMEText(msg_text, 'plain'))
            msg['To']=user.email
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Рассылка была отправлена успешно!',
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_admin_menu_kb)
#endregion

#region spam in all chanels
###Start spam in telegram and email
@dp.callback_query_handler(lambda call: call.data == 'spam_to_everything')
async def spam_to_tg(c: types.CallbackQuery):
    current_user_admin = await check_is_admin(c.from_user.id)
    if current_user_admin == True:
        await cl.FSMSpamAll.text.set()
        template_text = f"Не сбавляем обороты!🎰  \n" \
                        f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
                        f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на ТУТ БУДЕТ ВСТАВЛЕН ВАШ ТЕКСТ\n" \
                        f"💰Проходи и забирай свои подарки"
        await bot.edit_message_text(chat_id=c.from_user.id,
                                    text="Введите текст рассылки, который будет вставлен в шаблон: " + "\n" + template_text,
                                    message_id=c.message.message_id)
    else:
        await bot.send_message(chat_id=c.from_user.id,
                               text="Обратитесь к администратору, чтобы получить доступ!",
                               reply_markup=kb.back_to_menu_kb)

@dp.message_handler(state=cl.FSMSpamAll.text)
async def load_spam_admin(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spam'] = m.text
        await bot.send_message(chat_id=m.from_user.id,
                               text='Отправлять данное сообщение как рассылку?')
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"{data['spam']}",
                               reply_markup=kb.admin_all_spam_confirm_kb)
        await state.finish()

###Confirm message text for all users
@dp.callback_query_handler(lambda call: call.data == 'confirm_spam_all')
async def confirm_spam(c: types.CallbackQuery):
    password = cnfg.password
    users = s.query(User).filter(User.email != 'No').all()
    msg_text = f"Не сбавляем обороты!🎰  \n" \
               f"Врываемся в будни на волне эпических выигрышей!🤑\n" \
               f"💸Горячие промокоды,  эксклюзивные бонусы все это ждет тебя на {c.message.text}\n" \
               f"💰Проходи и забирай свои подарки"

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(cnfg.sender, password)
    for user in users:
        if user.is_admin == False:
            msg = MIMEMultipart()
            msg['Subject'] = cnfg.subject
            msg['From'] = cnfg.sender
            msg.attach(MIMEText(msg_text, 'plain'))
            msg['To'] = user.email
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    users_tg = s.query(User).filter(User.phone_number!='No').all()
    for user in users_tg:
        if user.is_admin == False:
            await bot.send_message(chat_id=user.chat_id,
                                   text=msg_text)
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Рассылка была отправлена успешно!',
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_admin_menu_kb)
#endregion



#Users bot interface
###Start function
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

###Back to main menu function
@dp.callback_query_handler(lambda call: call.data == 'back_to_menu')
async def telegram_contacts(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                                "тебе лучшие казино для игры и выигрыша",
                                message_id=c.message.message_id,
                                reply_markup=kb.main_menu_kb)

###Welcome bonus page
@dp.callback_query_handler(lambda call: call.data == 'welcome_bonus')
async def welcome_bonus(c: types.CallbackQuery):
    m_text = "Вам, как пользователю нашего сайта, полагается бонус, просто введите промокод LUDOBZOR при регистрации в следующих казино:\n"
    casino = s.query(Casino).filter(Casino.type == 'welcome').all()
    count = 1
    for cas in casino:
        temp_text = f"{count}. " + link(cas.casino_name, cas.link) + ". " + cas.casino_description + '\n'
        m_text += temp_text
        count += 1
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text=m_text,
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

###No deposite bonus page
@dp.callback_query_handler(lambda call: call.data == 'no_deposite')
async def no_deposite_bonus(c: types.CallbackQuery):
    m_text = "Бездепозитные бонусы по промокоду LUDOBZOR:\n"
    casino = s.query(Casino).filter(Casino.type == 'nodeposite').all()
    count = 1
    for cas in casino:
        temp_text = f"{count}. " + link(cas.casino_name, cas.link) + ". " + cas.casino_description + '\n'
        m_text += temp_text
        count += 1
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text=m_text,
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

###Top casino page
@dp.callback_query_handler(lambda call: call.data == 'casino_top')
async def welcome_bonus(c: types.CallbackQuery):
    m_text = "Сейчас лучшие для выбора казино это:\n"
    casino = s.query(Casino).filter(Casino.type == 'top').all()
    count = 1
    for cas in casino:
        temp_text = f"{count}. " + link(cas.casino_name, cas.link) + ". " + cas.casino_description + '\n'
        m_text += temp_text
        count += 1
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text=m_text,
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

###Casino bonus page
@dp.callback_query_handler(lambda call: call.data == 'bonus_top')
async def welcome_bonus(c: types.CallbackQuery):
    m_text = "Самые большие бонусы:\n"
    casino = s.query(Casino).filter(Casino.type == 'bonus').all()
    count = 1
    for cas in casino:
        temp_text = f"{count}. " + link(cas.casino_name, cas.link) + ". " + cas.casino_description + '\n'
        m_text += temp_text
        count += 1
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text=m_text,
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

###Support page
@dp.callback_query_handler(lambda call: call.data == 'support')
async def support(c: types.CallbackQuery):
    await bot.edit_message_text(chat_id=c.from_user.id,
                                text='Нажмите на ссылку ниже, чтобы перейти к общению с оператором:\n' +
                                     link('Поддержка Ludobzor',
                                          url=cnfg.support_link),
                                parse_mode="Markdown",
                                message_id=c.message.message_id,
                                reply_markup=kb.back_to_menu_kb)

#region add telegram contacts
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
                                 email='No',
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
                                 email='No',
                                 is_admin=False)
            await bot.send_message(chat_id=m.from_user.id,
                                   text=f"Номер телефона:{data['phone_number']}")
            await state.finish()
    await m.answer("Контактные данные успешно отправлены", reply_markup=types.ReplyKeyboardRemove())
    await m.answer(text="Привет! Я - Лудобзор-Бот. Я помогу подобрать "
                       "тебе лучшие казино для игры и выигрыша",
                   reply_markup=kb.main_menu_kb)
#endregion

#region add whatsapp contacts
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
#endregion

#region add email
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
#endregion

@dp.callback_query_handler(lambda call: call.data == 'jivo_email')
async def email_contacts(c: types.CallbackQuery, state: FSMContext):
    await cl.FSMAdminEmail.email.set()
    await bot.send_message(c.from_user.id,
                           text="Введите email пользователя в формате: \nludobzor@ludobzor.com")

@dp.message_handler(state=cl.FSMAdminEmail.email)
async def load_email(m: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = m.text
        await add_user_to_db(chat_id='No',
                             username='No',
                             first_name='No',
                             second_name='No',
                             phone_number='No',
                             email=data['email'],
                             is_admin=False)
        await bot.send_message(chat_id=m.from_user.id,
                               text=f"Email:{data['email']}")
        await state.finish()
    await m.answer("Контактные данные успешно добавлены")
    await m.answer(text="Хотите добавит еще пользователя?",
                   reply_markup=kb.add_jivo_email_kb)

'''@dp.message_handler(text="Telegram")
async def telegram_contacts(message: types.Message):
    await message.reply('Введите свой номер телефона Telegram')'''

if __name__ == "__main__":
    #create_database()
    executor.start_polling(dp)