from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from model import (User, StartState)
from config import ADMIN_ID
from keyboards import get_number, clearButton, user_option, admin_option
from service import register_to_telegram
from db import get_all_channels

router = Router()


async def check_subscriptions(bot: Bot, user_id: int):
    """Foydalanuvchi barcha kanallarga a'zo bo'lganini tekshiradi.
    Bot admin bo'lmagan kanallar o'tkazib yuboriladi."""
    channels = get_all_channels()
    not_joined = []
    for ch in channels:
        try:
            # channel_id ni normalize qilamiz
            channel_id = ch['channel_id']
            if channel_id.startswith('https://t.me/'):
                channel_id = '@' + channel_id.replace('https://t.me/', '').rstrip('/')

            bot_member = await bot.get_chat_member(channel_id, (await bot.get_me()).id)
            if bot_member.status not in ('administrator', 'creator'):
                continue
            member = await bot.get_chat_member(channel_id, user_id)
            if member.status in ('left', 'kicked', 'banned'):
                not_joined.append(ch)
        except Exception as e:
            print(f'[check_subscriptions] {ch["channel_id"]}: {e}')
    return not_joined


def build_channel_keyboard(channels: list) -> InlineKeyboardMarkup:
    """A'zo bo'lmagan kanallar uchun inline keyboard."""
    buttons = [
        [InlineKeyboardButton(text=f"📢 {ch['channel_name']}", url=ch['invite_link'])]
        for ch in channels
    ]
    buttons.append([InlineKeyboardButton(text="✅ A'zo bo'ldim", callback_data='check_subscription')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    not_joined = await check_subscriptions(bot, message.from_user.id)
    if not_joined:
        await message.answer(
            '📢 Botdan foydalanish uchun quyidagi kanallarga a\'zo bo\'ling:',
            reply_markup=build_channel_keyboard(not_joined)
        )
        return

    first_name = message.from_user.first_name or ''
    last_name = message.from_user.last_name or ''
    full_name = f'{first_name} {last_name}'.strip()
    await message.answer(f'Assalomu aleykum, {full_name} 👋', reply_markup=get_number)
    await state.set_state(StartState.wait)


@router.callback_query(F.data == 'check_subscription')
async def check_sub_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    not_joined = await check_subscriptions(bot, callback.from_user.id)
    if not_joined:
        await callback.answer("Hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=build_channel_keyboard(not_joined))
        except Exception:
            pass
        return

    await callback.answer("✅ Rahmat!")
    await callback.message.delete()

    first_name = callback.from_user.first_name or ''
    last_name = callback.from_user.last_name or ''
    full_name = f'{first_name} {last_name}'.strip()
    await callback.message.answer(f'Assalomu aleykum, {full_name} 👋', reply_markup=get_number)
    await state.set_state(StartState.wait)


@router.message(StartState.wait, F.contact)
async def contact_handler(message: types.Message, state: FSMContext):
    contact = message.contact
    user_id = contact.user_id
    user = User(
        user_id,
        contact.first_name or '',
        contact.last_name or '',
        contact.phone_number or ''
    )
    await message.answer('Qabul qilindi ✅', reply_markup=clearButton)

    if user_id in ADMIN_ID:
        await message.answer('Xush kelibsiz, admin!', reply_markup=admin_option)
    else:
        await message.answer('Xush kelibsiz!', reply_markup=user_option)

    response = register_to_telegram(user)
    try:
        if response and response.data:
            for admin_id in ADMIN_ID:
                await message.bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f'👤 Yangi foydalanuvchi ro\'yxatdan o\'tdi:\n'
                        f'Ismi: <code>{response.data.firstName}</code>\n'
                        f'Familiyasi: <code>{response.data.lastName}</code>\n'
                        f'Telefon: <code>{response.data.phoneNumber}</code>'
                    ),
                    parse_mode='HTML'
                )
    except Exception as e:
        print(f'[start] Admin xabari yuborishda xatolik: {e}')
    await state.clear()
