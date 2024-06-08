#!/usr/bin/env python

# Convert DATA.txt to a KML file for Google Earth

import sys
import json
# By Megazar with many help from copilot :)


def custom_iterator(foo):
    for char in foo:
        if char == '\n':
            yield foo[:foo.index(char)]
            foo = foo[foo.index(char) + 1:]
    if foo:
        yield foo
KML="""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.0">
<Document>
<Placemark>
  <name>IgdSat</name>
  <description>IgdSat track</description>
  <Style><LineStyle><color>ff0000ff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>
      <MultiGeometry><LineString><coordinates>"""

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: {} <filename>".format(sys.argv[0]))
    sys.exit(1)

# Open the file specified in the first argument
try:
    with open(sys.argv[1], 'r') as my_file:
        content = my_file.read()
        for line in custom_iterator(content):
            try:
                D = json.loads(line)
                if D["G"][1] == 0:
                    continue
                KML += "%s,%s,%s " % (D["G"][1],D["G"][0], D["A"][1]) # You can add 10 meters of height to properly visualize in Google Earth
            except:
                continue

except FileNotFoundError:
    print("File not found: {}".format(sys.argv[1]))
 # <extrude>1</extrude>
KML += """</coordinates><altitudeMode>absolute</altitudeMode></LineString></MultiGeometry>
</Placemark>
</Document>
</kml>
"""

with open("%s.KML" % sys.argv[1], 'w') as my_file:
    my_file.write(KML)
