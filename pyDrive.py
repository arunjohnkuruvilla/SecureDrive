import os
import json
import binascii
import re
import warnings

import hashlib
from hashlib import md5
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

BASE_SIZE = 32
FILE_FORMAT = ".txt"

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

def encrypt_file(input_filename, output_filename, filesize, key, iv):
	cipher = AES.new(key, AES.MODE_OFB, iv)
	in_file = open(input_filename, 'r')
	hash_file = open(input_filename, 'rb')
	out_file = open(output_filename, 'w')
	finished = False

	h = SHA256.new()

	# Adding size of file to output
	chunk = str(filesize)
	padding_length = BASE_SIZE - (len(chunk) % BASE_SIZE)
	chunk += padding_length * chr(padding_length)
	out_file.write(binascii.hexlify(cipher.encrypt(chunk)))

	while True:
		data = hash_file.read(BASE_SIZE)
		if not data:
			break
		h.update(data)

	file_encrypted_hash = binascii.hexlify(cipher.encrypt(h.digest()))
	file_hash = binascii.hexlify(h.digest())

	out_file.write(file_encrypted_hash)

	in_file.seek(0, 0)
	finished = False
	# Encrypting rest of the file
	while not finished:
		chunk = in_file.read(BASE_SIZE)
		if len(chunk) == 0 or len(chunk) % BASE_SIZE != 0:
			padding_length = BASE_SIZE - (len(chunk) % BASE_SIZE)
			chunk += padding_length * chr(padding_length)
			finished = True

		out_file.write(binascii.hexlify(cipher.encrypt(chunk)))

	out_file.close()
	in_file.close()

	return file_hash

def decrypt_file(input_filename, output_filename, key, iv):

	in_file = open(input_filename, 'r')
	out_file = open(output_filename, 'w')

	cipher = AES.new(key, AES.MODE_OFB, iv)

	chunk = cipher.decrypt(binascii.unhexlify(in_file.read(BASE_SIZE*2)))
	padding_length = ord(chunk[-1]) 
	chunk = chunk[:-padding_length]

	hash_chunk = in_file.read(BASE_SIZE*2)
	
	hash_chunk = binascii.hexlify(cipher.decrypt(binascii.unhexlify(hash_chunk)))

	h = SHA256.new()

	next_chunk = ''
	finished = False
	while not finished:
		try:
			#chunk, next_chunk = next_chunk, cipher.decrypt(binascii.unhexlify(in_file.read(BASE_SIZE*2)))
			chunk, next_chunk = next_chunk, cipher.decrypt(binascii.unhexlify(in_file.read(BASE_SIZE*2)))
		except:
			if os.path.exists(output_filename):
				os.remove(output_filename)
			return False, 0
		if len(next_chunk) == 0:
			padding_length = ord(chunk[-1]) 
			chunk = chunk[:-padding_length]
			finished = True
		h.update(chunk)
		for x in chunk:
			out_file.write(bytes(x)) 

	if binascii.hexlify(h.digest()) == hash_chunk:
		return True, hash_chunk
	else:
		if os.path.exists(output_filename):
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
	FILESYSTEM_CORRUPT = True
	
	# Checking for Private Key
	if os.path.exists("./private.key"):
		with open('private.key') as data_file:    
			data = json.load(data_file)
		
		key = data["KEY"]

		k = SHA256.new()
		k.update(key)
		key = k.digest()
		
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
	except InvalidConfigError:
		print "File client_secret.json not found. Exiting."
		return

	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		try:
			gauth.LocalWebserverAuth()
			drive = GoogleDrive(gauth)
		except Warning as e:
			pass
		except Exception as e:
			print "No internet connection found. Exiting."

	#current_location = "root"
	#current_location_name = "root"
	#path_history = []

	#current_directory_files = []
	#current_directory_directories = []

	# Filesystem Syncronization
	filesystem_hash = binascii.hexlify(md5(iv).digest()) + FILE_FORMAT
	file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	
	########################################################################################
	# DELETE FOR PRODUCTION
	########################################################################################
	# if file_list:
	#	for item in file_list:
	#		drive.CreateFile({'id': item['id']}).Trash()
	# os.remove(filesystem_hash)
	########################################################################################

	current_directory_files = []
	if file_list:
		for item in file_list:
			if item['title'] == filesystem_hash:

				filesystem_name = filesystem_hash
				filesystem_id = item['id']
				drive.CreateFile({'id': item['id']}).GetContentFile(filesystem_hash)
				status, temphash = decrypt_file(filesystem_hash, "filesystem.txt", key, iv)
				
				if status == False:
					FILESYSTEM_CORRUPT = True
				else:
					# Filesystem validation
					temp_ids = []

					for line in open("filesystem.txt"):
						if line == '\n':
							continue
						current_directory_files.append(line.split(","))
						temp_ids.append(line.split(",")[0])
					file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

					for item in file_list:
						if item['id'] == filesystem_id:
							continue
						if item['id'] in temp_ids:
							temp_ids.remove(item['id'])
					if temp_ids == []:
						FILESYSTEM_STATUS = True
						FILESYSTEM_CORRUPT = False
	else:
		FILESYSTEM_CORRUPT = False

	if FILESYSTEM_CORRUPT:
		print "Corrupt filesystem present."
		command = raw_input ("Do you want to wipe the Drive before proceeding? YES/NO: ")
		command = command.upper()
		if command == "YES":
			print "Wiping entire drive. This might take a moment."
			# Trashing all files in Drive
			file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
			for item in file_list:
				drive.CreateFile({'id': item['id']}).Trash()
			current_directory_files = []
			print "Drive wiped. Initializing filesystem."

		elif command == "NO":
			print "Initializing filesystem. Residual files may remain."
			current_directory_files = []

		else:
			print "Invalid command given. Wiping Drive."

			# Trashing all files in Drive
			file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
			for item in file_list:
				drive.CreateFile({'id': item['id']}).Trash()
			current_directory_files = []

	if os.path.exists(filesystem_hash):
		os.remove(filesystem_hash)
	if os.path.exists("filesystem.txt"):
		os.remove("filesystem.txt")

	# Shell
	while(True):
		command = raw_input("SecureDrive$ ")
		command = command.split(" ", 1)
		if command[0] == '':
			continue
		elif command[0] == "ls" :
			if current_directory_files:
				for item in current_directory_files:
					print '|--', item[1]
			else:
				print "No files found."
		elif command[0] == "pwd":
			print "Present Working Directory - Not implemented"

		# Download Function
		elif command[0] == "download":

			# Check for Argument count
			if len(command) == 2:
				filename = command[1]

				#Check for filename validity
				if re.match(r"[a-zA-Z0-9_]+\.[a-zA-Z0-9]+", filename) == None:
					print "Filename contains invalid characters. Only a-z, A-Z, 0-9 and _ allowed."
					continue

				FOUND_FILE_LOCAL = False
				FOUND_FILE_GLOBAL = False

				# Logic to check file presence
				for item in current_directory_files:
					if item[1] == filename:
						# requested_file = (ID, title, mimeType, filename_hash, file_hash, file_size)
						requested_file = (item[0], item[1], item[2], item[3], item[4], item[5])
						FOUND_FILE_LOCAL = True

				if not FOUND_FILE_LOCAL:
					print "File with filename does not exist."
					continue

				temp_file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
				if temp_file_list:
					for item in temp_file_list:
						if item['title'] == requested_file[3]:
							FOUND_FILE_GLOBAL = True

				# Download and Decrypt
				if FOUND_FILE_LOCAL and FOUND_FILE_GLOBAL:
					if requested_file[2] != "application/vnd.google-apps.folder":
						try:
							drive.CreateFile({'id': requested_file[0]}).GetContentFile(requested_file[3])
						except:
							print "File cannot be downloaded. Possibly a Google Doc or Slides file."
							continue

						else:
							status, requested_file_hash = decrypt_file(requested_file[3], 'dec_'+requested_file[1], key, iv)

							if os.path.exists(requested_file[3]):
								os.remove(requested_file[3])

							if status and requested_file_hash == requested_file[4]:
								print "File downloaded and saved to ./" + 'dec_'+requested_file[1]
							else:
								print "Corrupted file present. File has been modified outside the system."
					else:
						print "Requested resource is a directory"
				else:
					print "File with filename does not exist in the Drive. Possibly a corrupt filesystem."

		# Delete Function
		elif command[0] == "delete":
			if len(command) == 2:
				filename = command[1]
				if re.match(r"[a-zA-Z0-9_]+\.[a-zA-Z0-9]+", filename) == None:
					print "Filename contains invalid characters. Only a-z, A-Z, 0-9 and _ allowed."
					continue
				found_file = False
				for count, item in enumerate(current_directory_files):
					if item[1] == filename:
						requested_file = (item[0], item[1], item[2], item[3], item[4], item[5])
						found_file = True
						file_location = count
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
								flat_filesystem = flatten_filesystem(current_directory_files)
								open("temp_filesystem.txt", "w").write(flat_filesystem)

								encrypt_file("temp_filesystem.txt", filesystem_hash, requested_file[5], key, iv)

								if os.path.exists("temp_filesystem.txt"):
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

			
			if re.match(r"[a-zA-Z0-9_]+\.[a-zA-Z0-9]+", filename) == None:
				print "Filename contains invalid characters. Only a-z, A-Z, 0-9 and _ allowed."
				continue
			# Check if a file with a similar name is present
			filename_already_present = False
			if current_directory_files:
				for item in current_directory_files:
					if item[1] == filename:
						filename_already_present = True

			if not filename_already_present:
				filename_hash = binascii.hexlify(md5(filename).digest()) + FILE_FORMAT
				if filename in os.listdir("."):
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
						if os.path.exists(filename_hash):
							os.remove(filename_hash)

						current_directory_files.append((file['id'], filename, file['mimeType'], filename_hash, file_hash, file_size))
		
						flat_filesystem = flatten_filesystem(current_directory_files)
						open("temp_filesystem.txt", "w").write(flat_filesystem)
						encrypt_file("temp_filesystem.txt", filesystem_hash, file_size, key, iv)

						if os.path.exists("temp_filesystem.txt"):
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

						if os.path.exists(filesystem_hash):
							os.remove(filesystem_hash)
						print'File uploaded successfully.'

				else:
					print "File does not exist in current directory. Try again."
			else:
				print "Cannot upload file as a file with the same name already exists. Try renaming the file and trying again."

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
