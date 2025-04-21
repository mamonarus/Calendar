import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta

LOGIN = "124228"
PASSWORD = "Boeing019"
BASE_URL = "https://edu.rossiya-airlines.com"

def login():
    session = requests.Session()
    login_page = session.get(f"{BASE_URL}/workplan/")
    soup = BeautifulSoup(login_page.text, "html.parser")
    token = soup.find("input", {"name": "_token"})
    token_value = token["value"] if token else ""

    r = session.post(f"{BASE_URL}/login", data={
        "username": LOGIN,
        "password": PASSWORD,
        "_token": token_value
    })

    if "logout" not in r.text:
        raise Exception("❌ Не удалось авторизоваться")
    print("✅ Успешный вход")
    return session

def fetch_month(session, date):
    url = f"{BASE_URL}/workplan/?date={date.strftime('%d.%m.%Y')}"
    r = session.get(url)
    return BeautifulSoup(r.text, "html.parser")

def parse_schedule(soup):
    events = []
    rows = soup.select("table tbody tr")

    for row in rows:
        if row.find("s"):
            # Зачёркнутая строка (неподтверждённое изменение)
            continue

        columns = row.find_all("td")
        if len(columns) < 2:
            continue

        type_cell = columns[0].get_text(strip=True)
        date_cell = columns[1].get_text(strip=True)

        try:
            if "UTC" in date_cell:
                start = datetime.strptime(date_cell, "%d.%m.%Y %H:%M UTC")
            else:
                start = datetime.strptime(date_cell, "%d.%m.%Y")
        except Exception as e:
            print(f"⚠️ Не удалось разобрать дату: {date_cell}")
            continue

        event = Event()
        event.name = type_cell
        event.begin = start
        event.duration = timedelta(hours=8)
        event.description = row.get_text(" ", strip=True)
        events.append(event)
        print(f"➕ Добавлено событие: {event.name} — {start}")

    return events

def main():
    session = login()

    today = datetime.today()
    months = [today.replace(day=1)]
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    months.append(next_month)

    all_events = []
    for month in months:
        print(f"\n📅 Парсинг месяца: {month.strftime('%B %Y')}")
        soup = fetch_month(session, month)
        events = parse_schedule(soup)
        all_events.extend(events)

    calendar = Calendar(events=all_events)
    with open("calendar.ics", "w", encoding="utf-8") as f:
        f.writelines(calendar)

    print("\n✅ Файл calendar.ics успешно создан!")

if __name__ == "__main__":
    main()
