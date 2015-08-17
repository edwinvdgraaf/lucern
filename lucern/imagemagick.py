import os
import subprocess

def execute(command):
  process = subprocess.Popen(command, stdout=subprocess.PIPE)
  out, err = process.communicate()
  return out

def compare(*args):
  cmd = list(args)
  cmd.insert(0, "compare")
  process = subprocess.Popen(cmd, shell=False,
     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = process.communicate()
  return process.returncode, out
