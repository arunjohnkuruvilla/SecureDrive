from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

COMMANDS = [
	("help","Shows this help banner"),								# yet to implement
    ("ls", "List files in the current working directory"),			# Partially implemented
    ("pwd", "Prints the present working directory"),				# Partially implemented
    ("upload <filename>", "Uploads a file to drive"),				# Partially implemented
    ("download <filename>", "Downloads the file"),					# To be implemented
    ("cd <directory>", "Open directory specified."),				# Partially implemented
    ("logout", "Log out from current session."),					# To be implemented
    ("exit", "Exit the application without logging out.")			# Implemented
]

def print_valid_commands():
	print ""
	print "Valid Commands:"
	for (key, value) in COMMANDS:
		print key + " : " + value
	print ""


def main():
	gauth = GoogleAuth()
	gauth.LocalWebserverAuth()

	drive = GoogleDrive(gauth)

	current_location = "root"
	current_location_name = "root"
	path_history = []

	current_directory_files = []
	current_directory_directories = []

	file_list = drive.ListFile({'q': "'root' in parents"}).GetList()

	for item in file_list:
		if item['mimeType'] != "application/vnd.google-apps.folder":
			current_directory_files.append((item['id'], item['title'], item['mimeType']))
		else:
			current_directory_directories.append((item['id'], item['title'], item['mimeType']))

	while(True):
		command = raw_input("command$>")
		command = command.split(" ", 1)
		if command[0] == "ls" :
			if len(command) == 1:
				file_list = drive.ListFile({'q': "'"+ current_location +"' in parents and trashed=false", "orderBy": "folder"}).GetList()
				if not file_list:
					print'No files found.'
				else:
					current_directory_files = []
					current_directory_directories = []
					for item in file_list:
						if item['mimeType'] == "application/vnd.google-apps.folder":
							current_directory_directories.append((item['id'], item['title'], item['mimeType']))
							print "|----", item['title']
						else: 
							current_directory_files.append((item['id'], item['title'], item['mimeType']))
							print '|-', item['title']
		elif command[0] == "pwd":
			if len(path_history) == 0:
				print "/"
			else:
				path = ""
				for x in xrange(len(path_history)):
					if path_history[-x-1][1] == "root":
						path += "/"
					else:
						path = path + path_history[-x-1][1] + "/"
				print path + current_location_name

		elif command[0] == "download":
			if len(command) == 2:
				filename = command[1]
				found_file = False
				for id, title, mimeType in current_directory_files:
					if title == filename:
						requested_file = (id, title, mimeType)
						found_file = True
				if found_file:
					if requested_file[2] != "application/vnd.google-apps.folder":
						#file = service.files().get(fileId=requested_file[0], acknowledgeAbuse=None).execute()
						try:
							drive.CreateFile({'id': requested_file[0]}).GetContentFile(requested_file[1])
						except:
							print "File cannot be downloaded. Possibly a Google Doc or Slides file."
						else:
							print "File downloaded and saved to ./" + requested_file[1]
					else:
						print "Requested resource is a directory"
				else:
					print "File with filename does not exist"
		
		elif command[0] == "cd":
			if len(command) == 2:
				new_path = command[1]

				found_path = False

				if new_path == "..":
					if len(path_history) != 0:
						current_location = path_history.pop(0)[0]
						current_location_name = path_history.pop(0)[1]
					else:
						current_location = "root"
						current_location_name = "root"
					found_path = True
				else:
					for id, name, mimeType in current_directory_directories:
						if name == new_path:
							new_path_id = id
							if current_location == "root":
								current_location_name = "root"
							path_history.insert(0, (current_location, current_location_name))
							current_location = new_path_id
							current_location_name = name
							found_path = True
				if found_path:
					file_list = drive.ListFile({'q': "'"+ current_location +"' in parents and trashed=false", "orderBy": "folder"}).GetList()
					if not file_list:
						print'No files found.'
					else:
						current_directory_files = []
						current_directory_directories = []
						for item in file_list:
							if item['mimeType'] == "application/vnd.google-apps.folder":
								current_directory_directories.append((item['id'], item['title'], item['mimeType']))
								print "|----", item['title']
							else: 
								current_directory_files.append((item['id'], item['title'], item['mimeType']))
								print '|-', item['title']
				else:
					print "Invalid path provided"

		elif command[0] == "upload":
			filename = command[1]
			if command[1] in os.listdir("."):
				print "Preparing file to upload."
				# Create GoogleDriveFile instance with title 'Hello.txt'.
				file = drive.CreateFile()
				file.SetContentFile(filename)
				file.Upload()
				print('File uploaded. Title: %s, ID: %s' % (file['title'], file['id']))
				# title: Hello.txt, id: {{FILE_ID}}

			else:
				print "Filename provided does not exist in current directory"

		elif command[0] == 'logout':
			if len(command) == 1:
				if os.path.exists("./credentials.json"):
					os.remove("credentials.json")
				print "Logged out. Exiting."
				return

		elif command[0] == "exit":
			print "Exiting without logging out."
			return
		elif command[0] == "help":
			print_valid_commands()
		else:
			print "Invalid command."
			print_valid_commands()
	
if __name__ == '__main__':
	main()
