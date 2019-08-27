from qualitychecker import URL
from guppy import hpy


def printSize(prompt):
    s = str(prompt)[0:100].split("set of ")[1]
    s = s.split("Total size = ")
    print(s[0], s[1].split("\n")[0])


def xtest_memory_leak():
    h = hpy()
    with open("uris.txt", "r") as uris:
        print(uris)
        for uri in uris:
            u = URL(uri)
            print(u)
            printSize(h.heap())
