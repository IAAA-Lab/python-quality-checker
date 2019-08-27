from qualitychecker import URL
from guppy import hpy


def printSize(prompt):
    s = str(prompt)[0:100].split("set of ")[1]
    s = s.split("Total size = ")
    print(s[0], s[1].split("\n")[0])


def xtest_memory_leak():
    h = hpy()
    with open("uris.txt", "r") as uris:

        for uri in uris:
            URL(uri)
            printSize(h.heap())


def xtest_output():
    with open("uris.txt", "r") as uris:
        with open("out.csv", "w") as out:
            keys = URL("/").dict().keys()
            out.write("\t".join(keys) + "\n")

            for uri in uris:
                u = URL(uri)
                print(u)
                out.write(str(u) + "\n")
