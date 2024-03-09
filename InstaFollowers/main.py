import instaloader
import os
import sys
import json
from instamail import InstaMail
from instacontext import InstaContext


running_dir = os.path.dirname(__file__)
os.chdir(running_dir)


lost_followers = set()
new_followers = set()
users = []


try:
    for user in sys.argv:
        users.append(user)
except IndexError:
    print('Error - No username specified')
    print('Please pass a username to monitor. Exiting script.')
    exit(-1)


for username in users:
    user_dir = f'{running_dir}/Users/{username}'
    if not os.path.exists(user_dir):
        print('User data does not exist.')
        print(f'Please use `adduser.py` to add {username}\'s data')
        exit(0)
    else:
        with open(f'{user_dir}/{username}_args.json', 'r') as j:
            args = json.load(j)
            insta_user = args['insta_user']
            insta_password = args['insta_password']
            target_user = args['target_user']
            smtp_from = args['smtp_from']
            smtp_to = args['smtp_to']
            smtp_server = args['smtp_server']
            smtp_port = args['smtp_port']
            smtp_username = args['smtp_username']
            smtp_password = args['smtp_password']


    try:
        insta = instaloader.Instaloader()
        insta.login(insta_user, insta_password)
        user = InstaContext(
            target_user=target_user,
            context=insta.context
            )
    except instaloader.PrivateProfileNotFollowedException:
        print('Error: Target user is a private account and is not followed by bot account.')
        print('Exiting script.')
        exit(-1)


    mail = InstaMail(
        smtp_from=smtp_from, 
        smtp_to=smtp_to, 
        smtp_server=smtp_server, 
        smtp_port=smtp_port, 
        smtp_username=smtp_username, 
        smtp_password=smtp_password
        )


    if user.is_first_time():
        user.update_followers_file(followers=user.followers)
        print(f'First time running script for user {target_user}')
        print(f'Populated {user.followers_file} with current followers.')
        print('Run again in the future to check for new/lost followers.')
        print('Exiting script.')
        exit(0)


    with open(user.followers_file, 'r') as file:
        old_followers = {f.rstrip() for f in file.readlines()}

        for follower in user.followers:
            if follower not in old_followers:
                new_followers.add(follower)
        for old_follower in old_followers:
            if old_follower not in user.followers:
                lost_followers.add(old_follower)


    user.update_followers_file(old_followers.union(new_followers))
    msg = mail.build_email(lost_followers, new_followers, user.last_ran)
    mail.send(msg)