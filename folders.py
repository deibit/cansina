import itertools

ABC = "abcdefghijklmnopqrstuwxyz"
folders = []
p = itertools.product(ABC, ABC)
for n in p:
    folders.append("".join(n))

f = open("folder.txt", "w")
for n in folders:
    f.write("%s\n" % n)

