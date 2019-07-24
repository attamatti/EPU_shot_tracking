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
    newx = dax-sqx
    newy = day-sqy
    return(2048+(newx/sqapix),2048-(newy/sqapix)) 

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
        #test change
        #targets_dic[targetID] = [order,stageX,stageY,stageZ,drawX,drawY]
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')] = [order,stageX,stageY,stageZ,drawX,drawY]
    for n in range(len(targetsx)):
        plt.text(targetsx[n],targetsy[n],targetsorder[n],size=3)
    

    # map out the stage positions for the targets using the mrc headers for the actual images
    gsx,gsy = (float(GS_dic[i][2]),float(GS_dic[i][3]))
    print('gridsquare centre check \nmetadata:\t{0:.7f}\t{1:.7f}\nmrc header:\t{2:.7f}\t{3:.7f}'.format(gsx*1000,gsy*1000,sq_cent_x*1000,sq_cent_y*1000))
    
    targetstagex,targetstagey = [],[]
    GS_centerdata='no aqusitions this square'
    # didn't need to read the files again.... could have used exisiting dict
    for target in target_metadata:
        targetID,order,stageX,stageY,stageZ,drawX,drawY = parse_xml_target(target)    
        
        ### GS metadata and image extended header have different values for center...
        ## picking one for now...
        ## from metadata

        #scaled = DA_to_SQ(float(stageX),float(stageY),gsx,gsy,sq_apix)
        #GS_centerdata = 'metadata'
        
        ## from actual image header ... 
        scaled = DA_to_SQ(float(stageX),float(stageY),sq_cent_x,sq_cent_y,sq_apix)
        GS_centerdata = 'image header'
        
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[0])
        targets_dic[target.split('/')[-1].split('_')[1].replace('.dm','')].append(scaled[1])

        targetstagex.append(scaled[0])
        targetstagey.append(scaled[1])
    
    print('determined gridsquare center from: {0}'.format(GS_centerdata))
    
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
    plt.savefig('target_locations_{0}.png'.format(GS_name.split('/')[-1].split('.')[0]),dpi=300)
    plt.close()

    ### for each target that was actually imaged get the stage position of the foilhole image
    ### do it form bothteh metadata and the image header and compare
    foilhole_images = glob.glob('{0}/{1}/FoilHoles/FoilHole*.mrc'.format(images,GS_name))
    foilhole_metadata = glob.glob('{0}/{1}/FoilHoles/FoilHole*.xml'.format(images,GS_name))
    

    
    foilholes_dic = {}                  # {foilhole:[mdx,mdy,imx,imy]}

    sys.stdout.write('Reading foilhole metadata')
    n=0
    for FH in foilhole_metadata:
        FH_name = FH.split('/')[-1].split('.')[0]
        n+=1
        if n%10==0:
            sys.stdout.write('.')
            sys.stdout.flush()
        ABXYZ,acctime,beamshift = parse_xml_image(FH)
        FH_md_x,FH_md_y = float(ABXYZ[2]),float(ABXYZ[3])
                
        scaledx,scaledy = DA_to_SQ(FH_md_x,FH_md_y,sq_cent_x,sq_cent_y,sq_apix)
        foilholes_dic[FH_name] = [scaledx,scaledy]

        
    ##### skipping reading foil hole image headers becasure its slow and the same info is available in the xml files
    #n=0
    #sys.stdout.write('\nReading foilhole image headers')
    #for FH in foilhole_images:
    #    FH_name = FH.split('/')[-1].split('.')[0]
    #    n+=1
    #    if n%10==0:
    #        sys.stdout.write('.')
    #        sys.stdout.flush()
    #    FH_im_x,FH_im_y,FH_im_z,FH_apix,timestamp = get_image_info(FH)
    #    scaledx,scaledy = DA_to_SQ(float(FH_im_x),float(FH_im_y),sq_cent_x,sq_cent_y,sq_apix)
    #    foilholes_dic[FH_name].append(scaledx)
    #    foilholes_dic[FH_name].append(scaledy)
    #print('')
    
    FH_md_xs,FH_md_ys,FH_im_xs,FH_im_ys = [],[],[],[]    
    for hole in foilholes_dic:
        #print('{0}\t{1}\t{2}\t{3}\t{4}'.format(hole,foilholes_dic[hole][0],foilholes_dic[hole][1],foilholes_dic[hole][2],foilholes_dic[hole][3]))
    # general list of all foilhole XYs... but need to separate them into ones that were used for DA and off centre ones
        FH_md_xs.append(foilholes_dic[hole][0])
        FH_md_ys.append(foilholes_dic[hole][1])
        #FH_im_xs.append(foilholes_dic[hole][2])
        #FH_im_ys.append(foilholes_dic[hole][3])
    
    ## get the actual aquisitions for this gridsquare
    aquired = []
    DAimgs = glob.glob('{0}/{1}/Data/*.mrc'.format(images,GS_name))
    for img in DAimgs:
        if 'Fractions' in img:
            DAimgs.remove(img)
    for img in DAimgs:
        aquired.append('_'.join(img.split('/')[-1].split('_')[0:2]))
    
    ## map the aqusitions from the foilhole dict mark those used fro DA aquisitions in blue, centering iterations in yellow, skipped in red
    connect_shot_centit = {}            #{foilhole number: [[shotx,shoty],[centitrx,centity]...[centitx,centity]]}
    connect_skipped = {}                 #{foilhole number: [[shotx,shoty],[shotx,shoty]...[shotx,shoty]]}
    centitsx,centitsy,aqFHx,aqFHy,notaqFHx,notaqFHy = [],[],[],[],[],[]
    hols = list(foilholes_dic)
    hols.sort(reverse=True)
    alreadyshot = []
    for hole in hols:
        holeid= '_'.join(hole.split('_')[0:2])
        holeno = hole.split('_')[1]
        
        if holeid in alreadyshot:
            print(hole,'Centering iteration',foilholes_dic[hole][0],foilholes_dic[hole][1])
            centitsx.append(foilholes_dic[hole][0])
            centitsy.append(foilholes_dic[hole][1])
            connect_shot_centit[holeid].append([foilholes_dic[hole][0],foilholes_dic[hole][1]])
        
        elif holeid in aquired:
            print(hole,'Shot',foilholes_dic[hole][0],foilholes_dic[hole][1])
            aqFHx.append(foilholes_dic[hole][0])
            aqFHy.append(foilholes_dic[hole][1])
            alreadyshot.append(holeid)
            connect_shot_centit[holeid] = [[foilholes_dic[hole][0],foilholes_dic[hole][1]]]
            shotno = hole.split('_')[1]
            try:
                targetxy = (float(targets_dic[shotno][1]),float(targets_dic[shotno][2]))
                scaled_txy = DA_to_SQ(targetxy[0],targetxy[1],sq_cent_x,sq_cent_y,sq_apix)
                plt.scatter(float(targets_dic[shotno][4]),float(targets_dic[shotno][5]),c='red',s=1,marker='o')
                plt.text(float(targets_dic[shotno][4]),float(targets_dic[shotno][5]),shotno+'-'+str(targets_dic[shotno][0]),size=2,color='red')
            except:
                print('target match fail {0}'.format(shotno))
        else:
            print(hole,'Skipped',foilholes_dic[hole][0],foilholes_dic[hole][1])
            notaqFHx.append(foilholes_dic[hole][0])
            notaqFHy.append(foilholes_dic[hole][1])
            try:
                connect_skipped[holeid].append([foilholes_dic[hole][0],foilholes_dic[hole][1]])
            except:
                connect_skipped[holeid]=[[foilholes_dic[hole][0],foilholes_dic[hole][1]]]
    
    print('# aquisitions          : {0} '.format(len(aqFHx)))
    print('# centering iterations : {0}'.format(len(centitsx)))
    print('# centered then skipped: {0}'.format(len(notaqFHx)))
    ###make the foil hole plot
    ###plot the shots, centering iterations and misses
    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)
    plt.scatter(notaqFHx,notaqFHy,c='red',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
    plt.scatter(centitsx,centitsy,c='yellow',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
    plt.scatter(aqFHx,aqFHy,c='blue',s=20,alpha=0.3,linewidth=0.5)
    
    ### connect the dots between shots and centering iterations
    for shotit in connect_shot_centit:
        #print(shotit,connect_shot_centit[shotit])
        shotno = shotit.replace('FoilHole_','')
        zipx = [x[0] for x in connect_shot_centit[shotit]]
        zipy = [y[1] for y in connect_shot_centit[shotit]]
        plt.plot(zipx,zipy,linewidth=0.5)
        plt.text(zipx[0],zipy[0],shotno,size=2)
        
    #### connect the skipped shots 
    for shotit in connect_skipped:
        shotno = shotit.replace('FoilHole_','')
        zipx = [x[0] for x in connect_skipped[shotit]]
        zipy = [y[1] for y in connect_skipped[shotit]]
        plt.plot(zipx,zipy,linewidth=0.5)
        plt.text(zipx[0],zipy[0],shotit.replace('FoilHole_','SKIP-'),size=2)
     
     
    plt.tight_layout()
    plt.savefig('foilhole_locations_{0}.png'.format(GS_name.split('/')[-1].split('.')[0]),dpi=300)
    plt.close()
    
    #### connect the target xys with the actual 1st centering iteration stage xy
    ### use this to calculate shifts why is this happening??
    ### done ad hoc but will be useful for calculating shifts

    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)
    shiftdic,coordsx,coordsy = {},[],[]
    for shotit in connect_shot_centit:
        shotno = shotit.replace('FoilHole_','')
        tx = float(targets_dic[shotno][4])
        ty = float(targets_dic[shotno][5])
        ax = float(connect_shot_centit['FoilHole_{0}'.format(shotno)][0][0])
        ay = float(connect_shot_centit['FoilHole_{0}'.format(shotno)][0][1])
        xdif = ax-tx
        ydif = ay-ty
        shiftdic[shotno] = (xdif,ydif)
        coordsx.append(float(targets_dic[shotno][4]))
        coordsy.append(float(targets_dic[shotno][5]))
        coordsx.append(float(connect_shot_centit['FoilHole_{0}'.format(shotno)][0][0]))
        coordsy.append(float(connect_shot_centit['FoilHole_{0}'.format(shotno)][0][1]))
        plt.plot([coordsx[-1],coordsx[-2]],[coordsy[-1],coordsy[-2]],linewidth=0.5)
    
    ### for drawing this graph
    plt.scatter(coordsx,coordsy,s=2,c='red')
    plt.scatter(targetsx,targetsy,s=2,c='green')
    
    plt.tight_layout()
    plt.savefig('foilhole_shifts_{0}.png'.format(GS_name.split('/')[-1].split('.')[0]),dpi=300)
    plt.close()

# now redo it all with shifts    
## map the aqusitions from the foilhole dict mark those used fro DA aquisitions in blue, centering iterations in yellow, skipped in red
    connect_shot_centit = {}            #{foilhole number: [[shotx,shoty],[centitrx,centity]...[centitx,centity]]}
    connect_skipped = {}                 #{foilhole number: [[shotx,shoty],[shotx,shoty]...[shotx,shoty]]}
    centitsx,centitsy,aqFHx,aqFHy,notaqFHx,notaqFHy = [],[],[],[],[],[]
    hols = list(foilholes_dic)
    hols.sort(reverse=True)
    alreadyshot = []
    for hole in hols:
        holeid= '_'.join(hole.split('_')[0:2])
        holeno = hole.split('_')[1]
        shiftx = -shiftdic[holeno][0]
        shifty = -shiftdic[holeno][1]
        if holeid in alreadyshot:
            print(hole,'Centering iteration',foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty)
            centitsx.append(foilholes_dic[hole][0]+shiftx)
            centitsy.append(foilholes_dic[hole][1]+shifty)
            connect_shot_centit[holeid].append([foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty])
        
        elif holeid in aquired:
            print(hole,'Shot',foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty)
            aqFHx.append(foilholes_dic[hole][0]+shiftx)
            aqFHy.append(foilholes_dic[hole][1]+shifty)
            alreadyshot.append(holeid)
            connect_shot_centit[holeid] = [[foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty]]
            shotno = hole.split('_')[1]
            try:
                plt.scatter(float(targets_dic[shotno][4]),float(targets_dic[shotno][5]),c='red',s=1,marker='o')
                plt.text(float(targets_dic[shotno][4]),float(targets_dic[shotno][5]),shotno+'-'+str(targets_dic[shotno][0]),size=2,color='red')
            except:
                print('target match fail {0}'.format(shotno))
        else:
            print(hole,'Skipped',foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty)
            notaqFHx.append(foilholes_dic[hole][0]+shiftx)
            notaqFHy.append(foilholes_dic[hole][1]+shifty)
            try:
                connect_skipped[holeid].append([foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty])
            except:
                connect_skipped[holeid]=[[foilholes_dic[hole][0]+shiftx,foilholes_dic[hole][1]+shifty]]
    
    print('# aquisitions          : {0} '.format(len(aqFHx)))
    print('# centering iterations : {0}'.format(len(centitsx)))
    print('# centered then skipped: {0}'.format(len(notaqFHx)))
    ###make the foil hole plot
    ###plot the shots, centering iterations and misses
    sq_cent_x,sq_cent_y,sq_z,sq_apix = make_bg(GS_image)
    plt.scatter(notaqFHx,notaqFHy,c='red',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
    plt.scatter(centitsx,centitsy,c='yellow',edgecolor='black',s=20,alpha=0.3,linewidth=0.5)
    plt.scatter(aqFHx,aqFHy,c='blue',s=20,alpha=0.3,linewidth=0.5)
    
    ### connect the dots between shots and centering iterations
    for shotit in connect_shot_centit:
        #print(shotit,connect_shot_centit[shotit])
        shotno = shotit.replace('FoilHole_','')
        zipx = [x[0] for x in connect_shot_centit[shotit]]
        zipy = [y[1] for y in connect_shot_centit[shotit]]
        plt.plot(zipx,zipy,linewidth=0.5)
        plt.text(zipx[0],zipy[0],shotno,size=2)
        
    #### connect the skipped shots 
    for shotit in connect_skipped:
        shotno = shotit.replace('FoilHole_','')
        zipx = [x[0] for x in connect_skipped[shotit]]
        zipy = [y[1] for y in connect_skipped[shotit]]
        plt.plot(zipx,zipy,linewidth=0.5)
        plt.text(zipx[0],zipy[0],shotit.replace('FoilHole_','SKIP-'),size=2)
     
     
    plt.tight_layout()
    plt.savefig('foilhole_locations_shifted_{0}.png'.format(GS_name.split('/')[-1].split('.')[0]),dpi=300)
    plt.close()    



