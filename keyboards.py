from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import config as cnfg

start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("Telegram"))
start_kb.add(KeyboardButton("WhatsApp"))
start_kb.add(KeyboardButton("Email"))

start_inline_kb = InlineKeyboardMarkup()
start_inline_kb.add(InlineKeyboardButton("Telegram", callback_data='telegram_contacts'))
start_inline_kb.add(InlineKeyboardButton("WhatsApp", callback_data='whatsapp_contact'))
start_inline_kb.add(InlineKeyboardButton("Email", callback_data='email_contacts'))

phone_numb_kb = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
phone_numb_kb.add(KeyboardButton("Отправить свой контакт", request_contact=True))

main_menu_kb = InlineKeyboardMarkup()
main_menu_kb.add(InlineKeyboardButton("Приветственный бонус", callback_data='welcome_bonus'))
main_menu_kb.row(InlineKeyboardButton("Топ казино", callback_data='casino_top'), InlineKeyboardButton('Топ бонусов', callback_data='bonus_top'))
main_menu_kb.add(InlineKeyboardButton('Задать вопрос оператору', callback_data='operator'))

back_to_menu_kb = InlineKeyboardMarkup()
back_to_menu_kb.add(InlineKeyboardButton("Вернуться назад", callback_data='back_to_menu'))

admin_menu_kb = InlineKeyboardMarkup()
admin_menu_kb.add(InlineKeyboardButton('Рассылка', callback_data='spam'))
admin_menu_kb.add(InlineKeyboardButton('Управление администраторами', callback_data='managing_admin'))

admin_controls_kb = InlineKeyboardMarkup()
admin_controls_kb.add(InlineKeyboardButton('Добавление администратора', callback_data='add_admin'))
admin_controls_kb.add(InlineKeyboardButton('Удаление администратора', callback_data='delete_admin'))
admin_controls_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

add_admin_choice_kb = InlineKeyboardMarkup()
add_admin_choice_kb.add(InlineKeyboardButton('Добавить по никнейму', callback_data='add_from_username'))
add_admin_choice_kb.add(InlineKeyboardButton('Добавить по номеру телефона', callback_data='add_from_phone'))
add_admin_choice_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

enter_again_admin_username_kb = InlineKeyboardMarkup()
enter_again_admin_username_kb.add(InlineKeyboardButton('Повторить поиск по никнейму', callback_data='add_from_username'))
enter_again_admin_username_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

enter_again_admin_phone_kb = InlineKeyboardMarkup()
enter_again_admin_phone_kb.add(InlineKeyboardButton('Повторить поиск по номеру телефона', callback_data='add_from_phone'))
enter_again_admin_phone_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))