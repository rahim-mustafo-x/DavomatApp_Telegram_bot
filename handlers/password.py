from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from model.passwordstate import PasswordState
from service import update_password
from config import ADMIN_ID
from keyboards import user_option, admin_option, get_number

router = Router()


@router.message(F.text == "Parolni o'zgartirish 🔐")
async def ask_phone(message: types.Message, state: FSMContext):
    await message.answer('Telefon raqamingizni yuboring 📱', reply_markup=get_number)
    await state.set_state(PasswordState.wait)


@router.message(PasswordState.wait, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number.strip().lstrip('+')
    await state.update_data(phone=phone)
    await message.answer('Yangi parolni kiriting:')
    await state.set_state(PasswordState.password)


@router.message(PasswordState.password)
async def set_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data.get('phone')
    result = update_password(phone, message.text)
    markup = admin_option if message.from_user.id in ADMIN_ID else user_option

    if result == 'not_found':
        await message.answer(
            '❌ Bu telefon raqam tizimda topilmadi.\n'
            'Iltimos, avval ilovada ro\'yxatdan o\'ting.',
            reply_markup=markup
        )
    elif result:
        await message.answer('✅ Parol muvaffaqiyatli o\'zgartirildi.', reply_markup=markup)
    else:
        await message.answer('⚠️ Xatolik yuz berdi. Qayta urinib ko\'ring.', reply_markup=markup)

    await state.clear()
