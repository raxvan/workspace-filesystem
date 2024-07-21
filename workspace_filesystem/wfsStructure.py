

import os
import sys
import json
import time
import hashlib
from datetime import datetime

_chunk = 1024 * 1024 * 8

def _create_default_ignore(il):
	il.push(".git")
	il.push(".wfs")
	il.push("__pycache__")
	il.push("package-lock.json")
	il.push("node_modules")
	il.push(".egg-info")

def sha512File(file_path):
	sha512_hash = hashlib.sha512()
	with open(file_path, 'rb') as file:
		while chunk := file.read(_chunk):
			sha512_hash.update(chunk)
	return sha512_hash.hexdigest()

class IgnoreList:
	def __init__(self, parent, basedir):
		self.parent = parent
		self.basedir = basedir
		self.ends = []
		self.starts = []
		self.parts = []

	def push(self, line):
		l = line.strip()
		if l.startswith("*"):

			if l.endswith("*"):
				# *NAME*
				self.parts.append(l.replace("*",""))
			else:
				# *NAME
				self.ends.append(l.replace("*",""))
		elif l.endswith("*"):
			# NAME*
			self.starts.append(l.replace("*",""))
		else:
			# NAME
			self.ends.append(l)

	def load(self, file):
		f = open(file, "r")
		lines = f.readlines()
		f.close()

		for l in lines:
			self.push(l)

	def accept(self, abspath):
		for e in self.ends:
			if abspath.endswith(e):
				return False

		rpath = os.path.relpath(abspath, self.basedir)

		for e in self.starts:
			if rpath.startswith(e):
				return False

		for e in self.parts:
			if e in rpath:
				return False

		if self.parent != None:
			return self.parent.accept(abspath)

		return True

#######################################################################################

class Structure():
	def __init__(self):
		self.fileList = None
		self.folderList = None
		self.hashMap = None
		self.hash = None

		self.scanTime = None
		self.ignored = None

	def doScan(self, rootdir):
		self.fileList = []
		self.folderList = []
		self.hash = None
		self.scanTime = time.time()
		self.ignored = 0
		
		ignorelist = IgnoreList(None, rootdir)
		
		_create_default_ignore(ignorelist)

		_scan_recursive(self, rootdir, ignorelist, rootdir)

		self.fileList.sort()
		self.folderList.sort()

		self.hashMap = None
		self.hash = None

	def doHash(self, rootdir):

		hmap = {}
		sha512_hash = hashlib.sha512()
	
		for f in self.fileList:
			path = os.path.join(rootdir, f)
			sha = sha512File(path)
			hmap[f] = sha
			sha512_hash.update(sha.encode('ascii'))

		for f in self.folderList:
			sha512_hash.update(f.encode('ascii'))

		self.hashMap = hmap
		self.hash = sha512_hash.hexdigest()

	def save(self, filePath):
		content = json.dumps({
			"hash" : self.hash,
			"scanTimepoint" : self.scanTime,
			"ignoredCount" : self.ignored,

			"filelist" : self.fileList,
			"folderlist" : self.folderList,
			"hashMap" : self.hashMap,
		})
		f = open(filePath, "w")
		f.write(content)
		f.close()

	def load(self, filePath):
		f = open(filePath, "r")
		content = f.read()
		f.close()
		content = json.loads(content)

		self.hash = content["hash"]
		self.scanTime = content["scanTimepoint"]
		self.ignored = content["ignoredCount"]

		self.fileList = content["filelist"]
		self.folderList = content["folderlist"]
		self.hashMap = content["hashMap"]

	def delta(self, other):
		#changes of this structure vs `other`
		
		this_files = set(self.fileList)
		other_files = set(other.fileList)

		new_files = this_files - other_files
		deleted_files = other_files - this_files
		common_files = this_files | other_files

		_out_new_files = { k : self.hashMap[k] for k in new_files }
		_out_changed_files = {}

		for f in common_files:
			fh = self.hashMap[f]
			if fh != other.hashMap[f]:
				_out_changed_files[f] = fh

		this_folders = set(self.folderList)
		other_folders = set(other.folderList)

		new_folders = this_folders - other_folders
		deleted_folders = other_folders - this_folders

		return {
			"+" : _out_new_files,
			"*" : _out_changed_files,
			"-" : list(deleted_files),
			"+f": list(new_folders),
			"-f": list(deleted_folders),
		}


	def info(self):
		result = {}

		if self.scanTime != None:
			dt_object = datetime.fromtimestamp(self.scanTime)
			formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
			result['scanned'] = formatted_time

		if self.fileList != None:
			result['file-count'] = len(self.fileList)
		else:
			result['file-count'] = "[unknown]"

		if self.folderList != None:
			result['empty-folder-count'] = len(self.folderList)
		else:
			result['empty-folder-count'] = "[unknown]"

		if self.hash != None:
			result['hash'] = self.hash
		else:
			result['hash'] = "[unknown]"

		if self.ignored != None:
			result['ignored'] = self.ignored

		return result


#######################################################################################

def _scan_recursive(structure, rootdir, ignorelist, absdir):
	l = len(structure.fileList)

	wfi = os.path.join(absdir, ".wfsignore")
	if os.path.exists(wfi):
		ignorelist = IgnoreList(ignorelist, absdir)
		ignorelist.load(wfi)

	for f in os.listdir(absdir):

		path = os.path.join(absdir, f)

		if not ignorelist.accept(path):
			structure.ignored += 1
			continue

		if os.path.isfile(path):
			structure.fileList.append(os.path.relpath(path, rootdir))
		elif os.path.isdir(path):
			_scan_recursive(structure, rootdir, ignorelist, path)

	if l == len(structure.fileList):
		structure.folderList.append(os.path.relpath(absdir, rootdir))

#######################################################################################
#######################################################################################

