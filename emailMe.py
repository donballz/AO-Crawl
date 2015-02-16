# Import smtplib for the actual sending function
import smtplib
from email.mime.text import MIMEText as text


def email_me(run=1):
	if run == 1:
		msg = {}

		# me == the sender's email address
		# you == the recipient's email address
		msg = text('Now get back to work!')

		msg['Subject'] = 'Code completed'
		msg['From'] = 'darms28@yahoo.com'
		msg['To'] = 'donald.armstead@gmail.com'
		msg['Password'] = 'curtis3078'

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		s = smtplib.SMTP('smtp.mail.yahoo.com')
		s.login(msg['From'], msg['Password'])
		s.sendmail(msg['From'], msg['To'], msg.as_string())
		s.quit()
	return None
