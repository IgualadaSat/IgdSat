import sys
import json


def custom_iterator(foo):
    for char in foo:
        if char == '\n':
            yield foo[:foo.index(char)]
            foo = foo[foo.index(char) + 1:]
    if foo:
        yield foo

file = ""
try:
    with open(sys.argv[1], 'r') as my_file:
        content = my_file.read()
        for line in custom_iterator(content):
            try:
                D = json.loads(line)
                #if D["G"][1] == 0:
                #    continue
                file += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (D["U"][0], D["C"][0],D["T"][0], D["T"][1], D["T"][2], D["T"][3], D["H"][0],D["A"][0], D["A"][1], D["P"][0] ,D["R"][0],D["R"][1], D["R"][2], D["G"][0] , D["G"][1], D["S"][0], D["S"][1], D["D"][0]) # You can add 10 meters of height to properly visualize in Google Earth
            except Exception as e:
                print(e)
                continue
except FileNotFoundError:
    print("File not found: {}".format(sys.argv[1]))
 # <extrude>1</extrude>

print("OK")
 
with open("%s.csv" % sys.argv[1], 'w') as my_file:
    my_file.write(file)
