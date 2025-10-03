import secrets
import string

# 1. 英数字と記号を含む長い文字列を生成（例: 32文字）
# string.ascii_letters: A-Z, a-z
# string.digits: 0-9
# string.punctuation: 記号
key_chars = string.ascii_letters + string.digits + string.punctuation
KEY = ''.join(secrets.choice(key_chars) for i in range(32))

print(KEY)
