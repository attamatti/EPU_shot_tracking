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
    sq_cent_x,sq_cent_y,sq_z,sq_apix,DF = (mic_ed[0][12],mic_ed[0][13],mic_ed[0][14],mic_ed[0][17],mic_ed[0][20])
    return(sq_cent_x,sq_cent_y,sq_z,sq_apix,DF)

def get_image_part_stats(image,ctfstarfile):
    '''for an image get the number of particles picked, used, and calculate DF for that image'''

def DA_to_SQ(dax,day,sqx,sqy,sqapix):
    newx = dax-sqx
    newy = day-sqy
    print(2048+(newx/sqapix),2048-(newy/sqapix))
    return(2048+(newx/sqapix),2048-(newy/sqapix))



# make BG
SQ_x,SQ_y,SQ_z,SQ_apix = (make_bg(sys.argv[1]))

#read DA files
DA_files = glob.glob('Data/FoilHole*.mrc')
print DA_files
daxs,days,defoci = [],[],[]
for i in DA_files:
    DA_x,DA_y,DA_z,DA_apix,DA_DF = get_DA_level_stats(i)
    newpoint = DA_to_SQ(DA_x,DA_y,SQ_x,SQ_y,SQ_apix)
    daxs.append(newpoint[0])
    days.append(newpoint[1])
    defoci.append(DA_DF*1000000)
    
plt.scatter(daxs,days,c=defoci,alpha = 0.5,s=80,cmap='seismic')
color_bar = plt.colorbar()
color_bar.set_alpha(1)
color_bar.draw_all()
plt.title('grid distance from eucentric focus (um)')

plt.tight_layout()
plt.show() 