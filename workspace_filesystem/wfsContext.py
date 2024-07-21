

import os
import sys
import json
import shutil
import zipfile

_this_dir_ = os.path.dirname(__file__)

from . import wfsStructure

def _read_lines(path):
	f = open(path, "r")
	result = f.readlines()
	f.close()
	return [r.strip() for r in result]

def _zip_files(output_zip, root_folder, file_list):
	with zipfile.ZipFile(output_zip, 'w') as zipf:
		for f in file_list:
			file_path = os.path.join(root_folder, f)
			zipf.write(file_path, os.path.relpath(file_path, start=root_folder))

class Context():
	def __init__(self, w):
		self.workspace = w
		self.wmeta = os.path.join(w, ".wfs")
		self.structurePath = os.path.join(self.wmeta, "structure.json")

		self.structure = None

	def initialize(self):
		self.structure = wfsStructure.Structure()

		p = self.structurePath
		if os.path.exists(p):
			self.structure.load(p)
		else:
			self.structure.save(p)

	def scan(self):
		self.structure.doScan(self.workspace)
		self.structure.save(self.structurePath)

	def hash(self):
		self.structure.doHash(self.workspace)
		self.structure.save(self.structurePath)

	def info(self):
		i = self.structure.info()
		i['path'] = self.workspace
		return i

	def delta(self):
		s = wfsStructure.Structure()
		s.doScan(self.workspace)
		s.doHash(self.workspace)
		return s.delta(self.structure)

def _find_workspace(path):
	current_dir = path
	parent_dir = os.path.dirname(current_dir)

	while current_dir != parent_dir:
		wp = os.path.join(current_dir, ".wfs")
		if os.path.exists(wp):
			return current_dir

		current_dir = parent_dir
		parent_dir = os.path.dirname(current_dir)
	return None

#######################################################################################
#######################################################################################

def CreateWorkspace(path):
	p = os.path.abspath(path)

	f = _find_workspace(p)
	if f != None:
		raise Exception(f"Nested workspaces are not allowed; check {f}")

	wp = os.path.join(p, ".wfs")
	os.makedirs(wp)

	ctx = Context(wp)
	ctx.initialize()

	return ctx

def FindWorkspace(path):
	p = os.path.abspath(path)

	f = _find_workspace(p)
	if f == None:
		raise Exception(f"Failed to find workspace from {path}")

	wp = os.path.join(f, ".wfs")
	ctx = Context(p)
	ctx.initialize()

	return ctx

#######################################################################################
#######################################################################################
