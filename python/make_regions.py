
AREAS = { 
          'NINO34' : [ -170, -120,  -5,   5 ],
          'NINO12' : [  -90,  -80,  -10,   0 ],
          'NTrPac' : [  160,  -100,   8,  20 ],
          'STrPac' : [  160,   -90, -20,  -8 ],
          'SPacGyre' : [-179,  -90, -45, -20 ],
          'CalCurnt' : [-125, -100,  20,  40 ],
          'NPacDrft' : [ 160, -120,  45,  65 ],
          'Tropics' : [ -180,  180, -20,  20 ],
          'North40' : [ -180,  180,  40,  90 ],
          'South40' : [ -180,  180, -90, -40 ],
          'North60' : [ -180,  180,  60,  90 ],
          'NordAtl' : [ - 90,   15,  30,  65 ],
          'Pirata' : [  -40,  -30, -2.5, 2.5 ],
          'GMexico': [  -89,  -85,   24,  28 ],
          'FLStrt' : [  -81,  -75,   24,  28 ],
          'GlfSt1' : [  -70,  -62,   36,  40 ],
          'GlfSt2' : [  -62,  -45,   38,  42 ],
          'NFIS'   : [  -48,  -37,   45,  55 ],
          'ACC'    : [ -180,  180,  -90, -45 ]
        }
        
def make_poly_from_box( box ):
    X0 = box[0]
    X1 = box[1]
    Y0 = box[2]
    Y1 = box[3]
    polygon = [ [X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1], [X0, Y0] ]
    return polygon

# Defined
# /home/dpe000/data/ppp5/ORDS/GITHUB/giops/GIOPS_RIOPS_sam2_coolskin/src/ROA_ITF/mod_domain.F90
# /home/kch001/scripts/SAM2_diagnostics/GIOPS/constants/GIOPS_regions    
PAREAS = { 'NINO34' : make_poly_from_box( AREAS['NINO34'] ),
           'NINO12' : make_poly_from_box( AREAS['NINO12'] ),
           'SPacGyre' : make_poly_from_box( AREAS['SPacGyre']),
           'CalCurnt' : make_poly_from_box( AREAS['CalCurnt']),
           'Tropics' : make_poly_from_box( AREAS['Tropics'] ),
           'NordAtl' : make_poly_from_box( AREAS['NordAtl'] ),
           'Pirata'  :  make_poly_from_box( AREAS['Pirata'] ),
           'GlfSt1'  : make_poly_from_box( AREAS['GlfSt1'] ),
           'GlfSt2'  : make_poly_from_box( AREAS['GlfSt2'] ),
           'NFIS'    : make_poly_from_box( AREAS['NFIS'] ),
           'NPacGyre' : [[130.,20.], [160.,45.], [240.,45.], [240.,20.], [130.0, 20.0]],
           'ISBsn'    : [[-35.,55.],[-25.,62.],[-10.,62.],[-10.,55],[-35.,55.]],
           'ACC'      : make_poly_from_box( AREAS['ACC'] ),
           'North60'  : make_poly_from_box( AREAS['North60'] ),
         }
         
   
