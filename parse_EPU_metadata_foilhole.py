#!/usr/bin/env python

#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def parse_xml_FH(xml_file):
    root = ET.parse(xml_file).getroot()
    for i in root.findall(".//"):
        print(i.tag,i.text)

parse_xml_FH(sys.argv[-1])