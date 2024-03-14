# igtracker.py



import instaloader
import os
import json
from igmail import IGMail
from iguser import IGUser
from argparse import ArgumentParser



running_dir = os.path.dirname(__file__)



def banner():
    '''Print banner & script description'''

    print('''
===========================================================================
|██╗ ██████╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ |
|██║██╔════╝     ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗|
|██║██║  ███╗       ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝|
|██║██║   ██║       ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗|
|██║╚██████╔╝       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║|
|╚═╝ ╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝|
===========================================================================
          
Track new followers, lost followers, and one-way followers\n''')



def parse_users() -> list:
    '''Parse users to run this script against'''

    parser = ArgumentParser(description='IG Tracker -- Report on lost/new followers, and track one-way followers.')
    parser.add_argument('-u', '--users', dest='users', nargs='*', help='User or comma-separated list of users. Specified user must have existing data in users/. Use tools/adduser.py to add user data.')
    args = parser.parse_args()
    global users
    return args.users



def parse_user_data(username: str) -> str:
    '''Parse user data like the recipient email address'''

    if not os.path.exists(f'{running_dir}/users/{username}'):
        return
    with open(f'{running_dir}/users/{username}/{username}_args.json') as args:
        return json.load(args)['smtp_to']



def parse_bot_data(username: str) -> tuple[instaloader.instaloadercontext, IGMail]:
    '''Parse bot data like credentials and SMTP arguments'''
    
    print('Parsing bot SMTP and IG arguments')

    with open(f'{running_dir}/users/bot/smtp.json', 'r') as smtp:
        args = json.load(smtp)
        smtp_from = args['smtp_from']
        smtp_to = parse_user_data(username)
        smtp_server = args['smtp_server']
        smtp_port = args['smtp_port']
        smtp_username = args['smtp_username']
        smtp_password = args['smtp_password']

    mail = set_insta_mail(smtp_from, smtp_to, smtp_server, smtp_port, smtp_username, smtp_password)


    with open(f'{running_dir}/users/bot/ig.json') as ig:
        args = json.load(ig)
        insta_user = args['insta_user']
        insta_password = args['insta_password']
    
    context = log_into_instagram(insta_user, insta_password)

    return (context, mail)



def log_into_instagram(user: str, password: str) -> instaloader.instaloadercontext:
    '''Log into instagram and return instaloader context'''
    

    print(f'Logging into instagram with bot account')
    try:
        insta = instaloader.Instaloader(max_connection_attempts=1)
        insta.login(user, password)
    except instaloader.QueryReturnedBadRequestException:
        print('Error - Received bad request attempt notification')
        print('Check your bot account\'s standing in instagram.')
        print('Exiting script')
        exit(0)
    return insta.context

    # Loading a session seems to return http/401 when working with more than 1 IG user
    # Need to find a workaround
    # try:
    #     insta.load_session_from_file(user)
    # except FileNotFoundError:
    #     insta.save_session_to_file()



def set_insta_mail(smtp_from: str, smtp_to: str, smtp_server: str, smtp_port: str, smtp_username: str, smtp_password: str):
    '''Instantiate IGMail object'''

    return IGMail(
            smtp_from=smtp_from,
            smtp_to=smtp_to,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password
        )
    


def set_ig_user(username: str, context: instaloader.instaloadercontext) -> IGUser:
    '''Instantiate IGUser object. Raises PrivateProfileNotFollowedException if account is not followed by bot.'''

    print('Retrieving IG user data.')
    try:
        return IGUser(
                target_user=username,
                context=context
            )
    except instaloader.PrivateProfileNotFollowedException:
        print('Error: Target user is a private account and is not followed by bot account.')
        print('Exiting script.')
        exit(-1)



def check_first_time(user: IGUser, username: str):
    '''Check if followers list exists for passed-in user.'''

    if user.is_first_time():
        user.update_followers_file(followers=user.followers)
        print(f'First time running script for user {username}')
        print(f'Populated {user}\'s followers file.')
        print('Run again in the future to check for new/lost followers.')
        print('Continuing to other users, if any.')
        return True



def print_follows(lost_followers, new_followers, one_way, last_ran, username):
    '''Print any updates to follows.'''

    print(f'\n--- Updates since {last_ran} for {username} ---')

    print('\n--- New Followers ---')
    for new in new_followers:
        print(f'\t- {new}')

    print('\n--- Lost Followers ---')
    for lost in lost_followers:
        print(f'\t- {lost}')

    print(f'\n--- Unverified Followers not Following you Back ---')
    for one in one_way:
        print(f'\t- {one}')



def iterate_users(users: list):
    '''Iterate through users and compare follows'''

    for username in users:

        print(f'Running igtracker for {username}')
        
        # Get IG context and mail object
        context, mail = parse_bot_data(username)


        # Get IGUser object
        user = set_ig_user(username, context)


        # Check if user's followers list exists
        print('Checking if user\'s followers file has followers')
        if check_first_time(user, username):
            continue


        # Open followers file with old list of followers
        with open(user.followers_file, 'r') as file:
            old_followers = {f.rstrip() for f in file.readlines()}


        # Compare followers to following
        lost_followers = set()
        new_followers = set()
        one_way = set()


        print('Comparing followers to old followers')
        for follower in user.followers:
            if follower not in old_followers:
                new_followers.add(follower)
        for old_follower in old_followers:
            if old_follower not in user.followers:
                lost_followers.add(old_follower)
        for following in user.following:
            if following.username not in user.followers and not following.is_verified:
                one_way.add(following.username)


        print('Updating user\'s followers file with new followers')
        # Update followers file with actual followers
        user.update_followers_file(old_followers.union(new_followers))

        # Print to console any updates to followers
        print_follows(lost_followers, new_followers, one_way, user.last_ran, username)

        # Build compliant email message and send it
        msg = mail.build_email(lost_followers, new_followers, one_way, user.last_ran)
        mail.send(msg)

        

def main():
    '''Main function'''
    
    os.chdir(running_dir)
    banner()
    users = parse_users()
    iterate_users(users)



main()