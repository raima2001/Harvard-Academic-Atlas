import base64
import os

valid_salt = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
print(f"Generated Salt: {valid_salt}")
