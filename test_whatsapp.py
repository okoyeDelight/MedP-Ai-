raw_phone = ""
raw_phone = raw_phone.replace('+', '').replace(' ', '')
wa_phone = "234" + raw_phone[1:] if raw_phone.startswith('0') else raw_phone
print(f"Empty: {wa_phone}")
