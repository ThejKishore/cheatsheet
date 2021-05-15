import os
import shutil
import sys

def readFiles(fpath,projectName):
    with open(fpath) as f:
        s = f.read()
    s = s.replace("${project}", projectName)
    return s

def writeContent(fpath,data):
    with open(fpath, "w") as f:
        f.write(data)

def renamefile(fpath,fname,projectName,dname):
    os.remove(fpath)
    fname = fname.replace("${project}", projectName)
    return os.path.join(dname, fname)

def copyFileRecursively(src,dest):
    shutil.copytree(src, dest)
    print("After copying file:")

def main(args):
    projectName = input(" Enter Project Name : ")

    print(" project name enterd : "+projectName)

    src = input(" SRC Directory : ")
    # src = "/Users/thej/test-project/demo"
    print(" src directory : "+src)

    trgt = input(" TRGT Directory : ")
    print(" trgt directory : " + trgt)

    # copy files recursivley
    dest = trgt+projectName
    # dest = "/Users/thej/test-project/"+projectName
    print(" dest directory : " + dest)

    copyFileRecursively(src,dest)

    # iterate over each file and update the project name
    for dname, dirs, files in os.walk(dest):
        for fname in files:
            fpath = os.path.join(dname, fname)
            print(fpath)
            if (fpath.endswith(".jar") or fpath.endswith(".DS_Store")):
                continue
            else:
                data = readFiles(fpath,projectName)
                fpath = renamefile(fpath,fname,projectName,dname)
                writeContent(fpath,data)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
