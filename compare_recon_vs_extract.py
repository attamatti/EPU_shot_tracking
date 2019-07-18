#!/usr/bin/env python

# parse starfile get particle count from each micrograph
# get reported DF

import sys

###---------function: read the star file get the header, labels, and data -------------#######
def read_starfile_new(f):
    inhead = True
    alldata = open(f,'r').readlines()
    labelsdic = {}
    data = []
    header = []
    count = 0
    labcount = 0
    for i in alldata:
        if '_rln' in i:
            labelsdic[i.split()[0]] = labcount
            labcount +=1
        if inhead == True:
            header.append(i.strip("\n"))
            if '_rln' in i and '#' in i and  '_rln' not in alldata[count+1] and '#' not in alldata[count+1]:
                inhead = False
        elif len(i.split())>=1:
            data.append(i.split())
        count +=1
    
    return(labelsdic,header,data)
#---------------------------------------------------------------------------------------------#

def parse_starfile(starfile):
    '''for each micrograph [count,defocus]'''
    (labels,header,data) = read_starfile_new(starfile)
    micrographs = {}
    for i in data:
        micname = i[labels['_rlnMicrographName']].split('/')[-1]
        try:
            micrographs[micname][0] +=1
        except:
            defocus = (float(i[labels['_rlnDefocusU']])+float(i[labels['_rlnDefocusV']]))/2
            micrographs[micname] = [1,defocus]
    return(micrographs)

reconstruction = (parse_starfile(sys.argv[1]))
initial = (parse_starfile(sys.argv[2]))

for i in initial:
    try:
        print(i,initial[i][0],reconstruction[i][0],float(reconstruction[i][0])/float(initial[i][0]))
    except:
        pass