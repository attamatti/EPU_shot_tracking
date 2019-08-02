#!/usr/bin/env python


import sys
import os
import glob
import xml.etree.ElementTree as ET

errormsg = '''
USAGE: EPU_find_duplicates_quantifoil.py <EPU directory> <hole size (um)> <hole spacing (um)>
'''

def get_dirs(datapath):
    try:
        metadata_path = os.path.abspath('{0}/Metadata/'.format(datapath))
    except:
        sys.exit('metadata files not found at {0}{1}'.format('{0}/Metadata/'.format(datapath),errormsg))
    try:
        GSimages_path = os.path.abspath('{0}/Images-Disc1/'.format(datapath))
    except:
        sys.exit('grid squares not found at {0}'.format('{0}/Images-Disc1/{1}'.format(datapath,errormsg)))
    return(metadata_path,GSimages_path)
    
def parse_xml_GS(xml_file):
    root = ET.parse(xml_file).getroot()
    targets = []
    for i in root.findall(".//"):
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

def get_files(dirpath,ext):
    files = glob.glob('{0}/{1}'.format(dirpath,ext))
    print('targeting metadata : {0}/{1}'.format(dirpath,ext))
    print('{0} files/dirs found'.format(len(files)))
    return(files)
    
def parse_xml_image(xml_file):
    root = ET.parse(xml_file).getroot()
    ABXYZ = []
    beamshift = []
    for i in root.findall(".//{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}Position/"):
        ABXYZ.append(i.text)
    for i in root.findall(".//"):
        if i.tag == '{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}acquisitionDateTime':
            acctime = i.text
    for i in root.findall(".//{http://schemas.datacontract.org/2004/07/Fei.SharedObjects}BeamShift/"):
        beamshift.append(float(i.text))
    return(ABXYZ)

def calc_dist(xy1,xy2):
    xd = abs(xy1[0]-xy2[0])
    yd = abs(xy1[1]-xy2[1])
    return(xd+yd)

def pretty_aq_time(t,d):
    return('{0}-{1}-{2} {3}:{4}:{5}'.format(d[0:3],d[4:6],d[6:],t[0:2],t[2:4],t[4:],))
# identify the selected squares
try:
    holesize = float(sys.argv[2])
    holespacing = float(sys.argv[3])
except:
    sys.exit(errormsg)

selected= []        
print('Finding all gridsquares')
metadata,images = get_dirs(sys.argv[1])
GS_metadata= get_files(metadata,'*.dm')

for i in GS_metadata:
    GS_data = parse_xml_GS(i)
    if GS_data[4] == 'true':
        selected.append(i.split('/')[-1].replace('.dm',''))
print('Found {0} selected gridsquares to process'.format(len(selected)))

for GS in selected:
    imagepath = '{0}/{1}/'.format(images,GS)
    DA_MD= glob.glob('{0}Data/*.xml'.format(imagepath,GS))
    foilholes = {}          #{foilhole:[DAimage1,Daimage2...,DAimagen],[stageposx,stageposy]}
    if len(DA_MD) > 0:
        for f in DA_MD:
            if f.split('_')[-1] != 'Fractions.xml':
                FHid = f.split('/')[-1].split('_')[1]
                try:
                    foilholes[FHid][0].append(f)
                except:
                    foilholes[FHid] = [[f]]
    for hole in foilholes:
        ABXYZ = parse_xml_image(foilholes[hole][0][0])
        foilholes[hole].append([float(ABXYZ[2])*(10**6),float(ABXYZ[3])*(10**6)])
    
    bins = [0,0.25,0.50,1,1.1]
    n=0
    binn=0
    sys.stdout.write(GS)
    sys.stdout.flush()
    hits = []
    if len(foilholes) == 0:
        sys.stdout.write(' - no data aquisition images for this square\n')
        sys.stdout.flush()
    else:
        for hole in foilholes:    
            for hole2 in foilholes:
                if hole != hole2:
                    dif = calc_dist(foilholes[hole][1],foilholes[hole2][1])
                    if dif < (0.5*holesize)+holespacing and [hole2,hole,dif] not in hits:
                        hits.append([hole,hole2,dif])
                    while float(n)/(len(foilholes)**2) > bins[binn]:
                        sys.stdout.write('.....'.format(binn))
                        sys.stdout.flush()
                        binn+=1
                    n+=1
        sys.stdout.write('{0} possible duplicates found\n'.format(len(hits)))
        sys.stdout.flush()
        done = []
        for hit in hits:
            t1 = foilholes[hit[0]][0][0].split('/')[-1].split('_')[-1].replace('.xml','')
            d1 = foilholes[hit[0]][0][0].split('/')[-1].split('_')[-2]
            t2 = foilholes[hit[1]][0][0].split('/')[-1].split('_')[-1].replace('.xml','')
            d2 = foilholes[hit[1]][0][0].split('/')[-1].split('_')[-2]
            print('{0}   aquisition time: {1}'.format('_'.join(foilholes[hit[0]][0][0].split('/')[-1].split('_')[:3]),pretty_aq_time(t1,d1)))
            print('{0}   aquisition time: {1}'.format('_'.join(foilholes[hit[1]][0][0].split('/')[-1].split('_')[:3]),pretty_aq_time(t2,d2)))
            print('--')
