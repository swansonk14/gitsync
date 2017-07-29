import argparse
import os
from subprocess import Popen, PIPE
import time

def check_branch():
	if get_branch_name() != 'sync':
		exit()

def get_branch_name():
	p = Popen(['git', 'branch'], stdout=PIPE)
	branch_names = p.communicate()[0].decode('utf-8').split('\n')

	for branch_name in branch_names:
		if branch_name[0] == '*':
			return branch_name[2:]

def get_status():
	p = Popen(['git', 'status'], stdout=PIPE)
	status = p.communicate()[0].decode('utf-8')

	return status

def pull():
	p = Popen(['git', 'pull', 'origin', 'sync'], stdout=PIPE, stderr=PIPE)
	out = p.communicate()[0].decode('utf-8')
	if 'Already up-to-date' not in out:
		print(out)

def push():
	Popen(['git', 'add', '*']).wait()
	Popen(['git', 'status']).wait()
	Popen(['git', 'commit', '-m', 'sync']).wait()
	Popen(['git', 'push', 'origin', 'sync']).wait()

def main(create):
	# Exit if changes in current branch
	status = get_status()
	if not 'nothing to commit' in status:
		print(status)
		print('')
		print('Please commit or stash your changes before syncing')
		exit()

	# Delete local sync branch
	Popen(['git', 'branch', '-D', 'sync']).wait()

	# Match remote sync branch by pushing or pulling
	if create:
		# Force remote sync branch to match local sync branch
		Popen(['git', 'checkout', '-b', 'sync']).wait()
		Popen(['git', 'push', 'origin', 'sync', '--force']).wait()
	else:
		# Use remote sync branch
		Popen(['git', 'checkout', '-b', 'sync']).wait()
		Popen(['git', 'fetch', '--all']).wait()
		Popen(['git', 'reset', '--hard', 'origin/sync']).wait()

	# Check whether files have been modified every second.
	# If modified, push to github.
	# Pull every second.
	while True:
		status = get_status()
		if 'nothing to commit' in status:
			time.sleep(1)
		else:
			check_branch()
			push()

		check_branch()
		pull()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Syncing for git')
	parser.add_argument(
		'--create',
		default=False,
		action='store_true',
		help='Flag to create the sync branch based off the current branch')
	parser.add_argument(
		'--listen',
		default=False,
		action='store_true',
		help='Flag to create sync branch based on remote sync branch')
	args = parser.parse_args()

	if args.create == args.listen:
		raise ValueError('Must set exactly one flag')

	main(args.create)
