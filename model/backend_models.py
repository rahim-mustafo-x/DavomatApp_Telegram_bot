from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict
from datetime import date

T = TypeVar('T')


# GET /api/telegram/balance → ResponseBalance { code, data: Balance, message }
# PUT /api/telegram/pay    → ResponseBoolean  { code, data: bool,    message }
# POST /api/telegram/register → ResponseTelegramUser { code, data: TelegramUser, message }
# PUT /api/telegram/update/user → ResponseUser { code, data: User, message }
# GET /api/telegram/get_all_users → ResponsePageResponseTelegramUser { code, data: PageResponseTelegramUser, message }

class ApiResponse(BaseModel, Generic[T]):
    """Generic wrapper — ba'zi endpointlar code/data/message ishlatadi"""
    code: int
    data: Optional[T] = None
    message: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)


# --- Swagger: Balance schema ---
class Balance(BaseModel):
    limit: Optional[date] = None
    telegramUserId: Optional[int] = None


# --- Swagger: TelegramUser schema (register uchun request va response) ---
class TelegramUser(BaseModel):
    id: Optional[int] = None
    userId: Optional[int] = None
    telegramUserId: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None


# --- Swagger: TelegramUser register request (faqat kerakli fieldlar) ---
class TelegramUserRequest(BaseModel):
    telegramUserId: int
    firstName: str
    lastName: str
    phoneNumber: str


# --- Swagger: User schema (update/user response ichida) ---
class User(BaseModel):
    id: Optional[int] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    role: Optional[str] = None
    payedDate: Optional[date] = None


# --- Swagger: PageResponseTelegramUser ---
class PageResponseTelegramUser(BaseModel):
    content: Optional[List[TelegramUser]] = None
    pageNumber: Optional[int] = None
    pageSize: Optional[int] = None
    totalElements: Optional[int] = None
    totalPages: Optional[int] = None
    last: Optional[bool] = None
    first: Optional[bool] = None


# Eski nomlar — backward compat uchun
TelegramUserResponse = TelegramUser
BalanceResponse = Balance
