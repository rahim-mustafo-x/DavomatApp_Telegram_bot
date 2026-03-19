from aiogram import types, F, Router
from config import ADMIN_ID
from service import get_user_list

router = Router()


@router.message(F.text == "Foydalanuvchilar 👥")
async def get_users(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer('⛔ Bu funksiya faqat adminlar uchun.')
        return

    users = get_user_list()
    if not users:
        await message.answer('📭 Foydalanuvchilar topilmadi yoki server bilan bog\'lanishda xatolik.')
        return

    await message.answer(f'👥 Jami foydalanuvchilar: <b>{len(users)} ta</b>', parse_mode='HTML')
    for data in users:
        result = (
            f'👤 <b>{data.firstName} {data.lastName}</b>\n'
            f'📱 Telefon: <code>{data.phoneNumber}</code>\n'
            f'🆔 Telegram ID: <code>{data.telegramUserId}</code>'
        )
        await message.answer(result, parse_mode='HTML')
