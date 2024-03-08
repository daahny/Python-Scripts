import instaloader
import smtplib
import json
import os


# Instagram creds
running_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(running_dir)
with open('insta-creds.txt', 'r') as creds:
    insta_user = creds.readline().replace('\n', '')
    insta_password = r'' + creds.readline()


# SMTP variables
with open('smtp-args.json', 'r') as args:
    smtp_args = json.load(args)
source = smtp_args['SOURCE_ADDR']
dest = smtp_args['DEST_ADDR']
server = smtp_args['SMTP_SERVER']
port = smtp_args['SMTP_PORT']
smtp_user = smtp_args['USERNAME']
smtp_password = smtp_args['PASSWORD']


# Instagram context
insta = instaloader.Instaloader()
insta.login(insta_user, insta_password)
user = input('username: ')
user_profile = instaloader.Profile.from_username(insta.context, user)


# Followers and following lists
followers = [follower.username for follower in user_profile.get_followers()]
following = [following for following in user_profile.get_followees()]


# Compare followers to following
one_way = set()
for f in following:
    if f.username not in followers and not f.is_verified:
        one_way.add(f.username)


# Build out email message
msg = f'From: {source}\r\n' \
      f'To: {dest}\r\n\r\n' \
       'The following users are not following you back:\n'''
for loser in one_way:
    msg += loser + '\n'


# Send email
smtp_connection = smtplib.SMTP(server, port)
smtp_connection.ehlo()
smtp_connection.starttls()
smtp_connection.ehlo()
smtp_connection.login(smtp_user, smtp_password) 
smtp_connection.sendmail(from_addr=source, to_addrs=dest, msg=msg)