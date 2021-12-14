#!/usr/bin/env python3

from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError
from subprocess import Popen, PIPE
from sys import exit
from time import sleep

# Global Variables
MAX_TRIES = 3

def clear_clipboard():
    p = Popen(['xsel', '-bc'])

    p.communicate()

def copy_to_clipboard(input):
    p = Popen(['xsel', '-bi'], stdin=PIPE)

    p.communicate(input=bytes(input, 'utf-8'))

def rofi_show_entries(elements):

    # rofi -no-config -no-lazy-grab -sep "|" -dmenu -i -theme interface.rasi
    p = Popen([
        'rofi',
        '-no-config',
        '-no-lazy-grab',
        '-sep',
        '|',
        '-dmenu',
        '-i',
        '-format',
        'i',
        '-theme',
        'interface.rasi'
    ], stdin=PIPE, stdout=PIPE)

    output, error = p.communicate(input=bytes('|'.join(elements), 'utf-8'))

    if error:
        print("[-] Hubo un error")

    return output.decode('utf-8').rstrip("\n")

def rofi_password_input():
    p = Popen([
        'rofi',
        '-dmenu',
        '-password',
        '-theme',
        'password.rasi'
    ], stdout=PIPE)

    output, error = p.communicate()

    return output.decode('utf-8').rstrip("\n")


def main():
    kp = None
    attempts = 3

    while kp is None:
        try:
            # kp = PyKeePass('prueba.kdbx', password='password123')
            password = rofi_password_input()

            if not password:
               exit(1)

            kp = PyKeePass('prueba.kdbx', password=password)
        except CredentialsError:
            print("[-] Password incorrect.")
            attempts -= 1

            if attempts <= 0:
                exit(1)


    # Root group
    parents_group_stack = []
    current_group = kp.root_group

    while True:
        is_there_parents = len(parents_group_stack) > 0

        # Text elements in one list
        text_elements = [' ..'] if is_there_parents else []
        text_elements += [' ' + group.name for group in current_group.subgroups]
        text_elements += [' ' + entry.title + '/' + entry.username for entry in current_group.entries]

        index = rofi_show_entries(text_elements)

        if not index:
            break

        index = int(index)
        offset = 1 if is_there_parents else 0

        if index == 0 and is_there_parents:
            current_group = parents_group_stack.pop()
        elif index <= len(current_group.subgroups):
            parents_group_stack.append(current_group)
            current_group = current_group.subgroups[index - offset]
        else:
            copy_to_clipboard(current_group.entries[index - offset - len(current_group.subgroups)].password)
            print("[+] Password was copied to clipboard.")
            sleep(10)
            clear_clipboard()
            print("[+] Clipboard cleared.")
            break

if __name__ == '__main__':
    main()
