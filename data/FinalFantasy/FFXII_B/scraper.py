import time
import requests
import os

pageKeys= [
	'1yVXjEKYqboerrkavKV6FGB_3tnVoCNIP9OfikDQ5fbk',
	'1BzbP1J-Dw2oMI8FRWRSpW1Advwi3AyE7CRruQ1TW5vk',
	'1q_z56uKxi-eDPyO8JfFRbM31yJ-EqtHMmiJRi66KSk0',
	'1quvXPeaOLtvpq0yb4-RpZP4LTUBqpS3iUWfYFE7OUcs',
	'1zBy_jYXyiUVslb96hhVWcmociZ0ewX2CWNeXq750VZI',
	'1oTvIGK23B-2f8SssH9pvZeldWEsu7UePgisD_nE3kPo',
	'1dD6Rc_hIw5B19vzSj-dJZGaIohRL-u1bW4J0yjJD-dA',
	'1XsdX_O5oc4yPkPOXfH4iyn3FbGTdjQ9STiEXWGxQsjM',
	'13K_-SluOW0PiSQoM1Xp9RBXwYQ6acMJ2f-4bSifxC8I',
	'1CgLSViRqep9mMNiiRvycKhV5qgtxw9icn7SGz61OnaQ',
	'1tnoRRBg2hO1UzTAeHEfsIogKsdwzAoMYXSnAoLP2x0s'     # side quests
]

i = 0
for pageKey in pageKeys:
	i += 1
	fileName = "raw/page_"+str(i).zfill(3)+".html"
	if not os.path.isfile(fileName):
		response = requests.get('https://docs.google.com/document/d/'+ pageKey + '/export?format=html')
		o = open(fileName,'wb')
		o.write(response.content)
		o.close()
		time.sleep(3)