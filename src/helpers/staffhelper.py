import logging
from typing import Optional

import httpx

from configs.settings import CommonSettings

CONFIG = CommonSettings()
PASSPORT_URL = "https://passport.skbkontur.ru"
STAFF_URL = "https://staff.skbkontur.ru"


async def get_staff_token() -> Optional[str]:
    """Получает в паспорте токен для запросов в АПИ Стаффа"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PASSPORT_URL}/connect/token",
            data={
                "grant_type": "client_credentials",
                "scope": "profiles",
            },
            auth=httpx.BasicAuth(CONFIG.STAFF_CLIENT_ID, CONFIG.STAFF_CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        logging.error(f"Ошибка при запросе токена: {response.status_code}")
        return None


async def search_emails(query: str) -> Optional[list[str]]:
    """Ищет по всей инфе о сотруднике в Стаффе и возвращает почты действующих сотрудников"""
    token = await get_staff_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{STAFF_URL}/api/Suggest/bytype",
            params={"Q": query, "Types": 7},
            headers={"Authorization": f"Bearer {token}"},
        )
    if response.status_code == 200:
        data = response.json()["items"]
        if len(data) == 0:
            return []
        else:
            return [item["email"] for item in data if item["status"] != "dismissed"]
    else:
        logging.error(f"Ошибка при поиске пользователей: {response.status_code}")
        return None
