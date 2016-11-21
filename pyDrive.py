import os
import json

from hashlib import md5
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from Crypto.Cipher import AES
from Crypto import Random

COMMANDS = [
	("help","Shows this help banner"),													# yet to implement
	("ls", "NOT IMPLEMENTED - List files in the current working directory"),			# Partially implemented
	("pwd", "NOT IMPLEMENTED - Prints the present working directory"),					# Partially implemented
	("upload <filename>", "Uploads a file to drive"),									# Partially implemented
	("download <filename>", "Downloads the file"),										# To be implemented
	("download <filename>", "Downloads the file"),										# Partially implemented
	("cd <directory>", "NOT IMPLEMENTED - Open directory specified."),					# Partially implemented
	("clear","Clears the screen")
	("logout", "Log out from current session."),										# To be implemented
	("exit", "Exit the application without logging out."),								# Implemented
]

def print_valid_commands():
	print ""
	print "Valid Commands:"
	for (key, value) in COMMANDS:
		print key + " : " + value
	print ""

def derive_key_and_iv(password, salt, key_length, iv_length):
	d = d_i = ''
	while len(d) < key_length + iv_length:
		d_i = md5(d_i + password + salt).digest()
		d += d_i
	return d[:key_length], d[key_length:key_length+iv_length]

def encrypt_file(in_file, out_file, bs, key, iv):
	cipher = AES.new(key, AES.MODE_CBC, iv)
	finished = False
	while not finished:
		chunk = in_file.read(1024 * bs)
		if len(chunk) == 0 or len(chunk) % bs != 0:
			padding_length = bs - (len(chunk) % bs)
			chunk += padding_length * chr(padding_length)
			finished = True
		out_file.write(cipher.encrypt(chunk))

def decrypt_file(in_file, out_file, bs, key, iv):
	# added salt_header=''
	# changed 'Salted__' to salt_header
	cipher = AES.new(key, AES.MODE_CBC, iv)
	next_chunk = ''
	finished = False
	while not finished:
		chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1])  # removed ord(...) as unnecessary
			chunk = chunk[:-padding_length]
			finished = True 
		for x in chunk:
			out_file.write(bytes(x))  # changed chunk to bytes(...)

def flatten_filesystem(filesystem):
	flat_filesystem = ''
	for file in filesystem:
		flat_filesystem += str(file[0]) + "," + str(file[1]) + "," + str(file[2]) + "\n"
	return flat_filesystem

def main():
	gauth = GoogleAuth()
	gauth.LocalWebserverAuth()

	drive = GoogleDrive(gauth)

	#current_location = "root"
	#current_location_name = "root"
	#path_history = []

	#current_directory_files = []
	#current_directory_directories = []

	file_list = drive.ListFile({'q': "'root' in parents"}).GetList()

	if os.path.exists("./filesystem"):
		os.remove("./filesystem")
	filesystem_status = False

	for item in file_list:
		if item['title'] == "filelist":

			# Add logic to check validity of the file system here
			#
			#
			#
			#
			filesystem_name = item['title']
			filesystem_id = item['id']
			drive.CreateFile({'id': item['id']}).GetContentFile(item['title'])
			filesystem_status = True
	
	if filesystem_status:
		print "File system found."
	else:
		current_directory_files = []
		print "File system not found. Initializing filesystem."


	'''
	for item in file_list:
		if item['mimeType'] != "application/vnd.google-apps.folder":
			current_directory_files.append((item['id'], item['title'], item['mimeType']))
		else:
			current_directory_directories.append((item['id'], item['title'], item['mimeType']))
	'''
	if os.path.exists("./private.key"):
		with open('private.key') as data_file:    
			data = json.load(data_file)
			
		bs = 32
		salt = data["SALT"]
		key = data["KEY"]
		iv = data["IV"]

	
	else:
		print "private.key missing."
		return

	while(True):
		command = raw_input("command$>")
		command = command.split(" ", 1)
		if command[0] == "ls" :
			'''
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
			'''
			print "List files function - Not implemented"
		elif command[0] == "pwd":
			'''
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
			'''
			print "Present Working Directory - Not implemented"

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
							with open("test_enc.txt", 'rb') as in_file, open("test_dec.txt", 'wb') as out_file:
								print decrypt_file(in_file, out_file, bs, key, iv)
							print "File downloaded and saved to ./" + "test_dec.txt"
					else:
						print "Requested resource is a directory"
				else:
					print "File with filename does not exist"
		elif command[0] == "delete":
			if len(command) == 2:
				filename = command[1]
				found_file = False
				for id, title, mimeType in current_directory_files:
					if title == filename:
						requested_file = (id, title, mimeType)
						found_file = True
				if found_file:
					if requested_file[2] != "application/vnd.google-apps.folder":
						
						try:
							file1 = drive.CreateFile({'id': requested_file[0]})
							file1.Trash()
						except:
							print "File cannot be deleted. Possibly a Google Doc or Slides file."
						else:
							print "File deleted : " + requested_file[1]
					else:
						print "Requested resource is a directory. Cannot be deleted"
				else:
					print "File with filename does not exist"

		elif command[0] == "cd":
			'''
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
			'''
			print "Change Directory - Not implemented"
		elif command[0] == "upload":
			filename = command[1]
			if command[1] in os.listdir("."):
				print "Preparing file to upload."
				# Create GoogleDriveFile instance with title 'Hello.txt'.

				with open(filename, 'rb') as in_file, open("test_enc.txt", 'wb') as out_file:
					print encrypt_file(in_file, out_file, bs, key, iv)

				'''
				'''
				try:
					file = drive.CreateFile({'title': 'test_enc.txt'})
					file.SetContentFile("test_enc.txt")
					file.Upload()
				except e:
					print "File upload failed. Please try again."
					pass
				else:

					current_directory_files.append((file['id'], file['title'], file['mimeType']))
					if filesystem_status:
						print "Updating filesystem in Drive"
					else:
						flat_filesystem = flatten_filesystem(current_directory_files)
						open("filesystem","w").write(flat_filesystem)
						file = drive.CreateFile({'title': 'filesystem'})
						file.SetContentFile("filesystem")
						file.Upload()

					os.remove("./test_enc.txt")
					print current_directory_files
					print'File uploaded. Title: %s, ID: %s' % (file['title'], file['id'])
				# title: Hello.txt, id: {{FILE_ID}}

			else:
				print "File does not exist in current directory"

		elif command[0] == 'logout':
			if len(command) == 1:
				if os.path.exists("./credentials.json"):
					os.remove("credentials.json")
				print "Logged out. Exiting."
				return

		elif command[0] == "exit":
			print "Exiting without logging out."
			return
		elif command[0] == 'clear':
			for i in xrange(20):
				print "\n"
		elif command[0] == "help":
			print_valid_commands()
		else:
			print "Invalid command."
			print_valid_commands()
	
if __name__ == '__main__':
	main()
