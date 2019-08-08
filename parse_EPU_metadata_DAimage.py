#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def parse_xml_DA(xml_file):
    root = ET.parse(xml_file).getroot()
    ABXYZ = []
    beamshift = []
    for i in root.findall(".//{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Position/"):
        print(i,i.text)
        ABXYZ.append(i.text)
    for i in root.findall(".//"):
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}acquisitionDateTime':
            print (i,i.text)
            acctime = i.text
    for i in root.findall(".//{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamShift/"):
        beamshift.append(float(i.text))
        
    
    return(ABXYZ,acctime,beamshift)
    
    
parse_xml_DA(sys.argv[-1])