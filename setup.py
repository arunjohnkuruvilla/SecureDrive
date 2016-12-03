# Secure Drive
# setup.py
# Generate your private key
# 

import commands
import json
import os

output = commands.getstatusoutput("openssl enc -aes-256-cbc -k secret -P -md sha1")

output = output[1].split("\n")

private_key = {}
for item in output:
	item = item.split("=")
	key = item[0].upper()
	key = key.split(" ")[0]
	value = item[1]
	if key == "IV":
		value = value[:16]
	private_key[key] = value

final = json.dumps(private_key)

if os.path.exists("private.key"):
	os.rename("private.key", "private.key.bak")

open("private.key", "w").write(final)

