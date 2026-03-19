from aiogram import (Router, types, F, Bot)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from config import (CARD_NUMBER, ADMIN_ID, MONTHLY_PAYMENT)
from model import PaymentState
from service import pay_to_user
from keyboards import (admin_choice, user_option)

router = Router()


@router.message(F.text == "To'lov qilish 💳")
async def pay_balance(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_ID:
        await message.answer(text='Siz adminsiz, to\'lov funksiyasi sizga tegishli emas.')
        return
    await state.set_state(PaymentState.wait)
    await message.answer(
        text=(
            f'💳 <b>To\'lov ma\'lumotlari:</b>\n\n'
            f'Oylik to\'lov: <b>{MONTHLY_PAYMENT:,} so\'m</b>\n'
            f'Karta raqami:\n<code>{CARD_NUMBER}</code>\n\n'
            f'To\'lovni amalga oshirgach, <b>chek rasmini</b> shu yerga yuboring 👇\n'
            f'<i>Eslatma: Chek rasmisiz to\'lov tasdiqlanmaydi.</i>'
        ),
        parse_mode='HTML'
    )


@router.message(PaymentState.wait, F.photo)
async def wait_for_image(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # user_id ni state'ga saqlaymiz
    await state.update_data(payer_id=user_id)

    for admin_id in ADMIN_ID:
        await message.send_copy(chat_id=admin_id)
        await message.bot.send_message(
            chat_id=admin_id,
            text=(
                f'👤 Foydalanuvchi: <b>{user_name}</b>\n'
                f'🆔 ID: <code>{user_id}</code>\n\n'
                f'Chekni tasdiqlaysizmi?'
            ),
            parse_mode='HTML',
            reply_markup=admin_choice
        )

    await message.answer('✅ Chekingiz adminga yuborildi. Admin tasdiqlashini kuting...')
    await state.set_state(PaymentState.wait_for_validate)


@router.callback_query(F.data == 'approved')
async def approved(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Tasdiqlash bosildi ✅')

    # Admin state'idan payer_id ni olamiz — lekin bu admin state'i
    # Shuning uchun xabardan user_id ni parse qilamiz
    text = callback.message.text or ''
    payer_id = None
    for line in text.split('\n'):
        if 'ID:' in line:
            try:
                payer_id = int(line.split('`')[1] if '`' in line else line.split(':')[1].strip())
            except Exception:
                pass

    if payer_id is None:
        await callback.message.answer('⚠️ Foydalanuvchi ID topilmadi. Qayta urinib ko\'ring.')
        return

    await state.update_data(payer_id=payer_id)
    await callback.message.answer(
        f'✅ Tasdiqlandi. Endi foydalanuvchiga o\'tkazilgan summani kiriting (so\'mda):\n'
        f'<i>Masalan: 40000</i>',
        parse_mode='HTML'
    )
    await state.set_state(PaymentState.wait_for_amount)


@router.callback_query(F.data == 'disapproved')
async def disapproved(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Rad etildi ❌')

    text = callback.message.text or ''
    payer_id = None
    for line in text.split('\n'):
        if 'ID:' in line:
            try:
                payer_id = int(line.split('`')[1] if '`' in line else line.split(':')[1].strip())
            except Exception:
                pass

    await callback.message.answer('❌ To\'lov rad etildi.')
    if payer_id:
        await callback.bot.send_message(
            chat_id=payer_id,
            text='❌ To\'lovingiz rad etildi.\nIltimos, admin bilan bog\'laning 👤',
            reply_markup=user_option
        )
    await state.clear()


@router.message(PaymentState.wait_for_amount)
async def wait_for_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payer_id = data.get('payer_id')

    if not payer_id:
        await message.answer('⚠️ Foydalanuvchi ID topilmadi.')
        await state.clear()
        return

    try:
        amount = int(message.text.replace(' ', '').replace(',', ''))
        if amount <= 0:
            await message.answer('⚠️ Summa 0 dan katta bo\'lishi kerak.')
            return
    except ValueError:
        await message.answer('⚠️ Iltimos, faqat raqam kiriting. Masalan: <code>40000</code>', parse_mode='HTML')
        return

    months = amount / MONTHLY_PAYMENT
    response = pay_to_user(payer_id, amount)

    if response and response.ok:
        await message.bot.send_message(
            chat_id=payer_id,
            text=(
                f'✅ To\'lovingiz tasdiqlandi!\n\n'
                f'💰 Summa: <b>{amount:,} so\'m</b>\n'
                f'📅 Muddat: <b>{months:.1f} oy</b> qo\'shildi'
            ),
            parse_mode='HTML',
            reply_markup=user_option
        )
        await message.answer(f'✅ Muvaffaqiyatli! {payer_id} ga {amount:,} so\'m o\'tkazildi.')
    else:
        await message.bot.send_message(
            chat_id=payer_id,
            text='⚠️ To\'lovni qayta ishlashda xatolik yuz berdi. Admin bilan bog\'laning.',
            reply_markup=user_option
        )
        await message.answer('⚠️ Serverda xatolik yuz berdi.')

    await state.clear()
