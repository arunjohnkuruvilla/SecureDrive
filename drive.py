import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

COMMANDS = [
    ("list", "List files in the current working directory"),
    ("upload <filename>", "Uploads a file to drive"),
    ("download <filename>", "Downloads the file"),
    ("open <directory>", "Open directory specified."),
    ("exit", "Exit the application.")
]

def print_valid_commands():
    print "Valid Commands:"
    for (key, value) in COMMANDS:
        print key + " : " + value


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    current_location = "root"
    previous_location = "root"

    current_directory = []
    while(True):
        command = raw_input("command$>")
        command = command.split(" ")
        if command[0] == "list" :
            results = service.files().list( q = "'"+ current_location + "' in parents and trashed=false", orderBy="folder", fields="nextPageToken, files(id, name, kind, mimeType)").execute()
            items = results.get('files', [])
            if not items:
                print'No files found.'
            else:
                for item in items:
                    if item['mimeType'] == "application/vnd.google-apps.folder":
                        print "|----", item['name']
                    else: 
                        print '|-', item['name']
                    current_directory.append((item['id'], item['name'], item['mimeType']))
            continue
        if command[0] == "open":
            if len(command) == 2:
                new_path = command[1]
                found_path = False

                for id, name, mimeType in current_directory:
                    if name == new_path:
                        new_path_id = id
                        found_path = True
                if found_path:
                    results = service.files().list( q = "'"+ new_path_id + "' in parents and trashed=false", orderBy="folder", fields="nextPageToken, files(id, name, kind, mimeType)").execute()
                    items = results.get('files', [])
                    if not items:
                        print'No files found.'
                    else:
                        previous_location = current_location
                        current_location = new_path

                        for item in items:
                            if item['mimeType'] == "application/vnd.google-apps.folder":
                                print "|----", item['name']
                            else: 
                                print '|-', item['name']
                    continue   
        if command[0] == "upload":
            print command[1]
            continue

        if command[0] == "download":
            print command[1]
            continue

        if command[0] == "exit":
            return

        print "Invalid command."
        print_valid_commands()

if __name__ == '__main__':
    main()