from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)

clearButton = ReplyKeyboardRemove()

get_number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Telefon raqamni berish 📱', request_contact=True)]
], one_time_keyboard=True, resize_keyboard=True)

user_option = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="To'lov qilish 💳"), KeyboardButton(text="Parolni o'zgartirish 🔐")],
    [KeyboardButton(text="Admin bilan bo'g'lanish 👤")]
], one_time_keyboard=True, resize_keyboard=True)

stop_conversation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Chatni to'xtatish ❌")]
], one_time_keyboard=True, resize_keyboard=True)

admin_option = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Foydalanuvchilar 👥'), KeyboardButton(text="Parolni o'zgartirish 🔐")],
    [KeyboardButton(text='Kanallar 📢')]
], one_time_keyboard=True, resize_keyboard=True)

admin_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Tasdiqlash', callback_data='approved'),
     InlineKeyboardButton(text='❌ Rad etish', callback_data='disapproved')]
])

admin_choice_for_conversation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Boshlash', callback_data='start'),
     InlineKeyboardButton(text='❌ Bekor qilish', callback_data='cancel')]
])

channel_manage = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="➖ Kanal o'chirish")],
    [KeyboardButton(text="📋 Kanallar ro'yxati"), KeyboardButton(text='🔙 Orqaga')]
], one_time_keyboard=True, resize_keyboard=True)
