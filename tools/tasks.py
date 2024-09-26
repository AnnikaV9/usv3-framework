#
#  Invoke style task file for calling tools from poetry
#  as scripts.
#

import subprocess

def build_cython():
    subprocess.run(["python", "tools/build_cython.py", "build_ext", "--inplace"])
