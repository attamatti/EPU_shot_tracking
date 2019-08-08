#!/usr/bin/env python

import xml.etree.ElementTree as ET
import sys

def read_xml_GS(xmlfile):
    root = ET.parse(xmlfile).getroot()
    namespace1 = '{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}'
    namespace2='{http://schemas.datacontract.org/2004/07/System.Drawing}'
    targets = []
    for i in root.findall(".//"):
        print(i.tag,i.text)
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Types}Id':
            sqID = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}Order':
            order = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}X':
            stageX = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Y':
            stageY = i.text
        if i.tag == '{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}Selected':
            selected = i.text
        if i.tag =='{http://schemas.datacontract.org/2004/07/Applications.Epu.Persistence}State':
            completed = i.text
        if i.tag =='{http://schemas.datacontract.org/2004/07/Fei.Applications.Common.Types}FileName':
            targets.append(i.text)
    return(sqID,order,stageX,stageY,selected,completed,targets)

read_xml_GS(sys.argv[1])