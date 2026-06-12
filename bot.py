import requests
import json
import os
from datetime import datetime, timedelta

WEBHOOK_URL = os.environ["AGIT_WEBHOOK_URL"]

def get_week_range():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday

def send_weekly_report():
    monday, friday = get_week_range()

    month = monday.month
    week_num = (monday.day - 1) // 7 + 1
    title = f"{month}월 {week_num}주차 HR Weekly Report ({monday.strftime('%Y.%m.%d')} ~ {friday.strftime('%Y.%m.%d')})"

    payload = {
        "text": title,
        "schedule": {
            "title": title,
            "is_allday": True,
            "color": "blue",
            "starts_at": int(monday.replace(hour=0, minute=0, second=0).timestamp()),
            "ends_at": int(friday.replace(hour=23, minute=59, second=59).timestamp())
        }
    }

    response = requests.post(
        WEBHOOK_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )
    print(f"전송 완료: {response.json()}")

if __name__ == "__main__":
    send_weekly_report()
