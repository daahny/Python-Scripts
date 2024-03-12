# igmail.py



import smtplib
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class IGMail:



    def __init__(self, smtp_from, smtp_to, smtp_server, smtp_port, smtp_username, smtp_password):
        self.smtp_from = smtp_from
        self.smtp_to = smtp_to
        self.smtp_server= smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password



    EMOJIS = [
        '&#129314',
        '&#129326',
        '&#129393',
        '&#129299',
        '&#128128',
        '&#128169',
        '&#129531',
        '&#127844',
        '&#128078',
        '&#128514'
    ]



    def build_email(self, lost_followers: set, new_followers: set, one_way_set: set, last_ran: str) -> MIMEMultipart:
        '''Build and return MIME compliant message'''


        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Instagram Followers Update'
        msg['From'] = self.smtp_from
        msg['To'] = self.smtp_to
        text = 'Users not following you back:\n'


        losers = ''
        for lost in lost_followers:
            losers += f'<li>{random.choice(self.EMOJIS)}{lost}{random.choice(self.EMOJIS)}</li>\n'
            text += lost


        cool_people = ''
        for new in new_followers:
            cool_people += f'<li>&#128526{new}&#128526</li>\n'


        one_way = ''
        for one in one_way_set:
            one_way += f'<li>{random.choice(self.EMOJIS)}{one}{random.choice(self.EMOJIS)}</li>\n'


        with open(r'templates/email.html', 'r') as email:
            html = email.read().format(losers=losers, cool_people=cool_people, one_way=one_way, last_ran=last_ran)


        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))


        return msg



    def send(self, msg: MIMEMultipart):
        '''Send followers update email'''


        smtp_connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_connection.ehlo()
        smtp_connection.starttls()
        smtp_connection.ehlo()


        smtp_connection.login(self.smtp_username, self.smtp_password) 
        smtp_connection.sendmail(self.smtp_from, self.smtp_to, msg.as_string())

        print(f'Sent email to {self.smtp_to}')