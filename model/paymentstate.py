from aiogram.fsm.state import State, StatesGroup


class PaymentState(StatesGroup):
    wait = State()
    wait_for_validate = State()
    wait_for_amount = State()
