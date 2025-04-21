import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import re

LOGIN = "124228"
PASSWORD = "Boeing019"
BASE_URL = "https://edu.rossiya-airlines.com"

session = requests.Session()
login_page = session.get(f"{BASE_URL}/workplan/")
soup = BeautifulSoup(login_page.text, "html.parser")

# Получаем токен из формы входа
token_input = soup.find("input", {"name": "_token"})
token = token_input["value"] if token_input else ""

# Отправляем форму входа
session.post(f"{BASE_URL}/login", data={
    "username": LOGIN,
    "password": PASSWORD,
    "_token": token
})

# Генерация месяцев: текущий и следующий
today = datetime.utcnow()
months = [today.replace(day=1), (today.replace(day=28) + timedelta(days=4)).replace(day=1)]

events = []
for month in months:
    url = f"{BASE_URL}/workplan/?date={month.strftime('%d.%m.%Y')}"
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table tbody tr")
    for row in rows:
        # Пропускаем зачеркнутые строки (неподтвержденные)
        if row.find("s"):
            continue

        cols = row.find_all("td")
        if len(cols) < 2:
            continue

        type_cell = cols[0].text.strip()
        datetime_str = cols[1].text.strip()
        desc = row.text.strip().replace("\n", " ")

        try:
            dt = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M UTC")
        except:
            dt = datetime.strptime(datetime_str.split()[0], "%d.%m.%Y")
            dt = datetime.combine(dt, datetime.min.time())

        event = Event()
        event.name = type_cell
        event.begin = dt
        event.duration = timedelta(hours=8)
        event.description = desc
        events.append(event)

# Сохраняем в ICS
cal = Calendar(events=events)
with open("calendar.ics", "w", encoding="utf-8") as f:
    f.writelines(cal)
