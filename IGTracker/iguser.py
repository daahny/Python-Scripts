# iguser.py



import instaloader
import os
import datetime



class IGUser:



    def __init__(self, target_user: str, context: instaloader.instaloadercontext):
        self.insta = instaloader.Instaloader()
        self.context = context

        self.target_profile = target_user
        self.followers = self.target_profile
        self.following = self.target_profile
        self.followers_file = self.target_profile
        self.last_ran = self.followers_file



    @property
    def target_profile(self) -> instaloader.Profile:
            '''Return user's instaloader profile object'''
            return self._target_profile
    
    @target_profile.setter
    def target_profile(self, username):
        '''Set user's instaloader profile object'''
        try:
            self._target_profile = instaloader.Profile.from_username(self.context, username)
        except instaloader.exceptions.ProfileNotExistsException:
            print(f'Error: could not find user \'{username}\'')
            print('Exiting script')
            exit(0)
        except instaloader.exceptions.QueryReturnedBadRequestException:
            print('Error: received HTTP/400 - Bad Request from server')
            print('Make sure your Instagram bot account is in good standing')
            print('Exiting script')
            exit(0)



    @property
    def followers(self) -> set:
        '''Return followers'''
        return self._followers
    
    @followers.setter
    def followers(self, target_profile):
        '''Set followers'''
        try:
            self._followers = {follower.username for follower in target_profile.get_followers()}
        except instaloader.ConnectionException:
            print('Error - Received HTTP/401 Unauthorized. Exiting script.')
            exit(-1)
        if len(self._followers) == 0:
            raise instaloader.PrivateProfileNotFollowedException
        


    @property
    def following(self) -> set:
        '''Return following'''
        return self._following
    
    @following.setter
    def following(self, target_profile):
        '''Set following'''

        self._following = {following for following in target_profile.get_followees()}
        if len(self._following) == 0:
            raise instaloader.PrivateProfileNotFollowedException
        


    @property
    def followers_file(self) -> str:
        '''Return followers file path
        '''
        return self._followers_file
    
    @followers_file.setter
    def followers_file(self, target_profile):
        '''Set followers file with current followers'''

        username = target_profile.username
        current_dir = os.path.dirname(__file__)
        if not os.path.exists(f'{current_dir}/Users/{username}'):
            print(f'{current_dir}/Users/{username}/ does not exist.')
            print('Create this directory and create an args.json file.')
            print('Exiting script.')
            exit(-1)
        self._followers_file = f'{current_dir}/Users/{username}/{username}_followers.txt'
    


    @property
    def last_ran(self) -> str:
        '''Return user's last run time'''
        return self._last_ran

    @last_ran.setter
    def last_ran(self, file):
        '''Set user's last run time'''

        if os.path.isfile(file):
            time = os.path.getmtime(file)
            self._last_ran = datetime.datetime.fromtimestamp(time).strftime('%a %B %d')



    def is_first_time(self):
        '''Check if user's followers file is populated'''

        if not os.path.isfile(self.followers_file):
            return True
        return False
    


    def update_followers_file(self, followers):
        '''Update user's followers file '''

        with open(self.followers_file, 'w') as file:
            for count, follower in enumerate(followers):
                if count == len(followers) - 1:
                    file.write(follower)
                else:
                    file.write(follower +'\n')