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
main_menu_kb.add(InlineKeyboardButton('Задать вопрос оператору', callback_data='support'))

back_to_menu_kb = InlineKeyboardMarkup()
back_to_menu_kb.add(InlineKeyboardButton("Вернуться назад", callback_data='back_to_menu'))

back_to_admin_menu_kb = InlineKeyboardMarkup()
back_to_admin_menu_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_menu_kb = InlineKeyboardMarkup()
admin_menu_kb.add(InlineKeyboardButton('Рассылка', callback_data='spam'))
admin_menu_kb.add(InlineKeyboardButton('Управление администраторами', callback_data='managing_admin'))
admin_menu_kb.add(InlineKeyboardButton('Управление списками казино', callback_data='managing_casino'))

managing_casino_kb = InlineKeyboardMarkup()
managing_casino_kb.add(InlineKeyboardButton('Список топ казино', callback_data='top_casino_a'))
managing_casino_kb.add(InlineKeyboardButton('Список топ бонусов', callback_data='top_bonus_a'))
managing_casino_kb.add(InlineKeyboardButton('Приветственный бонус', callback_data='welcome_bonus_a'))
managing_casino_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

top_casino_kb = InlineKeyboardMarkup()
top_casino_kb.add(InlineKeyboardButton('Добавить', callback_data='add_top'))
top_casino_kb.add(InlineKeyboardButton('Удалить', callback_data='casinodel_top'))
top_casino_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

top_add_else_kb = InlineKeyboardMarkup()
top_add_else_kb.add(InlineKeyboardButton('Добавить еще', callback_data='add_top'))
top_add_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

top_del_else_kb = InlineKeyboardMarkup()
top_del_else_kb.add(InlineKeyboardButton('Удалить еще', callback_data='casinodel_top'))
top_del_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

top_bonus_kb = InlineKeyboardMarkup()
top_bonus_kb.add(InlineKeyboardButton('Добавить', callback_data='add_bonus'))
top_bonus_kb.add(InlineKeyboardButton('Удалить', callback_data='casinodel_bonus'))
top_bonus_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

bonus_add_else_kb = InlineKeyboardMarkup()
bonus_add_else_kb.add(InlineKeyboardButton('Добавить еще', callback_data='add_bonus'))
bonus_add_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

bonus_del_else_kb = InlineKeyboardMarkup()
bonus_del_else_kb.add(InlineKeyboardButton('Удалить еще', callback_data='casinodel_bonus'))
bonus_del_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

welcome_kb = InlineKeyboardMarkup()
welcome_kb.add(InlineKeyboardButton('Добавить', callback_data='add_welcome'))
welcome_kb.add(InlineKeyboardButton('Удалить', callback_data='casinodel_welcome'))
welcome_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

welcome_add_else_kb = InlineKeyboardMarkup()
welcome_add_else_kb.add(InlineKeyboardButton('Добавить еще', callback_data='add_welcome'))
welcome_add_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

welcome_del_else_kb = InlineKeyboardMarkup()
welcome_del_else_kb.add(InlineKeyboardButton('Удалить еще', callback_data='casinodel_welcome'))
welcome_del_else_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_controls_kb = InlineKeyboardMarkup()
admin_controls_kb.add(InlineKeyboardButton('Добавление администратора', callback_data='add_admin'))
admin_controls_kb.add(InlineKeyboardButton('Удаление администратора', callback_data='delete_admin'))
admin_controls_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

add_admin_choice_kb = InlineKeyboardMarkup()
add_admin_choice_kb.add(InlineKeyboardButton('Добавить по никнейму', callback_data='add_from_username'))
add_admin_choice_kb.add(InlineKeyboardButton('Добавить по номеру телефона', callback_data='add_from_phone'))
add_admin_choice_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_spam_kb = InlineKeyboardMarkup()
admin_spam_kb.add(InlineKeyboardButton('Рассылка в Телеграмм', callback_data='spam_to_tg'))
admin_spam_kb.add(InlineKeyboardButton('Рассылка по электронной почте', callback_data='spam_to_email'))
admin_spam_kb.add(InlineKeyboardButton('Рассылка по всем каналам', callback_data='spam_to_everything'))
admin_spam_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_spam_confirm_kb = InlineKeyboardMarkup()
admin_spam_confirm_kb.add(InlineKeyboardButton('Отправить', callback_data='confirm_spam_tg'))
admin_spam_confirm_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_email_spam_confirm_kb = InlineKeyboardMarkup()
admin_email_spam_confirm_kb.add(InlineKeyboardButton('Отправить', callback_data='confirm_spam_email'))
admin_email_spam_confirm_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

admin_all_spam_confirm_kb = InlineKeyboardMarkup()
admin_all_spam_confirm_kb.add(InlineKeyboardButton('Отправить', callback_data='confirm_spam_all'))
admin_all_spam_confirm_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

enter_again_admin_username_kb = InlineKeyboardMarkup()
enter_again_admin_username_kb.add(InlineKeyboardButton('Повторить поиск по никнейму', callback_data='add_from_username'))
enter_again_admin_username_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))

enter_again_admin_phone_kb = InlineKeyboardMarkup()
enter_again_admin_phone_kb.add(InlineKeyboardButton('Повторить поиск по номеру телефона', callback_data='add_from_phone'))
enter_again_admin_phone_kb.add(InlineKeyboardButton('Назад к меню администратора', callback_data='back_to_admin_menu'))