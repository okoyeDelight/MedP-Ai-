import urllib.parse
raw_phone = "0801 234 5678"
raw_phone = raw_phone.replace('+', '').replace(' ', '')
wa_phone = "234" + raw_phone[1:] if raw_phone.startswith('0') else raw_phone
msg_text = "Hello, I am interested in your item on Desprix Med AI."
print(f"https://api.whatsapp.com/send?phone={wa_phone}&text={urllib.parse.quote(msg_text)}")
