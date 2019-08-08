#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def read_xml_general(xmlfile):
    root = ET.parse(xmlfile).getroot()
    for i in root.findall(".//"):
        print(i.tag,i.text)

read_xml_general(sys.argv[-1])