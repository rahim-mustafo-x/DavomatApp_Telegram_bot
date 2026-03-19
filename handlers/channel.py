from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from db import add_channel, remove_channel, get_all_channels
from keyboards import channel_manage, admin_option

router = Router()


class ChannelState(StatesGroup):
    wait_channel_id = State()
    wait_channel_name = State()
    wait_channel_link = State()
    wait_remove_id = State()


@router.message(F.text == 'Kanallar 📢')
async def channels_menu(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        return
    await message.answer('Kanal boshqaruvi:', reply_markup=channel_manage)


@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID:
        return
    await message.answer(
        'Kanal ID sini yuboring.\n'
        '<i>Masalan: @mening_kanalim yoki -1001234567890</i>',
        parse_mode='HTML'
    )
    await state.set_state(ChannelState.wait_channel_id)


@router.message(ChannelState.wait_channel_id)
async def get_channel_id(message: types.Message, state: FSMContext):
    await state.update_data(channel_id=message.text.strip())
    await message.answer('Kanal nomini kiriting:\n<i>Masalan: Rasmiy kanal</i>', parse_mode='HTML')
    await state.set_state(ChannelState.wait_channel_name)


@router.message(ChannelState.wait_channel_name)
async def get_channel_name(message: types.Message, state: FSMContext):
    await state.update_data(channel_name=message.text.strip())
    await message.answer('Kanal invite linkini kiriting:\n<i>Masalan: https://t.me/mening_kanalim</i>', parse_mode='HTML')
    await state.set_state(ChannelState.wait_channel_link)


@router.message(ChannelState.wait_channel_link)
async def get_channel_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_id = data['channel_id']
    channel_name = data['channel_name']
    invite_link = message.text.strip()

    # channel_id ni to'g'ri formatga keltiramiz
    # https://t.me/username → @username
    if channel_id.startswith('https://t.me/'):
        channel_id = '@' + channel_id.replace('https://t.me/', '').rstrip('/')

    add_channel(channel_id, channel_name, invite_link)
    await message.answer(
        f'✅ Kanal qo\'shildi:\n'
        f'📢 <b>{channel_name}</b>\n'
        f'🆔 <code>{channel_id}</code>',
        parse_mode='HTML',
        reply_markup=channel_manage
    )
    await state.clear()


@router.message(F.text == "➖ Kanal o'chirish")
async def remove_channel_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_ID:
        return
    channels = get_all_channels()
    if not channels:
        await message.answer('📭 Hech qanday kanal yo\'q.')
        return
    text = '🗑 O\'chirish uchun kanal ID sini yuboring:\n\n'
    for ch in channels:
        text += f'📢 <b>{ch["channel_name"]}</b> — <code>{ch["channel_id"]}</code>\n'
    await message.answer(text, parse_mode='HTML')
    await state.set_state(ChannelState.wait_remove_id)


@router.message(ChannelState.wait_remove_id)
async def do_remove_channel(message: types.Message, state: FSMContext):
    remove_channel(message.text.strip())
    await message.answer('✅ Kanal o\'chirildi.', reply_markup=channel_manage)
    await state.clear()


@router.message(F.text == "📋 Kanallar ro'yxati")
async def list_channels(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        return
    channels = get_all_channels()
    if not channels:
        await message.answer('📭 Hech qanday kanal yo\'q.')
        return
    text = '📋 <b>Majburiy kanallar:</b>\n\n'
    for ch in channels:
        text += f'📢 <b>{ch["channel_name"]}</b>\n🆔 <code>{ch["channel_id"]}</code>\n🔗 {ch["invite_link"]}\n\n'
    await message.answer(text, parse_mode='HTML')


@router.message(F.text == '🔙 Orqaga')
async def back_to_admin(message: types.Message):
    if message.from_user.id not in ADMIN_ID:
        return
    await message.answer('Admin panel:', reply_markup=admin_option)
