#!/usr/bin/env python

# MRC file read FEI extended header

import sys
import mrcfile
import numpy as np

themrc = mrcfile.open(sys.argv[1],permissive=True)

e_head = themrc.extended_header

basic = ('metadata_size','metadata_version')
bitmask1 = {3:'timestamp',
            4:'microscope_type',
            5:'D_number',
            6:'application',
            7:'application_version',
            8:'gun_HT',
            9:'gun_dose',
            10:'stage_a_tilt',
            11:'stage_b_tilt',
            12:'stage_x',
            13:'stage_y',
            14:'stage_z',
            15:'stage_tilt_axis_angle',
            16:'stage_dual_axis_rotation',
            17:'pixel_size_x',
            18:'pixel_size_y',
            20:'defocus',
            21:'STEM_defocus',
            22:'applied_defocus',
            23:'instrument_mode',
            24:'projection_mode',
            25:'obj_lens_mode',
            26:'high_mag_mode',
            27:'probe_mode',
            28:'EFTEM_on',
            29:'magnification'}


BM1 = list(bitmask1)
BM1.sort()
print e_head
print('%% BITMASK1 %%')
for i in BM1:
    if i <=18:
        print('{0:02d} {1} {2}'.format(i-3,bitmask1[i],e_head[0][i]))
    else:
        print('{0:02d} {1} {2}'.format(i+2,bitmask1[i],e_head[0][i]))

    
bitmask2 = {31:'camera_length',
            32:'spot_index',
            33:'illuminated_area',
            34:'intensity',
            35:'convergence_angle',
            36:'illumination_mode',
            37:'wide_convergence_angle_range',
            38:'slit_inserted',
            39:'slit_width',
            40:'acc_voltage_offset',
            41:'drift_tube_voltage',
            42:'energy_shift',
            43:'image_shift_x',
            44:'image_shift_y',
            45:'beam_shift_x',
            46:'beam_shift_y,',
            47:'integration_time',
            48:'binning_width',
            49:'binning_height',
            50:'camera_name',
            51:'readout_area_left',
            52:'readout_area_top',
            53:'readout_area_right',
            54:'readout_area_bottom',
            55:'ceta_noise_reduction',
            56:'ceta_frames_summed',
            57:'DD_electron_counting',
            58:'DD_align_frames',
            59:'camera_param_res_0',
            60:'camera_param_res_1',
            61:'camera_param_res_2',
            62:'camera_param_res_3'
}

print('\n%% BITMASK2 %%')
BM2 = list(bitmask2)
BM2.sort()
for i in BM2:
    print('{0:02d} {1} {2}'.format(i-31,bitmask2[i],e_head[0][i]))
