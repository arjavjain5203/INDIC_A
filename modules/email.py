# modules/email.py

import smtplib
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from tts import speak

def send_email(subject, body, to_email):
    try:
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            speak("Email credentials are missing.")
            return

        message = f"Subject: {subject}\n\n{body}"
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, message)
        server.quit()
        speak("Email sent successfully.")

    except Exception as e:
        speak("I couldn't send the email.")
        print(e)
