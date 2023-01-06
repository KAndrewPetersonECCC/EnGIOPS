test_polygon = [[0, 0], [1, 0], [1, 1], [0, 1], [0,0] ]

open_polygon = [[0, 0], [1, 0], [1, 1], [0, 1]]

test_points = [ [0, 0.5], [0.5, 0.5], [2,0], [1, 1] ]

import matplotlib.path as path
from shapely import geometry 

def test_inside_path(polygon, points, closed=True):
    Ppolygon = path.Path(polygon, closed=closed)
    Inside = Ppolygon.contains_points(points)
    return Inside
    
def test_inside_shapely(polygon, points):
    # Inside is inside the polygon.
    # In(ter)sect(s) is inside or on the polygon.
    Inside = []
    Insect = []
    for point in points:
        insect, inside = test_inside_single(polygon, point)
        Spoint = geometry.Point(point[0], point[1])
        Insect.append(insect)
        Inside.append(inside)
    return Insect, Inside

def test_inside_xyarray(polygon, xarray, yarray):
    # Inside is inside the polygon.
    # In(ter)sect(s) is inside or on the polygon.
    Inside = []
    Insect = []
    npts=len(xarray)
    mpts=len(yarray)
    if ( npts != mpts ):  return None
    for ipt in range(npts):
        point = [xarray[ipt], yarray[ipt]]
        insect, inside = test_inside_single(polygon, point)
        Spoint = geometry.Point(point[0], point[1])
        Insect.append(insect)
        Inside.append(inside)
    return Insect, Inside

def test_inside_single(polygon, point):
    line = geometry.LineString(polygon)
    Spolygon = geometry.Polygon(line)
    # Inside is inside the polygon.
    # In(ter)sect(s) is inside or on the polygon.
    Spoint = geometry.Point(point[0], point[1])
    insect = Spolygon.intersects(Spoint)
    inside = Spolygon.contains(Spoint)
    return insect, inside
        
