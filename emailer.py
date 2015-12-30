import smtplib
import logging

from settings import *

def sendemail(subject, message):
    # Credentials
    from_addr = username = EMAIL_USER
    password = EMAIL_PASSWORD
    to_addr = EMAIL_RECIPIENT

    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % to_addr
    header += 'Subject: %s\n\n' % subject
    message = header + message

    # SMTP_SSL
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(from_addr, password)
    problems = server_ssl.sendmail(from_addr, to_addr, message)
    server_ssl.close()

    if problems:
        logging.debug("Error: " + str(problems))
        return False
    else:
        logging.debug("Email sent!")
        return True
