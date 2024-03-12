import os
import json


running_dir = os.path.dirname(__file__)
os.chdir(running_dir)


with open('templates/args.json') as j:
    user_args = json.load(j)


target_user = input(f'{"Enter username to monitor: ":<30} ')
smtp_to = input(f'{"Enter users email for alerts: ":<30} ')
    

user_args['target_user'] = target_user
user_args['smtp_to'] = smtp_to


path = f'{running_dir}/Users/{target_user}'
if os.path.exists(path):
    print(f'User {target_user} already has data in {path}')
    exit(0)
else:
    os.mkdir(path)
    print(f'Created user directory in {path}')


with open(f'{path}/{target_user}_args.json', 'w') as args_file:
    args_file.write(json.dumps(user_args, indent=4, sort_keys=True))