# SecureDrive

SecureDrive brings [Google Drive](https://www.google.com/drive/) to the command line. Allowing faster and more secure access to the cloud from the terminal. 


## Code Example

Show what the library does as concisely as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise.

## Dependencies

[OpenSSL](https://www.openssl.org/) - Library for cryptographic functions in python.
[PyCrypto](https://www.dlitz.net/software/pycrypto/) - Library for cryptographic functions in python.
[PyDrive](https://pythonhosted.org/PyDrive/) - Library for API calls to Google Drive in python.

## Installation
```
pip install PyDrive
pip install pycrypto
git clone https://github.com/arunjohnkuruvilla/SecureDrive.git
cd SecureDrive
python setup.py
python pydrive.py 
```

## API Reference
```
help				:	Shows this help banner
ls					:	List files in the current working directory
pwd					:	NOT IMPLEMENTED - Prints the present working directory
upload <filename>	: 	Uploads a file to drive
download <filename> :	Downloads the file
cd <directory>		:	NOT IMPLEMENTED - Open directory specified.	
delete <filename>	:	Open directory specified.
clear				:	Clears the screen
logout				:	Log off current session.
exit				:	Exit the application without logging out.
```

## Contributors

* Arun John Kuruvilla
* Dushyanth NP Chowdary