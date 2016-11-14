from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)
# Auto-iterate through all files that matches this query
file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
for file1 in file_list:
  	print('title: %s, id: %s' % (file1['title'], file1['id']))

file6 = drive.CreateFile({'id': '0B0JI-vW4dTAeOTItZldKOXFSdTA'})
file6.GetContentFile('catlove.png')