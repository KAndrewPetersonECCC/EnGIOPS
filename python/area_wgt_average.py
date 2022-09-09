import numpy as np
import read_grid

lonn, latn, orca_area = read_grid.read_coord()

def area_wgt_average( FLD, area=orca_area, integral=False, return_area=False):
   awgt_FLD = FLD * area
   SUM_FLD = np.sum(awgt_FLD)
   SUM_AREA = np.sum(area)
   if ( integral == False ):
       if ( SUM_AREA != 0 ):
           area_wgt_mean = SUM_FLD / SUM_AREA
       else:
           area_wgt_mean = 0
   else:
       area_wgt_mean = SUM_FLD	
   if ( return_area ):    
       return area_wgt_mean, SUM_AREA
   else:
       return area_wgt_mean
   
