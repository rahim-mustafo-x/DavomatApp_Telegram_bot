from datetime import date
from typing import List
import requests
from dateutil.relativedelta import relativedelta
from config import BASE_URL, MONTHLY_PAYMENT
from model.user import User
from model.backend_models import (
    ApiResponse, Balance, TelegramUser, TelegramUserRequest,
    PageResponseTelegramUser
)


def pay_to_user(user_id: int, amount: int):
    try:
        resp = requests.get(
            f'{BASE_URL}/api/telegram/balance',
            params={'telegramUserId': user_id},
            timeout=10
        )
        resp.raise_for_status()
        api_resp = ApiResponse[Balance](**resp.json())
    except Exception as e:
        print(f'[pay_to_user] Balance xatolik: {e}')
        return None

    today = date.today()
    base = api_resp.data.limit if (api_resp.data and api_resp.data.limit and api_resp.data.limit >= today) else today

    total_months = amount / MONTHLY_PAYMENT
    years, rem = divmod(total_months, 12)
    months = int(rem)
    days = int((rem - months) * 30)
    new_limit = base + relativedelta(years=int(years), months=months, days=days)

    body = Balance(limit=new_limit, telegramUserId=user_id).model_dump()
    body['limit'] = body['limit'].isoformat() if body['limit'] else None

    try:
        response = requests.put(f'{BASE_URL}/api/telegram/pay', json=body, timeout=10)
        print(f'[pay_to_user] status={response.status_code}, body={response.text}')
        return response
    except Exception as e:
        print(f'[pay_to_user] Xatolik: {e}')
        return None


def register_to_telegram(user: User):
    try:
        req = TelegramUserRequest(
            telegramUserId=user.user_id,
            firstName=user.first_name,
            lastName=user.last_name,
            phoneNumber=user.phone_number.strip().lstrip('+')
        )
        response = requests.post(
            f'{BASE_URL}/api/telegram/register',
            data=req.model_dump_json(),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        result = ApiResponse[TelegramUser](**response.json())
        print(result)
        return result
    except Exception as e:
        print(f'[register_to_telegram] Xatolik: {e}')
        return None


def update_password(phone_number: str, password: str):
    try:
        phone_number = phone_number.strip().lstrip('+')
        print(f'[update_password] phoneNumber={phone_number!r}')
        response = requests.put(
            f'{BASE_URL}/api/telegram/update/user',
            params={'phoneNumber': phone_number, 'password': password},
            timeout=10
        )
        print(f'[update_password] status={response.status_code}, body={response.text}')
        if response.status_code != 200:
            return None
        api_response = ApiResponse(**response.json())
        if api_response.code == 500 and api_response.data is None:
            return 'not_found'
        return True if api_response.code == 200 else None
    except Exception as e:
        print(f'[update_password] Xatolik: {e}')
        return None


def get_user_list() -> List[TelegramUser]:
    try:
        response = requests.get(
            f'{BASE_URL}/api/telegram/get_all_users',
            params={'page': 0, 'size': 100},
            timeout=10
        )
        if response.status_code != 200:
            return []
        api_response = ApiResponse[PageResponseTelegramUser](**response.json())
        if api_response.code == 200 and api_response.data and api_response.data.content:
            return api_response.data.content
        return []
    except Exception as e:
        print(f'[get_user_list] Xatolik: {e}')
        return []
