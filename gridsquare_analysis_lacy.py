#!/usr/bin/env python

# compare CTF values from gCTF to microscope values
#
#
#
#


import sys
import mrcfile
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
# read ctf starfile

#-----------------------------------------------------------------------------------#
errormsg = '''compare CTF !!
run in the relion project directory
Arguments:
--ctf       ctf_starfile
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

def get_paths():
    ctffile = make_arg('--ctf',True,True)
    rawpath = make_arg('--raw',True,True)
    # add error checking here later
    return(ctffile,rawpath)

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

def parse_starfile_ctf(starfile):
    '''for each micrograph [defocus,ctfFOM]'''
    (labels,header,data) = read_starfile_new(starfile)
    micrographs = {}
    for i in data:
        micname = i[labels['_rlnMicrographName']].split('/')[-1]
        defocus = -(float(i[labels['_rlnDefocusU']])+float(i[labels['_rlnDefocusV']]))/20000
        ctfFOM = (float(i[labels['_rlnCtfFigureOfMerit']]))
        micrographs[micname] = [defocus,ctfFOM]
    return(micrographs)

def get_scope_DFS(file):
    '''return the autofocus and applied defocus for a micrograph returns [defocus, app defocus, stagex, stagey,timestamp]'''
    themrc = mrcfile.open(file,permissive=True)
    e_head = themrc.extended_header
    DF,appDF,stagex,stagey,timestamp = (e_head[0][20],e_head[0][22],e_head[0][12],e_head[0][13],e_head[0][3])
    themrc.close()
    return(DF,appDF,stagex,stagey,timestamp)

def make_bg(square_level_image): 
    '''make the plot with the mrc ofthe gridsquare as background'''
    gridsquare_image = mrcfile.open(square_level_image)
    micdata = gridsquare_image.data
    plt.axis('off')
    plt.imshow(micdata,cmap='Greys_r')
    mic_ed = gridsquare_image.extended_header
    sq_cent_x,sq_cent_y,sq_z,sq_apix = (mic_ed[0][12],mic_ed[0][13],mic_ed[0][14],mic_ed[0][17])
    gridsquare_image.close()
    return(sq_cent_x,sq_cent_y,sq_z,sq_apix) 

def DA_to_SQ(dax,day,sqx,sqy,sqapix):
    '''transform a DA scale image center to a GS image scale '''
    newx = dax-sqx
    newy = day-sqy
    print(2048+(newx/sqapix),2048-(newy/sqapix))
    return(2048+(newx/sqapix),2048-(newy/sqapix)) 
  
#get the data files ans trace mic to grid squares
ctffile,rawpath = get_paths()
ctfmicsdic = (parse_starfile_ctf(ctffile))      # {micname_Fractions:[defocus,ctfFOM]}
GSdic,micsGSdic = trace_to_GS(rawpath)          # {micname:gridsquare}, {gridsquare: [mics,mics,...,mics]}


heights,scopeDFS,gctfDFS,diffs,FOMs = [],[],[],[],[]

#update the dics wiith more info final output = {micname_Fractions:[defocus,ctfFOM,height,appDF,diff,centerx,centery]}
for i in ctfmicsdic:
    try:
        print(i,GSdic[i.replace('_Fractions','')])
        filepath = '{0}{1}/Data/{2}'.format(rawpath,GSdic[i.replace('_Fractions','')],i.replace('_Fractions',''))
        print(filepath)
        DF,appDF,micx,micy,timestamp = (get_scope_DFS(filepath))
        DF = float(DF)*1000000
        appDF = float(appDF)*1000000
        gctfDF = float(ctfmicsdic[i][0])
        ctfFOM = ctfmicsdic[i][1]
        print(DF,appDF,gctfDF,appDF-gctfDF,ctfFOM)
        scopeDFS.append(appDF)
        gctfDFS.append(gctfDF)
        diffs.append(appDF-gctfDF)
        FOMs.append(ctfFOM)
        heights.append(DF)
        ctfmicsdic[i].append(DF)
        ctfmicsdic[i].append(appDF)
        ctfmicsdic[i].append(appDF-gctfDF)
        ctfmicsdic[i].append(micx)
        ctfmicsdic[i].append(micy)
        ctfmicsdic[i].append(timestamp)
    except:
        pass

##general defocus graphs
## not especially informative 
#plt.scatter(diffs,FOMs,c=gctfDFS,cmap='seismic')
#plt.ylabel('FOM')
#plt.xlabel('DF difference')
#plt.vlines([-1,1],min(FOMs),max(FOMs),linestyles=':',colors='grey')
#plt.colorbar()
#plt.show()
#plt.close()
#map info to gridsquare_images 

def map_to_GS(GSname,GS_infodic,mic_infodic,rawpath,item_number,label,colmap,normpoint,valmin,valmax):   # NO SPACES IN LABEL NAME!!!
    GSmic = '{0}{1}/{1}.mrc'.format(rawpath,GSname)
    SQ_x,SQ_y,SQ_z,SQ_apix= make_bg(GSmic)

    daxs,days,vals = [],[],[]
    for i in GS_infodic[GSname]:
         try:
            newfilename = i.replace('.','_Fractions.')
            #print(i,mic_infodic[newfilename])
            newpoint = DA_to_SQ(mic_infodic[newfilename][5],mic_infodic[newfilename][6],SQ_x,SQ_y,SQ_apix)
            daxs.append(newpoint[0])
            days.append(newpoint[1])   
            vals.append(mic_infodic[newfilename][item_number])
         except:
            print('image {0} not found in micrographs ctf star file -- SKIPPING'.format(i.replace('.','_Fractions.')))
    if normpoint == 'auto':
        normpoint = sum(vals)/len(vals)
    if valmin == 'auto':
        valmin = min(vals)
    if valmax == 'auto':
        valmax = max(vals)
    plt.scatter(daxs,days,c=vals,alpha = 0.5,s=80,cmap=colmap,norm=MidpointNormalize(midpoint=normpoint,vmin=valmin, vmax=valmax))
    color_bar = plt.colorbar()
    color_bar.set_alpha(1)
    color_bar.draw_all()
    plt.title(label)
    plt.tight_layout()
    plt.savefig('{0}_{1}.png'.format(GSname,label))
    plt.show()
    plt.close()
    return(min(vals),max(vals))

class MidpointNormalize(colors.Normalize):
	"""
	Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

	e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
	"""
	def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
		self.midpoint = midpoint
		colors.Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip=None):
		x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
		return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

for GS in micsGSdic:
    map_to_GS(GS,micsGSdic,ctfmicsdic,rawpath,4,'defocus_difference','seismic',0.0,'auto','auto')
    map_to_GS(GS,micsGSdic,ctfmicsdic,rawpath,2,'defocus','PuOr',0.0,'auto','auto')
    map_to_GS(GS,micsGSdic,ctfmicsdic,rawpath,7,'order_of_aquisition','gist_rainbow','auto','auto','auto')
    vmin,vmax = map_to_GS(GS,micsGSdic,ctfmicsdic,rawpath,0,'gctf_defocus','tab20b','auto','auto','auto')
    map_to_GS(GS,micsGSdic,ctfmicsdic,rawpath,3,'requested_defocus','tab20b','auto',vmin,vmax)
