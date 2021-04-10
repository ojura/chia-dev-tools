import os
import sys
import shutil
from pathlib import Path
import hashlib
import re
import subprocess

from clvm_tools.clvmc import compile_clvm

def dev_util(args=sys.argv):
    cmd = args[1].lower()
    project_path = Path.cwd()
    script_root = Path(__file__).parent
    #Initialize a new project
    if cmd == "init" :
        project_path_lib = Path(project_path).joinpath("lib")
        project_path_std = Path(project_path_lib).joinpath("std")
        if not project_path_lib.exists():
            os.mkdir(project_path_lib)
        if project_path_std.exists() :
            shutil.rmtree(project_path_std)
        shutil.copytree(Path(script_root).joinpath("std"),project_path_std)
        hello_world_py = project_path_std.joinpath("examples","helloworld.py")
        hello_world_clvm = project_path_std.joinpath("clvm","helloworld.clvm")
        shutil.copy(hello_world_py,project_path)
        shutil.copy(hello_world_clvm,project_path)
        print("Run 'chialisp build' and then 'py helloworld.py'")
    #Build all the clvm in the current directory
    if cmd == "build" :
        clvm_files = list(Path(project_path).rglob("*.[cC][lL][vV][mM]"))
        already_compiled = []
        #Adjust for building only one file
        if (cmd == "build") & (len(args) > 2):
            clvm_files = list(filter(lambda e: e.name in args, clvm_files))
            all_hex_files = list(Path(project_path).rglob("*.[hH][eE][xX]"))
            staying_hex_files = list(filter(lambda e: args[2] not in e.name, all_hex_files))
            for hex_file in staying_hex_files:
                already_compiled.append(hex_file)

        for filename in clvm_files:
            filehash = ""
            with open(filename, "rb") as afile:
                buf = afile.read()
                afile.close()
                filehash = hashlib.sha256(buf).hexdigest()
            hex_file_name = (filename.name + "." + filehash + ".hex")
            full_hex_file_name = Path(filename.parent).joinpath(hex_file_name)
            already_compiled.append(full_hex_file_name)
            if not full_hex_file_name.exists():
                outfile = str(filename) + "." + filehash + ".hex"
                try:
                    print("Beginning compilation of "+filename.name+"...")
                    compile_clvm(str(filename),outfile)
                    print("...Compilation finished")
                except Exception as e:
                    print("Couldn't build "+filename+": "+e)
                    pass
        #clean up old hex files
        garbage_files = list(Path(project_path).rglob("*.[hH][eE][xX]"))
        garbage_files = list(filter(lambda e: e not in already_compiled, garbage_files))
        for file in garbage_files:
            file.unlink()