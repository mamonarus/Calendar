import os
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta

# Получаем логин и пароль из секретов
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# URLы
LOGIN_URL = "https://edu.rossiya-airlines.com/login/index.php"
WORKPLAN_URL = "https://edu.rossiya-airlines.com/workplan/"

# Сессия для работы с куками
session = requests.Session()

# 1. Получаем токен входа
login_page = session.get(LOGIN_URL)
soup = BeautifulSoup(login_page.text, "html.parser")
logintoken = soup.find("input", {"name": "logintoken"}).get("value")

# 2. Логинимся
payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "logintoken": logintoken,
}
response = session.post(LOGIN_URL, data=payload)

if "workplan" not in response.text:
    raise Exception("Ошибка входа — проверь логин/пароль")

print("✅ Успешный вход")

# 3. Пока просто создаём тестовый календарь
cal = Calendar()

event = Event()
event.name = "Рабочая смена (тест)"
event.begin = datetime.now() + timedelta(days=1)
event.end = event.begin + timedelta(hours=10)
event.description = "Это тестовая смена"

cal.events.add(event)

# 4. Сохраняем файл
with open("calendar.ics", "w", encoding="utf-8") as f:
    f.writelines(cal.serialize_iter())

print("✅ Календарь создан: calendar.ics")
