#!/usr/bin/env python

import mrcfile
import sys
import glob

vers = '0.1'

errormsg = '''Look for duplicate images
run in the relion project directory
Arguments:
--raw       path to the Equipment folder containing the raw images'''

class Arg(object):
    _registry = []
    def __init__(self, flag, value, req):
        self._registry.append(self)
        self.flag = flag
        self.value = value
        self.req = req

def make_arg(flag, value, req):
    Argument = Arg(flag, value, req)
    if Argument.req == True:
        if Argument.flag not in sys.argv:
            print(errormsg)
            sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
    if Argument.value == True:
        try:
            test = sys.argv[sys.argv.index(Argument.flag)+1]
        except ValueError:
            if Argument.req == True:
                print(errormsg)
                sys.exit("ERROR: required argument '{0}' is missing".format(Argument.flag))
            elif Argument.req == False:
                return False
        except IndexError:
                print(errormsg)
                sys.exit("ERROR: argument '{0}' requires a value".format(Argument.flag))
        else:
            if Argument.value == True:
                Argument.value = sys.argv[sys.argv.index(Argument.flag)+1]
        
    if Argument.value == False:
        if Argument.flag in sys.argv:
            Argument.value = True
        else:
            Argument.value = False
    return Argument.value

def get_paths():
    print('''
--- EPU duplcate image finder vers {0} ---
---         Lacy carbon version        ---\n'''.format(vers))
    rawpath = make_arg('--raw',True,True)
    # add error checking here later
    return(rawpath)

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

def read_image(mrcimage):
    '''read mrc image return [stagex,stagey,illuminated_area,timestamp]'''
    themrc = mrcfile.open(mrcimage,permissive=True)
    e_head = themrc.extended_header
    stagex = float(e_head[0][12])
    stagey = float(e_head[0][13])
    illarea = float(e_head[0][33])
    timestamp = float(e_head[0][3])
    return(stagex,stagey,illarea,timestamp)
    
def calc_dist(x1,y1,x2,y2):
    xd = abs(x1-x2)
    yd = abs(y1-y2)
    return(xd+yd)

def trace_to_GS(rawpath):
    '''map all the grid squares assign micrograpsh to grid square '''
    mic2GS = {}
    GS2mics = {}
    for GS in glob.glob('{0}/Grid*'.format(rawpath)):
        for mic in glob.glob('{1}/Data/*.mrc'.format(rawpath,GS)):
            if '_Fractions'not in mic:
                mic2GS[mic.split('/')[-1]] = GS.split('/')[-1]
                try:
                    GS2mics[GS.split('/')[-1]].append(mic.split('/')[-1])
                except:
                    GS2mics[GS.split('/')[-1]] = [mic.split('/')[-1]]
    return(mic2GS,GS2mics)

def parse_result(resultdic,micsdic):
    found = []
    hits = []
    n = 0
    for i in resultdic:
        hits.append([])
        hit = False
        done = False
        for j in resultdic[i]:
            if [i,j] not in found:
                hit = True
                hits[n].append([j,micsdic[j][3],(micsdic[j][0],micsdic[j][1])])
                found.append([j,i])
            for k in resultdic[i]:
                found.append([k,j])
                found.append([j,k])
            if hit == True and done == False:
                hits[n].append([i,micsdic[i][3],(micsdic[i][0],micsdic[i][1])])
                done = True
        n+=1
    for i in hits:
        if len(i) > 0:
            i.sort(key=lambda x: x[1])
            for j in i:
                print(j[0],j[1],j[2])
            print('')
            
#get the data files ans trace mic to grid squares
rawpath = get_paths()
mic2GS,GS2mic = trace_to_GS(rawpath)          # {micname:gridsquare}, {gridsquare: [mics,mics,...,mics]}



for gridsquare in GS2mic:
    # make the mics dic
    sys.stdout.write('indexing {0}'.format(gridsquare))
    sys.stdout.flush()
    count = 0
    mics = {}
    xys = []
    overlaps = {}
    for mic in GS2mic[gridsquare]:
        stagex,stagey,illarea,timestamp = read_image('{0}{1}/Data/{2}'.format(rawpath,gridsquare,mic))
        mics[mic] = [stagex,stagey,illarea,timestamp]
        count+=1
        if count%10 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
    print('DONE')
    sys.stdout.write('looking for duplicates')
    sys.stdout.flush()
    for mic in mics:
        for mic2 in mics:
            diff = calc_dist(mics[mic][0],mics[mic][1],mics[mic2][0],mics[mic2][1])
            if diff < 0.55*mics[mic][2] and mic != mic2:
                try:
                    overlaps[mic].append(mic2)
                except:
                    overlaps[mic] = [mic2]
            count+=1
            if count%1000 == 0:
                sys.stdout.write('.')
                sys.stdout.flush()    
    print'DONE'
    if len(overlaps) > 0:
        print'OH NO! Found some duplicates'
        parse_result(overlaps,mics)
    else:
        print('no duplicates found')



