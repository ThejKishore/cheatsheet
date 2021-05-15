import os
import shutil

print("project name :")
projectName = input()

# copy files recursivley
dest="/Users/thej/test-project/"+projectName

# Copy the content of
# source to destination
destination = shutil.copytree("/Users/thej/test-project/src", dest)
print("After copying file:")

#iterate over each file and update the project name
for dname, dirs, files in os.walk(dest):
    for fname in files:
        
        fpath = os.path.join(dname, fname)
        with open(fpath) as f:
            s = f.read()
        s = s.replace("${project}", projectName)

        os.remove(fpath)
        fname = fname.replace("${project}", projectName)
        fpath = os.path.join(dname, fname)

        with open(fpath, "w") as f:
            f.write(s)
