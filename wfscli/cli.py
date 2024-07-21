
import os
import sys
import time
import json
import shutil
import argparse

from workspace_filesystem import wfsContext

def _get_wdir(cwd, args):
	path = cwd
	if args.path != None:
		path = args.path

	return wfsContext.FindWorkspace(path)

def _do_create(cwd, args):
	path = cwd
	if args.path != None:
		path = args.path

	wfsContext.CreateWorkspace(path)
	print(f"Done")

def _do_hash(w):
	print(f"hashing {w.workspace}")

	start = time.time()
	w.hash()
	end = time.time()
	t = end - start

	h = w.structure.hash
	print(f"hashing completed in {t:.4f} seconds")
	print(f"\t-> {h}")
	

def _do_scan(w):
	print(f"scanning {w.workspace}")

	start = time.time()
	w.scan()
	end = time.time()
	t = end - start

	structure = w.structure

	files_count = str(len(structure.fileList)).rjust(16)
	efolders_count = str(len(structure.folderList)).rjust(16)
	ignored = str(structure.ignored).rjust(16)
	print(f"scanning completed in {t:.4f} seconds")
	print(f"{files_count} : files")
	print(f"{efolders_count} : empty folders")
	print(f"{ignored} : ignored")

def _do_info(w):
	
	i = w.info()
	ml = max([len(k) for k,_ in i.items()])
	
	for k, v in i.items():
		print(k.rjust(ml) + " : " + str(v))
	
def _do_delta(w):

	i = w.delta()

	print(json.dumps(i, indent=2))
	#ml = max([len(k) for k,_ in i.items()])
	#
	#for k, v in i.items():
	#	print(k.rjust(ml) + " : " + str(v))


def _exec_action(args):

	currentDirectory = os.getcwd()

	acc = args.action
	if acc == "create":
		_do_create(currentDirectory, args)
		return

	w = _get_wdir(currentDirectory, args)

	if acc == "scan":
		_do_scan(w)
	elif acc == "hash":
		_do_hash(w)
	elif acc == "delta":
		_do_delta(w)
	elif acc == "info":
		_do_info(w)

	os.chdir(currentDirectory)


def main():
	user_arguments = sys.argv[1:]

	parser = argparse.ArgumentParser()
	#parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help="Run in quiet mode.")

	subparsers = parser.add_subparsers(description='Actions:')

	_sp = subparsers.add_parser('create', description='Create workspace with path')
	_sp.set_defaults(action='create')
	_sp.add_argument('path', type=str, help='workspace path!', nargs='?', default=None)

	_sp = subparsers.add_parser('info', description='Create workspace with path')
	_sp.set_defaults(action='info')
	_sp.add_argument('path', type=str, help='workspace path!', nargs='?', default=None)

	_sp = subparsers.add_parser('scan', description='Scan workspace structure.')
	_sp.set_defaults(action='scan')
	_sp.add_argument('path', type=str, help='workspace path!', nargs='?', default=None)

	_sp = subparsers.add_parser('hash', description='Compute hash of the workspace structure.')
	_sp.set_defaults(action='hash')
	_sp.add_argument('path', type=str, help='workspace path!', nargs='?', default=None)

	_sp = subparsers.add_parser('delta', description='Compute the changes vs the structure.')
	_sp.set_defaults(action='delta')
	_sp.add_argument('path', type=str, help='workspace path!', nargs='?', default=None)

	args = parser.parse_args(user_arguments)

	if hasattr(args, 'action'):
		_exec_action(args)
	else:
		print("Usage:")
		print("\t-> wpm [-q] ACTION [args]")
		print("ARGS:")
		print("\t-q : `quiet` mode, print less stuff.")
		print("ACTION Choices:")
		for k, _ in subparsers.choices.items():
			print(f"\t-> {k}")
