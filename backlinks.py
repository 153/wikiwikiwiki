import os
import edit

file_list = []
for x in os.listdir("pages"):
    if x.endswith(".txt"):
        file_list.append(x)

print(file_list)

for fn in file_list:
    with open(f"pages/{fn}", "r") as content:
        content = content.read()
    fn = fn.split(".")[0]
    edit.backlinks(fn, content)
