#!/usr/bin/env python

import sys


vers = 0.1
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

print('''
---- remove duplicate micrographs vers {0} ----'''.format(vers))
try:
    duplist = open('duplicate_shots.txt','r').readlines()
    print('{0} duplicate foilholes found'.format(len(duplist)))
except:
   sys.exit("ERROR: couldn't find duplicate_shots.txt file")
try:
    labels,header,data = read_starfile_new(sys.argv[1])
except:
    sys.exit("ERROR: couldn't parse micrographs star file\nUSAGE: ./clean_duplicates <micrographs ctf file>")

dupdic = {}         #{micname: [duplicate1, duplicate2, ..., duplicaten]}
for i in duplist:
    try:
        dupdic[i.split()[1]].append(i.split()[0])
    except:
        dupdic[i.split()[1]] = [i.split()[0]]
    
all_mics = []
timesdic = {}               #{micrograph:aqusition time}
for i in data:
    micname = '_'.join(i[labels['_rlnMicrographName']].split('/')[-1].split('_')[:2])
    aqtime = ''.join(i[labels['_rlnMicrographName']].split('/')[-1].split('_')[-3:-1])
    all_mics.append(micname)
    timesdic[micname] = aqtime
tdkeys = list(timesdic)
tdkeys.sort()

tosslist = {}       #{mic:one that replaces it}
for mic in all_mics:
    if mic in dupdic:
        if mic in dupdic:
            dlist = [mic]
            for dup in dupdic[mic]:
                dlist.append(dup)
            dlist.sort(key=lambda x: timesdic[x])
            for badmic in dlist[1:]:
                tosslist[badmic] = dlist[0]
finalout = open('duplicates_removed.star','w')

for i in header:
    finalout.write('{0}\n'.format(i))
tosscount = 0
goodcount = 0
for i in data:
    micname = '_'.join(i[labels['_rlnMicrographName']].split('/')[-1].split('_')[:2])
    if micname in tosslist:
        print('threw away a micrograph from {0} which is a duplicate of {1}'.format(micname,tosslist[micname]))
        tosscount+=1
    else:
        finalout.write('{0}\n'.format('   '.join(i)))
        goodcount+=1
print('Discarded {0} micrographs from {1} foilholes'.format(tosscount,len(duplist)))
print('wrote duplicates_removed.star with {0} micrographs'.format(goodcount))