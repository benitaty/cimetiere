import smtplib
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

# Récupérer les identifiants depuis .env
email = os.getenv('EMAIL_HOST_USER')
password = os.getenv('EMAIL_HOST_PASSWORD')
smtp_server = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
port = int(os.getenv('EMAIL_PORT', 587))

try:
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp_server, port)
    server.starttls(context=context)
    server.login(email, password)
    print("✅ Connexion SMTP réussie !")
    server.quit()
except Exception as e:
    print(f"❌ Erreur SMTP : {e}")