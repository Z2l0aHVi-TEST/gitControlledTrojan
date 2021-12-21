import os

def run(**args):

	print("[#] In Dirlister module...")
	files = os.listdir('.')
	return str(files)