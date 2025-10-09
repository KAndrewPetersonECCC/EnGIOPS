import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
reload(ola_functions)
import ola_functions
input_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX355Hz/SAM2//20240904/DIA/2024090400_SAM.ola"
in1Hz_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX351Hz/SAM2//20240904/DIA/2024090400_SAM.ola"
in5Hz_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX355Hz/SAM2//20240904/DIA/2024090400_SAM.ola"

from importlib import reload
import sys
sys.path.insert(0, '/home/dpe000/EnGIOPS/python')
reload(ola_functions)
import ola_functions
input_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX355Hz/SAM2//20240904/DIA/2024090400_SAM.ola"
in1Hz_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX351Hz/SAM2//20240904/DIA/2024090400_SAM.ola"
in5Hz_file = "/fs/site5/eccc/cmd/e/kch001/maestro_archives/rel-3.5.0/tests_superOb/GX355Hz/SAM2//20240904/DIA/2024090400_SAM.ola"

ola_functions.read_data(in1Hz_file, 'IS')
ola_functions.read_data(in5Hz_file, 'IS')

import struct
import os

def cycle_through_file(file):
    with open(file, 'rb') as fid:
        while ( 0 == 0 ):
            len_bgn = struct.unpack(">I", fid.read(4))[0]
            len_end =  0
            len_bet = -4
            while ( len_end != len_bgn ):
               len_end = struct.unpack(">I", fid.read(4))[0]
               len_bet = len_bet + 4
            print(len_bgn, len_end, len_bet)
    return
