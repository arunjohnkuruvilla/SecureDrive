import os
import json
import binascii

from hashlib import md5
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

BASE_SIZE = 32

COMMANDS = [
	("help","Shows this help banner"),													# yet to implement
	("ls", "List files in the current working directory"),								# Partially implemented
	("pwd", "NOT IMPLEMENTED - Prints the present working directory"),					# Partially implemented
	("upload <filename>", "Uploads a file to drive"),									# Partially implemented
	("download <filename>", "Downloads the file"),										# To be implemented
	("cd <directory>", "NOT IMPLEMENTED - Open directory specified."),					# Not implemented
	("delete <filename>", "Open directory specified."),									# Implemented
	("clear","Clears the screen"),														# Implemented
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

def encrypt_file(input_filename, output_filename, filesize, key, iv):
	cipher = AES.new(key, AES.MODE_CBC, iv)
	in_file = open(input_filename, 'r')
	hash_file = open(input_filename, 'rb')
	out_file = open(output_filename, 'w')
	finished = False

	h = SHA256.new()

	# Adding size of file to output
	chunk = str(filesize)
	padding_length = BASE_SIZE - (len(chunk) % BASE_SIZE)
	chunk += padding_length * chr(padding_length)
	out_file.write(cipher.encrypt(chunk))

	while True:
		data = hash_file.read(BASE_SIZE)
		if not data:
			break
		h.update(data)

	file_hash = h.digest()

	out_file.write(cipher.encrypt(file_hash))

	in_file.seek(0, 0)
	finished = False
	# Encrypting rest of the file
	while not finished:
		chunk = in_file.read(1024 * BASE_SIZE)
		if len(chunk) == 0 or len(chunk) % BASE_SIZE != 0:
			padding_length = BASE_SIZE - (len(chunk) % BASE_SIZE)
			chunk += padding_length * chr(padding_length)
			finished = True
		out_file.write(cipher.encrypt(chunk))

	return file_hash

def decrypt_file(input_filename, output_filename, key, iv):
	# added salt_header=''
	# changed 'Salted__' to salt_header
	in_file = open(input_filename, 'r')
	out_file = open(output_filename, 'w')

	cipher = AES.new(key, AES.MODE_CBC, iv)

	chunk = cipher.decrypt(in_file.read(BASE_SIZE))
	padding_length = ord(chunk[-1])  # removed ord(...) as unnecessary
	chunk = chunk[:-padding_length]
	# for x in chunk:
	#	out_file.write(bytes(x))

	hash_chunk = cipher.decrypt(in_file.read(BASE_SIZE))

	h = SHA256.new()

	next_chunk = ''
	finished = False
	while not finished:
		chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(BASE_SIZE))
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1])  # removed ord(...) as unnecessary
			chunk = chunk[:-padding_length]
			finished = True
		h.update(chunk)
		for x in chunk:
			out_file.write(bytes(x))  # changed chunk to bytes(...)

	if h.digest() == hash_chunk:
		return True, hash_chunk
	else:
		os.remove(output_filename)
		return False, 0

def flatten_filesystem(filesystem):
	flat_filesystem = ''
	for file in filesystem:
		flat_filesystem += str(file[0]) + "," + str(file[1]) + "," + str(file[2]) + "," + str(file[3]) + "," + str(file[4]) + "," + str(file[5]) + "\n"
	return flat_filesystem

def main():
	DEBUG = False
	FILESYSTEM_STATUS = False

	


	# Checking for Private Key
	if os.path.exists("./private.key"):
		with open('private.key') as data_file:    
			data = json.load(data_file)
		
		salt = data["SALT"]
		key = data["KEY"]
		iv = data["IV"]

	
	else:
		print "private.key missing. Aborting."
		# Implement case when private key is missing
		# Generate Keys if a new user
		return


	if DEBUG:
		if os.path.exists("test_enc.txt"):
			os.remove("test_enc.txt")
		if os.path.exists("test_dec.txt"):
			os.remove("test_dec.txt")
		filesize = os.path.getsize("test.txt")
		file_hash = encrypt_file("test.txt", "test_enc.txt", filesize, key, iv)
		decrypt_file("test_enc.txt", "test_dec.txt", key, iv)
		return

	# Initialization
	try:
		gauth = GoogleAuth()
		gauth.LocalWebserverAuth()
		drive = GoogleDrive(gauth)
	except:
		print "No internet connection found. Exiting"
		return

	#current_location = "root"
	#current_location_name = "root"
	#path_history = []

	#current_directory_files = []
	#current_directory_directories = []

	# Filesystem Syncronization
	filesystem_hash = binascii.hexlify(md5(iv).digest()) + ".txt"
	file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	
	########################################################################################
	# DELETE FOR PRODUCTION
	########################################################################################
	# if file_list:
	#	for item in file_list:
	#		drive.CreateFile({'id': item['id']}).Trash()
	# os.remove(filesystem_hash)
	########################################################################################

	
	for item in file_list:
		if item['title'] == filesystem_hash:

			filesystem_name = filesystem_hash
			filesystem_id = item['id']
			drive.CreateFile({'id': item['id']}).GetContentFile(filesystem_hash)
			decrypt_file(filesystem_hash, "filesystem.txt", key, iv)
			# Add logic to check validity of the file system here
			#
			#
			#
			#
			
			FILESYSTEM_STATUS = True

	current_directory_files = []

	if FILESYSTEM_STATUS:
		for line in open("filesystem.txt"):
			current_directory_files.append(line.split(","))

	if os.path.exists(filesystem_hash):
		os.remove(filesystem_hash)
	if os.path.exists("filesystem.txt"):
		os.remove("filesystem.txt")

	# Shell
	while(True):
		command = raw_input("secureDrive$ ")
		command = command.split(" ", 1)
		if command[0] == "ls" :
			if current_directory_files:
				for item in current_directory_files:
					print '|--', item[1]
			else:
				print "No files found."
		elif command[0] == "pwd":
			print "Present Working Directory - Not implemented"

		elif command[0] == "download":
			if len(command) == 2:
				filename = command[1]
				found_file_local = False
				found_file_global = False
				for item in current_directory_files:
					if item[1] == filename:
						# requested_file = (ID, title, mimeType, filename_hash, file_hash, file_size)
						requested_file = (item[0], item[1], item[2], item[3], item[4], item[5])
						found_file_local = True
				temp_file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
				if temp_file_list:
					for item in temp_file_list:
						if item['title'] == requested_file[3]:
							found_file_global = True
				if found_file_local and found_file_global:
					if requested_file[2] != "application/vnd.google-apps.folder":
						try:
							drive.CreateFile({'id': requested_file[0]}).GetContentFile(requested_file[3])
						except:
							print "File cannot be downloaded. Possibly a Google Doc or Slides file."
						else:
							status, requested_file_hash = decrypt_file(requested_file[3], 'dec_'+requested_file[1], key, iv)
							os.remove(requested_file[3])
							if status and requested_file_hash == requested_file[4]:
								print "File downloaded and saved to ./" + 'dec_'+requested_file[1]
							else:
								print "Corrupted file present."
					else:
						print "Requested resource is a directory"
				else:
					print "File with filename does not exist"
		elif command[0] == "delete":
			if len(command) == 2:
				filename = command[1]
				found_file = False
				for count, item in enumerate(current_directory_files):
					if item[1] == filename:
						requested_file = (item[0], item[1], item[2], item[3], item[4], item[5])
						found_file = True
						file_location = count
						print file_location
				if found_file:
					if requested_file[2] != "application/vnd.google-apps.folder":
						try:
							file1 = drive.CreateFile({'id': requested_file[0]})
							file1.Trash()
							
						except:
							print "File cannot be deleted. Possibly a Google Doc or Slides file."
						else:
							print "File deleted : " + requested_file[1]

							del current_directory_files[file_location]
							if current_directory_files:
								print current_directory_files
								flat_filesystem = flatten_filesystem(current_directory_files)
								open("temp_filesystem.txt", "w").write(flat_filesystem)
								encrypt_file("temp_filesystem.txt", filesystem_hash, file_size, key, iv)
								os.remove("temp_filesystem.txt")
								# encrypt_file(filesystem_hash, filesystem_hash, )
								# Checking if filesystem file uploaded for the first time
								if FILESYSTEM_STATUS:
									filesystem_file = drive.CreateFile({'id': filesystem_id}).Trash()
								filesystem_file = drive.CreateFile({'title': filesystem_hash})
								filesystem_file.SetContentFile(filesystem_hash)
								filesystem_file.Upload()
								filesystem_name = filesystem_hash
								filesystem_id = filesystem_file['id']
							else:
								if FILESYSTEM_STATUS:
									filesystem_file = drive.CreateFile({'id': filesystem_id}).Trash()
					else:
						print "Requested resource is a directory. Cannot be deleted"
				else:
					print "File with filename does not exist"

		elif command[0] == "cd":
			print "Change Directory - Not implemented"

		elif command[0] == "upload":
			filename = command[1]
			filename_hash = binascii.hexlify(md5(filename).digest()) + ".txt"
			if command[1] in os.listdir("."):
				print "Preparing file to upload."

				file_size = os.path.getsize(filename)
				file_hash = encrypt_file(filename, filename_hash, file_size, key, iv)

				try:
					file = drive.CreateFile({'title': filename_hash})
					file.SetContentFile(filename_hash)
					file.Upload()
				except Exception as e:
					print "File upload failed. Please try again."
					pass
				else:
					# Updating the filesystem file on Drive
					current_directory_files.append((file['id'], filename, file['mimeType'], filename_hash, file_hash, file_size))
					flat_filesystem = flatten_filesystem(current_directory_files)
					open("temp_filesystem.txt", "w").write(flat_filesystem)
					encrypt_file("temp_filesystem.txt", filesystem_hash, file_size, key, iv)
					os.remove("temp_filesystem.txt")
					# encrypt_file(filesystem_hash, filesystem_hash, )
					# Checking if filesystem file uploaded for the first time
					if FILESYSTEM_STATUS:
						filesystem_file = drive.CreateFile({'id': filesystem_id}).Trash()
					
					FILESYSTEM_STATUS = True
					filesystem_file = drive.CreateFile({'title': filesystem_hash})
					filesystem_file.SetContentFile(filesystem_hash)
					filesystem_file.Upload()
					filesystem_name = filesystem_hash
					filesystem_id = filesystem_file['id']

					os.remove(filename_hash)
					print'File uploaded successfully.'

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
