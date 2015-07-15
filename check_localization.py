#!/usr/bin/env python
import sys
import os
import glob
import codecs
import re
from termcolor import colored, cprint

#
# CLASS PRINCIPAL 
#
class RootClass(object):
	"""docstring for RootClass"""
	def __init__(self, log):
		super(RootClass, self).__init__()
		self.log = log
	
	def showLog(self, message, addSpace):
		if self.log == "INFO":
			if addSpace == True:
				self.showSpace()
			self.showMessage(colored("--->>> LOG : " + message, 'yellow'))

	def showSpace(self):
		self.showMessage("")

	def showLogSpace(self):
		if self.log == "INFO":
			self.showMessage("")

	def showTitle(self, title):
		self.showSpace()
		self.showMessage("#######################################################################")
		self.showMessage("#\n# " + title + " #\n#")
		self.showMessage("#######################################################################")
		self.showSpace()
	
	def showLine(self, line):
		self.showMessage("  	---> AT LINE : " + colored(line, 'yellow', attrs=['bold']))

	def showKey(self, key):
		self.showMessage("  ---> KEY : " + colored(key, 'white', 'on_red')) 

	def showFile(self, filePath):
		self.showMessage(" ### FILE : "+ colored(filePath, 'green', attrs=['bold']))

	def showDone(self):
		self.showSpace()
		self.showMessage(colored('DONE :)...', 'green', attrs=['bold']))
		self.showSpace()

	def showMessage(self, message):
		print(message)
		

#
# CLASS FIND FILES TO GET THE LIST OF ALL THE FILES WE CAN HAVE
#
class FindFiles(RootClass):
	"""docstring for FindFiles"""
	def __init__(self, log, rootPath):
		super(FindFiles, self).__init__(log)
		self.showLog("****** START OBJECT : FindFiles ******", True)
		self.rootPath = rootPath
		self.filesPath = []

	def run(self):
		self.arrayFiles();
		self.showLogSpace()
		self.showMessage(" ###### NUMBER OF FILES FOUND : "+ str(len(self.filesPath)) + " ######")

	def arrayFiles(self):
		self.showSpace()
		self.showMessage(" ###### PROJECT PATH : " + self.rootPath)
		self.showLogSpace()
		for root, dirs, files in os.walk(self.rootPath, topdown=False):
			for name in files:
				path = os.path.join(root, name)
				if self.removedFiles(path, name) == True:
					self.showLog("------ FILE FOUND : " + path, False)
					self.filesPath.append(path)

	def removedFiles(self, pathFile, name):
		if "/.git/" in pathFile:
			return False
		if "/Pods/" in pathFile:
			return False

		
		elif ".m" == name[len(name)-2:len(name)]:
			return True
		elif ".strings" in name:
			return True
		else:
			return False


#
# CLASS FIND KEYS INTO THE FILE Base.lproj/Localizable.strings
#
class FindKeys(RootClass):
	"""docstring for F"""
	def __init__(self, log, rootPath, filesPath, filePathSource):
		super(FindKeys, self).__init__(log)
		self.showLog("****** START OBJECT : FindKeys ****** ", True)
		self.filesPath = filesPath
		self.rootPath = rootPath
		self.filePath = filePathSource
		self.keys = []

	def run(self):
		self.arrayKeys();
		self.showLogSpace()
		self.showMessage(" ###### NUMBER OF KEYS FOUND : "+ str(len(self.keys)) + " ######")
		if len(self.keys) == 0:
			self.showMessage("---> ERROR : NOT FOUND FILE '"+ self.filePath + "'...")
			self.showMessage("---> INFO : If you want to set an other file 'Localizable.strings' please add it to the comment line")
			self.showMessage("---> EXEMPLE : python check_localization.py PATH_FILE -s 'Base.lproj/Localizable.strings' -l")

	def arrayKeys(self):
		for path in self.filesPath:
			if self.filePath.lower() in path.lower():
				self.showSpace()
				self.showMessage(" ###### OPEN FILE : " + path)
				self.showLogSpace()
				try:
					with codecs.open(path, 'r', 'utf-16') as f:
						for line in f:
							if self.isAKey(line):
								key = self.getKey(line)
								self.keys.append(key)
				except UnicodeError:
					with codecs.open(path, 'r', 'utf-8') as f:
						for line in f:
							if self.isAKey(line):
								key = self.getKey(line)
								self.keys.append(key)

	def isAKey(self, line):
		# check if the first caractaire is "
		return (line[0:1] == "\"")
				
	def getKey(self, line):
		#get the key from the line
		mList  = line.split("=");
		key = mList[0];
		key = self.clearKey(key)
		self.showLog("---- FOUND KEY : " + key, False)
		return key;

	def clearKey(self, key):
		indexFirst = -1
		indexLast = -1
		for i in range(len(key)):
			if "\"" == key[i]:
				indexFirst = i
				break
		
		for i in reversed(range(len(key))):
			if "\"" == key[i]:
				indexLast = i
				break
		return key[indexFirst+1:indexLast]





#
# CLASS HOW WILL TEST IF ALL THE KEYS INTO Localication are been used
#
class KeyAreNotUsed(RootClass):
	"""docstring for KeyAreNotUsed"""
	def __init__(self, log, filesPath, keys):
		super(KeyAreNotUsed, self).__init__(log)
		self.showLog("****** START OBJECT : KeyAreNotUsed ****** ", True)
		self.filesPath = filesPath
		self.keys = keys
		self.keysBeenUsed = []

	def runCheck(self):
		self.showTitle("SEE BELLOW ALL KEYS WHICH ARE NOT BEEN USED INTO THE APPLICATION")
		if self.keys and self.filesPath:
			self.checkAllFiles();
			self.removedKeysUsed();
		else:
			self.showMessage("NO KEYS OR FILES FOUND ")

	def checkAllFiles(self):
		for filePath in self.filesPath:
			if ".strings" not in filePath:
				self.showLog("##### OPEN FILE : " + filePath, True)
				with codecs.open(filePath, 'r', 'utf-8') as f:
					for line in f:
						self.checkAllKeys(line)

	def checkAllKeys(self, line):
		for key in self.keys:
			if key in line:
				self.keysBeenUsed.append(key)

	def removedKeysUsed(self):
		for key in self.keys:
			isUser = False
			for keyBeenUsed in self.keysBeenUsed:
				if keyBeenUsed in key:
					isUser = True
			if isUser == False:
				self.showKey(key)


class KeysMissing(RootClass):
	"""docstring for KeysMissing"""
	def __init__(self, log, filesPath, keys):
		super(KeysMissing, self).__init__(log)
		self.showLog("****** START OBJECT : KeysMissing ****** ", True)
		self.filesPath = filesPath
		self.keys = keys
		self.currentFile = ""
		self.keysMissing = {}

	def runCheck(self):
		self.showTitle("SEE BELLOW ALL KEYS WHICH ARE NOT SET INTO Localizable.strings")
		if self.keys and self.filesPath:
			self.checkAllFiles();
		else: 
			self.showMessage("ERROR : NO KEYS OR FILES FOUND ")

	def checkAllFiles(self):
		for filePath in self.filesPath:
			self.currentFile = filePath
			if ".strings" not in filePath:
				self.showLog("##### OPEN FILE : " + filePath, True)
				with codecs.open(filePath, 'r', 'utf-8') as f:
					for line in f:
						self.checkKeysOnIt(line)

	def checkKeysOnIt(self, line):
		keysLine = re.findall(r'LocalizedString\(\@\"([^"]+)', line, re.DOTALL)
		if keysLine:
			self.extractKey(keysLine, line)
	
	def extractKey(self, keysLine, line):
		self.keysMissing = {}
		for keyLine in keysLine:
			isKeyUsed = False
			for key in self.keys:
				if (key == keyLine):
					isKeyUsed = True
					break
			if isKeyUsed == False:
				self.keysMissing.setdefault(keyLine, line)
		self.showResult();

	def showResult(self):
		if self.keysMissing:
			self.showFile(self.currentFile)
			for key in self.keysMissing:
				self.showKey(key)
				self.showLine(self.keysMissing[key])

def main():
	if (len(sys.argv) < 2):
		print("Nop... EXEMPLE : python check_localization.py PATH_FILE (OPTION: -s 'Base.lproj/Localizable.strings' -l)")

	if len(sys.argv) > 1:
		log = "NONE"
		file_path_default = "Base.lproj/Localizable.strings"
		for x in xrange(1,len(sys.argv)):
			if x == 1:
				path_base = sys.argv[1]
			elif x == 2 and "-s" in sys.argv[x]:
				pass
			elif x == 2 and "-l" in sys.argv[x]:
				log = "INFO"
			elif x == 3 and ".strings" in sys.argv[3]:
				file_path_default = sys.argv[3]
			elif x == 4 and ".l" in sys.argv[4]:
				log = "INFO"

		findFile = FindFiles(log, path_base)
		findFile.run()

		findKeys = FindKeys(log, path_base, findFile.filesPath, file_path_default)
		findKeys.run()
		
		keyAreUse = KeyAreNotUsed(log, findFile.filesPath, findKeys.keys)
		keyAreUse.runCheck()

		keysMissing = KeysMissing(log, findFile.filesPath, findKeys.keys)
		keysMissing.runCheck()

		keysMissing.showDone()

	
sys.exit(main());
