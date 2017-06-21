# SecureDrive

SecureDrive brings [Google Drive](https://www.google.com/drive/) to the command line. Allowing faster and more secure access to the cloud from the terminal. Secure drive also uses AES256 encryption, OFB and salting to encrypt all data to enforce confidentiality and it uses SSL to enforce integrity.


## Dependencies

1. [OpenSSL](https://www.openssl.org/) - Library for cryptographic functions in python.
2. [PyCrypto](https://www.dlitz.net/software/pycrypto/) - Library for cryptographic functions in python.
3. [PyDrive](https://pythonhosted.org/PyDrive/) - Library for API calls to Google Drive in python.

## Installation
1. Complete the instructions in Step 1 at [Google Drive for Python](https://developers.google.com/drive/v2/web/quickstart/python) to get the file client_secret.json
2. Proceed with the following: 
	```
	pip install PyDrive
	pip install pycrypto
	git clone https://github.com/arunjohnkuruvilla/SecureDrive.git
	cd SecureDrive
	python setup.py
	```

3. Move client_secret.json to the current working directory

## Running the tool
```
python pyDrive.py 
```
## API Reference
```
help			:	Shows this help banner
ls			:	List files in the current working directory
pwd			:	NOT IMPLEMENTED - Prints the present working directory
upload <filename>	: 	Uploads a file to drive
download <filename> 	:	Downloads the file
cd <directory>		:	NOT IMPLEMENTED - Open directory specified.	
delete <filename>	:	Open directory specified.
clear			:	Clears the screen
logout			:	Log off current session.
exit			:	Exit the application without logging out.
```
## Future Work

* Implement a hierarchical file systems. The current system just supports one level.
* Use a USB as a key, which has to be plugged in to communicate with Google Drive
* Implement multiple cryptographic schemes as encryption and hashing options.
* Add a GUI - Make more user friendly
* Port to other OSs and mobile.

## To Contribute
**Contributions are more than welcome**. Please feel free to develop any of the features mentioned in future work. Also please feel free to send us more ideas.

## Contributors

* [Arun John Kuruvilla](https://github.com/arunjohnkuruvilla)
* [Dushyanth NP Chowdary](https://github.com/chowdaryd)
