# 발송 대상: 피플팀 아지트 (Incoming Webhook)
# URL 은 GitHub Secret AGIT_WEBHOOK_URL 에 있다. 대상 그룹을 바꾸려면
# 아지트에서 웹훅을 새로 발급받아 그 Secret 값만 교체하면 된다.

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

KST = timezone(timedelta(hours=9))
WEBHOOK_URL = os.environ["AGIT_WEBHOOK_URL"]


def get_week_range():
    """이번 주 월~금 (KST 기준)"""
    today = datetime.now(KST)
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday


def build_payload():
    monday, friday = get_week_range()
    month = monday.month
    week_num = (monday.day - 1) // 7 + 1
    title = (
        f"{month}월 {week_num}주차 HR Weekly Report "
        f"({monday:%Y.%m.%d} ~ {friday:%Y.%m.%d})"
    )
    return {
        "text": title,
        "schedule": {
            "title": title,
            "is_allday": True,
            "color": "blue",
            "starts_at": int(monday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()),
            "ends_at": int(friday.replace(hour=23, minute=59, second=59, microsecond=0).timestamp()),
        },
    }


def main():
    payload = build_payload()
    print(f"발송 시도: {payload['text']}")

    try:
        response = requests.post(
            WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=15,
        )
    except requests.RequestException as e:
        sys.exit(f"발송 실패: 요청 자체가 안 됨 / {e}")

    # requests 는 4xx/5xx 에도 예외를 던지지 않는다. 직접 확인해야 한다.
    if response.status_code >= 400:
        sys.exit(f"발송 실패: HTTP {response.status_code} / {response.text[:300]}")

    try:
        body = response.json()
    except ValueError:
        sys.exit(f"발송 실패: 응답이 JSON 이 아님 / {response.text[:300]}")

    # 아지트는 성공 시 {"status": "ok", "id": <글 ID>} 를 준다.
    if body.get("status") != "ok" or not body.get("id"):
        sys.exit(f"발송 실패: 아지트 응답 이상 / {body}")

    print(f"발송 완료: post id={body['id']}")


if __name__ == "__main__":
    main()
