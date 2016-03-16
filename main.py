#!/usr/bin/python

import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re
import sys

OUT_FILE = "emails.txt"
MAX_FETCH = 0
EMAIL_FOLDER = "INBOX"

regex = re.compile('(.*)\s+<([^>]*)>.*')

def process_mailbox(M):
    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print("No messages found!")
        return

    contacts = {}

    i = 0

    for num in data[0].split():
        i += 1
        
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print("ERROR getting message", num)
            return

        msg = email.message_from_string(data[0][1])
        mailer = str(email.header.decode_header(msg['From'])[0][0])
        
        match = regex.match(mailer)

        sys.stdout.write("\r" + " " * 60)
        sys.stdout.flush()
        sys.stdout.write("\rFound contacts: [all: {0}; uniq: {1}]".format(i, len(contacts)))

        if match:
            found = match.group(2)
            if found not in contacts:
                contacts.update({ found: match.group(1) })
                sys.stdout.write(" found: {0}".format(found))

        sys.stdout.flush()

        if MAX_FETCH > 0 and i >= MAX_FETCH:
            break

    print("\nWriting file \"{0}\" ...".format(OUT_FILE))
    with open(OUT_FILE, 'w') as f:
        for e, n in contacts.iteritems():
            f.write(e+"\r\n")

M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    username = raw_input("Enter account name: ")
    rv, data = M.login(username, getpass.getpass())
except imaplib.IMAP4.error:
    print("LOGIN FAILED!!! ")
    sys.exit(1)

print(rv, data)

MAX_FETCH = int(raw_input("Maximum fetch emails (ALL): ") or '0')

rv, data = M.select(EMAIL_FOLDER)
if rv == 'OK':
    print("Processing mailbox:")
    process_mailbox(M)
    M.close()
else:
    print("ERROR: Unable to open mailbox ", rv)

M.logout()