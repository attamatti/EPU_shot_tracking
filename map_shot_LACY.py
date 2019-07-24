#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import mrcfile
import glob


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
    
def get_DA_level_stats(DA_image):
    '''for a DA level image read it and return x,y,z,nominalDF'''
    micdata = mrcfile.open(DA_image)
    mic_ed = micdata.extended_header
    sq_cent_x,sq_cent_y,sq_z,sq_apix,timestamp = (mic_ed[0][12],mic_ed[0][13],mic_ed[0][14],mic_ed[0][17],mic_ed[0][3])
    return(sq_cent_x,sq_cent_y,sq_z,sq_apix,timestamp)

def get_image_part_stats(image,ctfstarfile):
    '''for an image get the number of particles picked, used, and calculate DF for that image'''

def DA_to_SQ(dax,day,sqx,sqy,sqapix):
    newx = dax-sqx    
    newy = day-sqy
    print(2048+(newx/sqapix),2048-(newy/sqapix))
    return(2048+(newx/sqapix),2048-(newy/sqapix))

#Get the grid square images
GS = glob.glob('{0}Grid*.mrc'.format(sys.argv[1]))
mainsq = sys.argv[1].split('/')[-2]
print('{0}Grid*.mrc'.format(sys.argv[1]))
if len(GS)> 1:
    GS = GS.sort()
if GS == None:
    sys.exit('no gridsquare images')
name = GS[-1].split('/')[-1].replace('.mrc','')
SQ_x,SQ_y,SQ_z,SQ_apix = (make_bg(GS[-1]))

#read DA files
DA_files = glob.glob('{0}Data/FoilHole*.mrc'.format(sys.argv[1]))
print DA_files
daxs,days,timestamps = [],[],[]
for i in DA_files:
    if '_Fractions' not in i:
        DA_x,DA_y,DA_z,DA_apix,timestamp = get_DA_level_stats(i)
        newpoint = DA_to_SQ(DA_x,DA_y,SQ_x,SQ_y,SQ_apix)
        daxs.append(newpoint[0])
        days.append(newpoint[1])
        timestamps.append(timestamp)

# plot the actual aquisitions on the image    
plt.scatter(daxs,days,c=timestamps,edgecolors='k',linewidths=0.5,alpha = 0.4,s=80,cmap='gist_rainbow')
color_bar = plt.colorbar(ticks = [])
color_bar.set_alpha(1)
color_bar.draw_all()
plt.title('aquisition order')

plt.tight_layout()
plt.savefig('{1}_{0}_OA.png'.format(name,mainsq),dpi=300)

plt.close()