import argparse
import sys

from tempfile import mkstemp
from shutil import move
from os import remove, close, path

# http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
  """Ask a yes/no question via raw_input() and return their answer.
  
  "question" is a string that is presented to the user.
  "default" is the presumed answer if the user just hits <Enter>.
      It must be "yes" (the default), "no" or None (meaning
      an answer is required of the user).

  The "answer" return value is one of "yes" or "no".
  """
  valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
           "no":"no",     "n":"no"}
  if default == None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while 1:
    sys.stdout.write(question + prompt)
    choice = raw_input().lower()
    if default is not None and choice == '':
      return default
    elif choice in valid.keys():
      return valid[choice]
    else:
      sys.stdout.write("Please respond with 'yes' or 'no' "\
                       "(or 'y' or 'n').\n")

parser = argparse.ArgumentParser(description='Remove lines ending with specified string in specified file')
parser.add_argument('filename', help='what file to delete lines from')
parser.add_argument('string', help='the string to look for at end of line')

if __name__ == "__main__":
  args = parser.parse_args()
  if not path.isfile(args.filename):
    print "Could not find the input file"
    sys.exit(1)

  print "Removing lines that end in: {0}".format(args.string)

  #first make temp file to write new file
  temp_fh, temp_abspath = mkstemp()
  temp_file = open(temp_abspath, 'w')

  with open(args.filename, 'r') as f:
    for line in f:
      if not line.strip().endswith(args.string):
        temp_file.write(line)

  temp_file.close()
  close(temp_fh)

  if bool(query_yes_no("Do you want us to overwrite the file?") == "yes"):
    remove(args.filename)
    move(temp_abspath, args.filename)
  else:
    newFilePath = raw_input("Enter the new filename: ")
    while path.isfile(newFilePath):
      print "That file already exists! Try a different filename."
      newFilePath = raw_input("Enter the new filename: ")
    move(temp_abspath, newFilePath)
