#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def parse_xml_target(xml_file):
    root = ET.parse(xml_file).getroot()
    for i in root.findall(".//"):
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Types}Id':
            targetID = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}Order':
            order = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}X':
            stageX = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Y':
            stageY = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Z':
            stageZ = i.text
        if i.tag =='{http://schemas.datacontract.org/2004/07/System.Drawing}x':
            drawX = i.text
        if i.tag =='{http://schemas.datacontract.org/2004/07/System.Drawing}y':
            drawY = i.text
        print(i,i.text)
    return(targetID,order,stageX,stageY,stageZ,drawX,drawY)

print(parse_xml_target(sys.argv[-1]))