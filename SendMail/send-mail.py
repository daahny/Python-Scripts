import smtplib
import json
import os

# source_addr
# dest_addr
# smtp_server
# smtp_port
# message
args = {}
args_path = 'smtp-args.json'

def read_args(file):
    '''Get email args'''
    global args
    if os.open(file, os.F_OK, os.R_OK) and file.endswith('json'):
        with open(file, 'r') as file:
            args = json.load(file)
    else:
        print('Error: file could not be opened or file is not a JSON file.')
        exit(-1)
    

def send_mail():
    '''Send mail'''
    source = args.get("SOURCE_ADDR")
    dest = args.get("DEST_ADDR")
    server = args.get("SMTP_SERVER")
    port = args.get("SMTP_PORT")
    message = args.get("MESSAGE")
    smtp = smtplib.SMTP(host=server, port=port)
    smtp.sendmail(from_addr=source, to_addrs=dest, msg=message)


def main():
    read_args(args_path)
    send_mail()


main()