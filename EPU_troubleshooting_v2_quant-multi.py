#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import mrcfile
import glob
import xml.etree.ElementTree as ET
import os

def get_dirs(datapath):
    try:
        metadata_path = os.path.abspath('{0}/Metadata/'.format(datapath))
    except:
        sys.exit('metadata tfiles not found at {0}'.format('{0}/Metadata/'.format(datapath)))
    try:
        GSimages_path = os.path.abspath('{0}/Images-Disc1/'.format(datapath))
    except:
        sys.exit('grid squares not found at {0}'.format('{0}/Images-Disc1/'.format(datapath)))
    return(metadata_path,GSimages_path)

def get_files(dirpath,ext):
    files = glob.glob('{0}/{1}'.format(dirpath,ext))
    print('targeting metadata : {0}/{1}'.format(dirpath,ext))
    print('{0} files/dirs found'.format(len(files)))
    return(files)
    
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

def get_image_info(image):
    '''for a DA level image read it and return x,y,z,nominalDF'''
    micdata = mrcfile.open(image)
    mic_ed = micdata.extended_header
    sq_cent_x,sq_cent_y,sq_z,sq_apix,timestamp = (mic_ed[0][12],mic_ed[0][13],mic_ed[0][14],mic_ed[0][17],mic_ed[0][3])
    micdata.close()
    return(sq_cent_x,sq_cent_y,sq_z,sq_apix,timestamp)

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
    return(targetID,order,stageX,stageY,stageZ,drawX,drawY)

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
        
    
    return(ABXYZ,acctime,beamshift)

def DA_to_SQ(dax,day,sqx,sqy,sqapix):
    '''transform a DA scale image center to a GS image scale '''
    newx = sqx-dax
    newy = sqy-day
    return(4096-(2048+(newx/sqapix)),2048+(newy/sqapix)) #why is x flipped???

# get grid square metadata
print('Finding all gridsquares')
metadata,images = get_dirs(sys.argv[1])
GS_dic = {}                 #{gridsquare:[order,stageX,stageY,selected,completed,[targets]]}
GS_metadata= get_files(metadata,'*.dm')
for i in GS_metadata:
    GS_dic[i] = parse_xml_GS(i)
# identify the selected squares
selected= []
for i in GS_dic:
    if GS_dic[i][4] == 'true':
        selected.append(i)
print('Found {0} selected gridsquares to process'.format(len(selected)))
for i in selected:
    print(i,GS_dic[i][5],len(GS_dic[i][6]))

# draw the targeting info
for i in selected:
    ######## MAIN FoiLHOLE DICT will have #{ID number: [[FoilHole images metadata],[Targeting info],[DataAquisition images metadata]]
    
    
    
    # get GS image - make picture
    GS_name = i.split('/')[-1].split('.')[0]
    imagepath = '{0}/{1}/'.format(images,GS_name)
    
    print('----------')
    print(GS_name)
    print('gridsquare metadata: {0}'.format(i))
    print('gridsquare images  : {0}'.format(imagepath))
    GS_images = glob.glob('{0}/*.mrc'.format(imagepath))
    GS_images.sort()
    GS_image = GS_images[-1]
    print('{0} gridsquare images found :: using {1}'.format(len(GS_images),GS_image.split('/')[-1]))
    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)
# get targets for the square xy positions from metadata
    tmd_dir = '{0}/{1}'.format(metadata,GS_name)
    target_metadata = get_files(tmd_dir,'*.dm')
    targetsx,targetsy,targetsorder = [],[],[]
    targets_dic = {}            #{targetID:[order,stageX,stageY,stageZ,drawX,drawY,scaledstagex,scaledstagey] last two added later}
    
    # get coords of targets from metadata
    for target in target_metadata:
        targetID,order,stageX,stageY,stageZ,drawX,drawY = parse_xml_target(target)    
        targetsx.append(float(drawX))
        targetsy.append(float(drawY))
        targetsorder.append(order)
        # somtimes target ID is used sometime the name of the metadata file WTF!!
        targets_dic[targetID] = [order,stageX,stageY,stageZ,drawX,drawY]
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')] = [order,stageX,stageY,stageZ,drawX,drawY]
    for n in range(len(targetsx)):
        plt.text(targetsx[n],targetsy[n],targetsorder[n],size=3)
    

    # map out the stage positions for the targets using the mrc headers for the actual images
    gsx,gsy = (float(GS_dic[i][2]),float(GS_dic[i][3]))
    print('gridsquare centre check \nmetadata:\t{0:.7f}\t{1:.7f}\nmrc header:\t{2:.7f}\t{3:.7f}'.format(gsx*1000,gsy*1000,sq_cent_x*1000,sq_cent_y*1000))
    
    targetstagex,targetstagey = [],[]
    GS_centerdata='no aqusitions this square'

    for target in target_metadata:
        targetID,order,stageX,stageY,stageZ,drawX,drawY = parse_xml_target(target)    
        
        ### GS metadata and image extended header have different values for center... assuming because actual image has been centerd 
        ## picking one for now...
        ## from metadata

        #scaled = DA_to_SQ(float(stageX),float(stageY),gsx,gsy,sq_apix)
        #GS_centerdata = 'GridSquare metadata'
        
        ## from actual image header ... 
        scaled = DA_to_SQ(float(stageX),float(stageY),sq_cent_x,sq_cent_y,sq_apix)
        GS_centerdata = 'GridSquare image header'
        
        #add the target stage locations to target_dic
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[0])
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[1])

        targetstagex.append(scaled[0]) 
        targetstagey.append(scaled[1])
    
    print('determined gridsquare center using: {0}'.format(GS_centerdata))
    
    # mark the centre of the gridsquare image
    plt.scatter(2048,2048,c='green',s=20,alpha=0.6,marker='x')

    ## plot the differenes between stage positions in GS metadata and targeting metadata
    xzip = zip(targetsx,targetstagex)
    yzip = zip(targetsy,targetstagey)    
    for pair in range(len(xzip)):
        plt.plot(xzip[pair],yzip[pair],linewidth=0.5)
    plt.scatter(targetsx,targetsy,s=2)
    plt.scatter(targetstagex,targetstagey,c='red',s=2,alpha=0.4)

    plt.tight_layout()
    plt.savefig('target_locations_{0}.png'.format(GS_name.split('/')[-1].split('.')[0]),dpi=400)
    plt.close()

    ##### make a dict of all the requested aquisitions on this gridsquare
    ## initilize the next plot
    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)

    
    ## get the foilhole metadata files:
    print('FoilHoles metadata: {0}/FoilHoles/*.xml'.format(imagepath,GS_name))
    foilholes_MD = glob.glob('{0}/FoilHoles/*.xml'.format(imagepath,GS_name))
    foilholes_MD.sort(reverse=True)
    foilholes = {}             #{foilhole:[centered image,last centering image(s),...,first centeringimages(s)]}
    for FH in foilholes_MD:
        FH_name = FH.split('/')[-1].split('_')[1]
        try:
            foilholes[FH_name][0].append(FH)
        except:
            foilholes[FH_name] = [[FH]]
    
    # match the targets to the foilholes add that info to the main dict
    for FH in foilholes:
        try:
            #print(FH,len(foilholes[FH][0]),targets_dic[FH])
            foilholes[FH].append(targets_dic[FH])
        except:
            #print(FH,len(foilholes[FH][0]),'no target data found')
            foilholes[FH].append(['NONE'])
    
    #get the DataAqusition images :
    DA_MD= glob.glob('{0}Data/*.xml'.format(imagepath,GS_name))
    for f in DA_MD:
        if f.split('_')[-1] != 'Fractions.xml':
            id = f.split('/')[-1].split('_')[1]
            if id in foilholes:
                try:
                    foilholes[id][2].append(f)
                except:
                    foilholes[id].append([f])
            else:
                print('skipped {0}'.format(id))
    for i in foilholes:
       if len(foilholes[i]) != 3:
            foilholes[i].append(['NONE'])
    
    ## output all of the Foilhole info
    for hole in foilholes:        # check for skipped holes
        if foilholes[hole][2][0] == 'NONE':
            ndashots = 0
        else:
            ndashots = len(foilholes[hole][2])
        # output -targeting info
        print('\nFoilhole: {1}\tTargetID {2}\t#CentShots: {3}\t#DA images {4}\tDA files: {5}'.format(GS_name,hole,foilholes[hole][1][0],len(foilholes[hole][0]),ndashots,foilholes[hole][2][0].split('/')[-1].split('.')[0][:39]))
        print('Square center:    2048 2048 {0:.3f} {1:.3f} A/px: {2}'.format(float(sq_cent_x)*1000000,float(sq_cent_y)*1000000,float(sq_apix)*1000000000))
        try:
            print('target XY:        {0} {1}                 TargetLocation_{2}.dm'.format(foilholes[hole][1][4],foilholes[hole][1][5],hole))
            print('target stage pos: {0} {1} {2:.3f} {3:.3f} TargetLocation_{4}.dm'.format(int(round(foilholes[hole][1][6],0)),int(round(foilholes[hole][1][7],0)),float(foilholes[hole][1][1])*1000000,float(foilholes[hole][1][2])*1000000,hole.split('/')[-1]))
        except:
            print('No target info    XXXX XXXX')
        #plot the targeting info xys
        try:
            plt.scatter(float(foilholes[hole][1][4]),float(foilholes[hole][1][5]),c='r',s=2,alpha=0.3)
            plt.text(float(foilholes[hole][1][4]),float(foilholes[hole][1][5]),hole,size=3,color='red')
        except:
            pass
        
        centitsx,centitsy = [],[]
        dasx,dasy = [],[]
        
        # output - foilhole centering
        connectthedotsx,connectthedotsy=[],[]
        n=0
        for citer in reversed(foilholes[hole][0]):
            ABXYZ,acctime,beamshift = parse_xml_image(citer)
            stagexy = DA_to_SQ(float(ABXYZ[2]),float(ABXYZ[3]),sq_cent_x,sq_cent_y,sq_apix)
            print('iteration {0:02d}:     {1} {2} {6:.3f} {7:.3f} Beamshift x,y ({3},{4}) {5}'.format(n,int(round(stagexy[0],0)),int(round(stagexy[1],0)),beamshift[0],beamshift[1],citer.split('/')[-1],float(ABXYZ[2])*1000000,float(ABXYZ[3])*1000000))
            
            # data for graphing
            connectthedotsx.append(float(stagexy[0]))
            connectthedotsy.append(float(stagexy[1]))            
            centitsx.append(float(stagexy[0]))
            centitsy.append(float(stagexy[1]))            
            n+=1
        
        #output - Data-aquisition
        if foilholes[hole][2] != ['NONE']:
            for DA in foilholes[hole][2]:
                ABXYZ,acctime,beamshift = parse_xml_image(DA)
                stagexy = DA_to_SQ(float(ABXYZ[2]),float(ABXYZ[3]),sq_cent_x,sq_cent_y,sq_apix)
                print('DA shot:          {0} {1} {5:.3f} {6:.3f} Beamshift x,y ({2},{3}) {4}'.format(int(round(stagexy[0],0)),int(round(stagexy[1],0)),beamshift[0],beamshift[1],DA.split('/')[-1],float(ABXYZ[2])*1000000,float(ABXYZ[3])*1000000))
                # data for grahing
                dasx.append(float(stagexy[0]))
                dasy.append(float(stagexy[1]))
                connectthedotsx.append(float(stagexy[0]))
                connectthedotsy.append(float(stagexy[1]))
        else:
            print('Data aquisition skipped')
    ## make teh plot
        
        plt.plot(connectthedotsx,connectthedotsy,linewidth=0.5)
        
        try:
            plt.scatter(dasx,dasy,c='blue',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
            plt.text(dasx[0],dasy[0],hole,size=3)
        except:
            pass
        plt.scatter(centitsx,centitsy,c='yellow',edgecolor='black',s=4,linewidth=0.5)
    plt.tight_layout()
    plt.savefig('{0}_shots.png'.format(GS_name),dpi=400)
    plt.close()


###########################################################################
### now redo it all with the right filename
## make a dict with the correct DA image names
print('---- now doing the corrected plots ----')
for i in selected:
    print(i,GS_dic[i][5],len(GS_dic[i][6]))
for i in selected:
    
    ## make a dict to translate the DA images to teh correct name
    # first do the DA images
    GS_name = i.split('/')[-1].split('.')[0]
    imagepath = '{0}/{1}/'.format(images,GS_name)
    DAimglist = []
    allDAimages= glob.glob('{0}Data/*.xml'.format(imagepath,GS_name))
    for f in allDAimages:
        if f.split('_')[-1] != 'Fractions.xml':
            DAimglist.append(f)
    DAimglist.sort()
    #n=0
    #DA_name_dic ={}     #{DA name: DA_name+1}     
    #for daimg in DAimglist:
    #    try:
    #        DA_name_dic[daimg] = DAimglist[n+1]
    #    except:
    #        DA_name_dic[daimg] = DAimglist[n]           # don't know how the last one is handled...
    #    n+=1
    #
    ## use that same one to make a dict to translate targeting info
    #target_translate = {}
    ids = []
    for daimg in DAimglist:
        foilholeno = daimg.split('/')[-1].split('_')[1]
        if foilholeno not in ids:
            ids.append(foilholeno)
    n=0     
    target_translate = {}
    for id in ids:
        if id not in target_translate:                  # only do it once for multiple DA shots/foilhole
            try:
                target_translate[id] = ids[n+1]
            except:
                target_translate[id] = id # still don't know how to handle the last one
        n+=1

    ##### make a dict of all the requested aquisitions on this gridsquare
    ## initilize the next plot
    print('----------')
    print(GS_name)
    print('gridsquare metadata: {0}'.format(i))
    print('gridsquare images  : {0}'.format(imagepath))
    GS_images = glob.glob('{0}/*.mrc'.format(imagepath))
    GS_images.sort()
    GS_image = GS_images[-1]
    print('{0} gridsquare images found :: using {1}'.format(len(GS_images),GS_image.split('/')[-1]))
    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)
    
    ###### make a new targets dict
    tmd_dir = '{0}/{1}'.format(metadata,GS_name)
    target_metadata = get_files(tmd_dir,'*.dm')
    targetsx,targetsy,targetsorder = [],[],[]
    targets_dic = {}            #{targetID:[order,stageX,stageY,stageZ,drawX,drawY,scaledstagex,scaledstagey] last two added later}
    
    # get coords of targets from metadata
    for target in target_metadata:
        targetID,order,stageX,stageY,stageZ,drawX,drawY = parse_xml_target(target)    
        targetsx.append(float(drawX))
        targetsy.append(float(drawY))
        targetsorder.append(order)
        # somtimes target ID is used sometime the name of the metadata file WTF!!
        targets_dic[targetID] = [order,stageX,stageY,stageZ,drawX,drawY]
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')] = [order,stageX,stageY,stageZ,drawX,drawY]
    for n in range(len(targetsx)):
        plt.text(targetsx[n],targetsy[n],targetsorder[n],size=3)
    

    # map out the stage positions for the targets using the mrc headers for the actual images
    gsx,gsy = (float(GS_dic[i][2]),float(GS_dic[i][3]))
    print('gridsquare centre check \nmetadata:\t{0:.7f}\t{1:.7f}\nmrc header:\t{2:.7f}\t{3:.7f}'.format(gsx*1000,gsy*1000,sq_cent_x*1000,sq_cent_y*1000))
    
    targetstagex,targetstagey = [],[]
    GS_centerdata='no aqusitions this square'

    for target in target_metadata:
        targetID,order,stageX,stageY,stageZ,drawX,drawY = parse_xml_target(target)    
        
        ### GS metadata and image extended header have different values for center... assuming because actual image has been centerd 
        ## picking one for now...
        ## from metadata

        #scaled = DA_to_SQ(float(stageX),float(stageY),gsx,gsy,sq_apix)
        #GS_centerdata = 'GridSquare metadata'
        
        ## from actual image header ... 
        scaled = DA_to_SQ(float(stageX),float(stageY),sq_cent_x,sq_cent_y,sq_apix)
        GS_centerdata = 'GridSquare image header'
        
        #add the target stage locations to target_dic
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[0])
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[1])

        targetstagex.append(scaled[0]) 
        targetstagey.append(scaled[1])
    
    print('determined gridsquare center using: {0}'.format(GS_centerdata))    
    
    #############
    
    ## get the foilhole metadata files:
    print('FoilHoles metadata: {0}/FoilHoles/*.xml'.format(imagepath,GS_name))
    foilholes_MD = glob.glob('{0}/FoilHoles/*.xml'.format(imagepath,GS_name))
    foilholes_MD.sort(reverse=True)
    foilholes = {}             #{foilhole:[centered image,last centering image(s),...,first centeringimages(s)]}
    for FH in foilholes_MD:
        FH_name = FH.split('/')[-1].split('_')[1]
        try:
            foilholes[FH_name][0].append(FH)
        except:
            foilholes[FH_name] = [[FH]]
    
    # match the targets to the foilholes add that info to the main dict
    for FH in foilholes:
        fhDAdata = []
        try:
            #print(FH,len(foilholes[FH][0]),targets_dic[FH])
            foilholes[FH].append(targets_dic[FH])
        except:
            #print(FH,len(foilholes[FH][0]),'no target data found')
            foilholes[FH].append(['NONE'])
        try:
            FH_data = glob.glob('{0}Data/FoilHole_{1}*.xml'.format(imagepath,target_translate[FH]))
            if len(FH_data) > 0:
                for DAf in FH_data:
                    if '_Fractions' not in DAf:
                        fhDAdata.append(DAf)
                foilholes[FH].append(fhDAdata)
        except:
            foilholes[FH].append(['NONE'])
    
    #get the DataAqusition images :
    #DA_MD= glob.glob('{0}Data/*.xml'.format(imagepath,GS_name))
    #for f in DA_MD:
    #    if f.split('_')[-1] != 'Fractions.xml':
    #        id = f.split('/')[-1].split('_')[1]
    #        f = DA_name_dic[f]              ######## switched to the right name!
    #        if id in foilholes:
    #            try:
    #                foilholes[id][2].append(f)
    #            except:
    #                foilholes[id].append([f])
    #        else:
    #            print('skipped {0}'.format(id))
    #for ifh in foilholes:
    #   if len(foilholes[ifh]) != 3:
    #        foilholes[ifh].append(['NONE'])
    
    ## output all of the Foilhole info
    #put the foilholes in order of aquisition
    holeskeys = list(foilholes)
    holeskeys.sort(key=lambda x: foilholes[x][1][0])
    
    for hole in foilholes:        # check for skipped holes
        print foilholes[hole]
        if foilholes[hole][2][0] == 'NONE':
            ndashots = 0
        else:
            ndashots = len(foilholes[hole][2])
        # output -targeting info
        print('\nFoilhole: {1}\tTargetID {2}\t#CentShots: {3}\t#DA images {4}\tDA files: {5}'.format(GS_name,hole,foilholes[hole][1][0],len(foilholes[hole][0]),ndashots,'_'.join(foilholes[hole][2][0].split('/')[-1].split('.')[0].split('_')[:-3])))
        print('Square center:    2048 2048 {0:.3f} {1:.3f} A/px: {2}'.format(float(sq_cent_x)*1000000,float(sq_cent_y)*1000000,float(sq_apix)*1000000000))
        try:
            print('target XY:        {0} {1}                 TargetLocation_{2}.dm'.format(foilholes[target_translate[hole]][1][4],foilholes[target_translate[hole]][1][5],target_translate[hole]))
            print('target stage pos: {0} {1} {2:.3f} {3:.3f} TargetLocation_{4}.dm'.format(int(round(foilholes[target_translate[hole]][1][6],0)),int(round(foilholes[target_translate[hole]][1][7],0)),float(foilholes[hole][1][1])*1000000,float(foilholes[hole][1][2])*1000000,target_translate[hole])) # corrected target
        except:
            print('No target info    XXXX XXXX')
        #plot the targeting info xys
        try:
            plt.scatter(float(foilholes[target_translate[hole]][1][4]),float(foilholes[target_translate[hole]][1][5]),c='r',s=2,alpha=0.3) #with the correction
            plt.text(float(foilholes[target_translate[hole]][1][4]),float(foilholes[target_translate[hole]][1][5]),hole,size=3,color='red') #with the correction
        except:
            pass
        
        centitsx,centitsy = [],[]
        dasx,dasy = [],[]
        
        # output - foilhole centering
        connectthedotsx,connectthedotsy=[],[]
        n=0
        for citer in reversed(foilholes[hole][0]):
            ABXYZ,acctime,beamshift = parse_xml_image(citer)
            stagexy = DA_to_SQ(float(ABXYZ[2]),float(ABXYZ[3]),sq_cent_x,sq_cent_y,sq_apix)
            print('iteration {0:02d}:     {1} {2} {6:.3f} {7:.3f} Beamshift x,y ({3},{4}) {5}'.format(n,int(round(stagexy[0],0)),int(round(stagexy[1],0)),beamshift[0],beamshift[1],citer.split('/')[-1],float(ABXYZ[2])*1000000,float(ABXYZ[3])*1000000))
            
            # data for graphing
            connectthedotsx.append(float(stagexy[0]))
            connectthedotsy.append(float(stagexy[1]))            
            centitsx.append(float(stagexy[0]))
            centitsy.append(float(stagexy[1]))            
            n+=1
        
        #output - Data-aquisition
        if foilholes[hole][2] != ['NONE']:
            done = False
            for DA in foilholes[hole][2]:
                ABXYZ,acctime,beamshift = parse_xml_image(DA)
                stagexy = DA_to_SQ(float(ABXYZ[2]),float(ABXYZ[3]),sq_cent_x,sq_cent_y,sq_apix)
                print('DA shot:          {0} {1} {5:.3f} {6:.3f} Beamshift x,y ({2},{3}) {4}'.format(int(round(stagexy[0],0)),int(round(stagexy[1],0)),beamshift[0],beamshift[1],DA.split('/')[-1],float(ABXYZ[2])*1000000,float(ABXYZ[3])*1000000))
                # data for grahing
                if done == False:
                    dasx.append(float(stagexy[0]))
                    dasy.append(float(stagexy[1]))
                    connectthedotsx.append(float(stagexy[0]))
                    connectthedotsy.append(float(stagexy[1]))
                    done = True

        else:
            print('Data aquisition skipped')
    ## make teh plot
        
        plt.plot(connectthedotsx,connectthedotsy,linewidth=0.5)
        
        try:
            plt.scatter(dasx,dasy,c='blue',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
            plt.text(dasx[0],dasy[0],hole,size=3)
        except:
            pass
        plt.scatter(centitsx,centitsy,c='yellow',edgecolor='black',s=4,linewidth=0.5)
    plt.tight_layout()
    plt.savefig('{0}_shots_corrected.png'.format(GS_name),dpi=400)
    plt.close()