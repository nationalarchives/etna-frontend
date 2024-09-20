import json
from datetime import datetime
from urllib.parse import unquote

from flask import request


def now_iso_8601():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def cookie_preference(policy):
    if "cookies_policy" in request.cookies:
        cookies_policy = request.cookies["cookies_policy"]
        preferences = json.loads(unquote(cookies_policy))
        return preferences[policy] if policy in preferences else None
    return None


def get_date_from_string(s):
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y")
    except ValueError:
        pass
    return None


def get_year_from_date_string(s):
    date = get_date_from_string(s)
    if date:
        return date.strftime("%Y")
    return None


def get_month_year_from_date_string(s):
    date = get_date_from_string(s)
    if date:
        return date.strftime("%B %Y")
    return None


def pretty_date_range(s_from, s_to, include_time=False):
    date_from = get_date_from_string(s_from)
    date_to = get_date_from_string(s_to)
    if date_from and date_to:
        date_to_string = date_to.strftime("%d %B %Y")
        if (
            date_from.day == 1
            and date_from.month == 1
            and (
                (date_to.day == 31 and date_to.month == 12)
                or (date_to.day == 1 and date_to.month == 1)
            )
        ):
            if date_from.year == date_to.year:
                return date_from.year
            return f"{date_from.year}–{date_to.year}"
        if date_from.year == date_to.year:
            if date_from.month == date_to.month:
                if date_from.day == date_to.day:
                    if (
                        date_from.hour != date_to.hour
                        or date_from.minute != date_to.minute
                        or date_from.second != date_to.second
                    ):
                        return f"{date_to_string}, {date_from.strftime('%H:%M')}–{date_to.strftime('%H:%M')}"
                    return date_to_string
                else:
                    return f"{date_from.strftime('%d')}–{date_to_string}"
            else:
                return f"{date_from.strftime('%d %B')} to {date_to_string}"
        else:
            return f"{date_from.strftime('%d %B %Y')} to {date_to_string}"
    if date_from:
        if include_time:
            return f"{date_from.strftime('%d %B %Y, %H:%M')}"
        return f"From {date_from.strftime('%d %B %Y')}"
    if date_to:
        if include_time:
            return f"{date_from.strftime('%d %B %Y, %H:%M')}"
        return f"To {date_to.strftime('%d %B %Y')}"
    return f"{s_from}–{s_to}"
