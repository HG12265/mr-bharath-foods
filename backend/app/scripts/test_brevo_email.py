"""
Quick test: Send a real test email via Brevo to verify the API key and sender work.

Run from the backend directory:
    py -3 app/scripts/test_brevo_email.py
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")
SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Bharath Delight Foods")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", SENDER_EMAIL)

if not BREVO_API_KEY:
    print("ERROR: BREVO_API_KEY not found in .env")
    sys.exit(1)

if not SENDER_EMAIL:
    print("ERROR: BREVO_SENDER_EMAIL not found in .env")
    sys.exit(1)

print("Testing Brevo email...")
print(f"  API Key  : {BREVO_API_KEY[:20]}...")
print(f"  From     : {SENDER_NAME} <{SENDER_EMAIL}>")
print(f"  To       : {ADMIN_EMAIL}")

payload = {
    "sender": {"name": SENDER_NAME, "email": SENDER_EMAIL},
    "to": [{"email": ADMIN_EMAIL, "name": "Admin"}],
    "subject": "Bharath Delight Foods - Brevo Email Test",
    "htmlContent": """
        <div style="font-family: Arial, sans-serif; padding: 30px; background: #FAF9F6;">
            <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; border: 1px solid rgba(200,155,60,0.2);">
                <div style="background: #0F3D2E; padding: 24px; text-align: center;">
                    <h1 style="color: #FAF9F6; margin: 0; font-size: 20px; letter-spacing: 1.5px;">BHARATH DELIGHT FOODS</h1>
                    <p style="color: #C89B3C; margin: 5px 0 0; font-size: 10px; letter-spacing: 3px; text-transform: uppercase;">Email Test</p>
                </div>
                <div style="padding: 30px;">
                    <h2 style="color: #0F3D2E;">Brevo Email Working!</h2>
                    <p>This is a test email to confirm that Brevo transactional email is configured correctly for <b>Bharath Delight Foods</b>.</p>
                    <p style="color: #666; font-size: 13px;">Sender: """ + SENDER_EMAIL + """<br>API Key verified successfully.</p>
                </div>
                <div style="background: #FAF9F6; padding: 15px; text-align: center; font-size: 11px; color: #999;">
                    &copy; 2025 Bharath Delight Foods. All rights reserved.
                </div>
            </div>
        </div>
    """
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "https://api.brevo.com/v3/smtp/email",
    data=data,
    headers={
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print("\nSUCCESS! Email sent successfully.")
        print(f"  Message ID : {result.get('messageId', 'N/A')}")
        print(f"\nCheck inbox: {ADMIN_EMAIL}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8")
    print(f"\nFAILED! HTTP {e.code}: {body}")
except Exception as e:
    print(f"\nERROR: {e}")
