import os
import hashlib
from collections import defaultdict

hashmap = defaultdict(list)


def get_dir():
    '''Get directory path from user'''
    while True:
        dir = input('Enter absolute directory path: ')
        if os.path.isdir(dir):
            return dir
        else:
            print('Error - Directory path is not valid')


def hash(file, subdir=''):
    '''Update hashmap for passed-in file'''
    # recursive case
    path = os.path.abspath(file)
    if os.path.isdir(path):
        directory = file
        current_dir = os.getcwd()
        os.chdir(directory)
        for f in os.listdir('.'):
            hash(f, f'{subdir + directory}/')
        os.chdir(current_dir)
    # base case
    else:
        hash_obj = hashlib.sha256()
        with open(file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        file_hash = hash_obj.hexdigest()
        hashmap[file_hash].append(f'{subdir}{file}')


def print_duplicates():
    '''Print duplicate files'''
    for hash in hashmap.keys():
        if len(hashmap[hash]) > 1:
            print(f'Identical files: {hashmap[hash]}')


def main():
    '''Main'''
    dir = get_dir()
    os.chdir(dir)

    for file in os.listdir(dir):
        hash(file)

    print_duplicates()


main()