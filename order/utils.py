import re

def format_phone_number(phone: str) -> str:
    phone = phone.replace("+", "")
    if re.match(r"^254\d{9}$", phone):
        return phone
    if phone.startswith("0") and len(phone) == 10:
        return "254" + phone[1:]
    raise ValueError("Invalid phone number format")
