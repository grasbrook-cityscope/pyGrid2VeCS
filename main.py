import json
import math
import urllib.request 
from pyproj import Transformer

def getFromCfg(key : str) -> str:
    #import os#os.path.dirname(os.path.realpath(__file__)+
    with open("config.json") as file:
        js = json.load(file)
        return js[key]

def getCurrentState():
    with urllib.request.urlopen(getFromCfg("input_url")) as url:
        return json.loads(url.read().decode())
    return None

class Grid:
    cellSize = 0
    ncols = 0
    nrows = 0

    @staticmethod
    def fromCityIO(data):
        ret = Grid()
        ret.cellSize = data["header"]["spatial"]["cellSize"]
        ret.ncols = data["header"]["spatial"]["ncols"]
        ret.nrows = data["header"]["spatial"]["nrows"]
        ret.mapping = data["header"]["mapping"]["type"]
        ret.tablerotation = data["header"]["spatial"]["rotation"]

        proj = Transformer.from_crs(4326, 32632)

        utm_origin = proj.transform(data["header"]["spatial"]["latitude"], data["header"]["spatial"]["longitude"])
        print(utm_origin)

        ret.origin = utm_origin
        return ret


    def RoadAt(self, typejs, x, y):
        cell = gridData[x + y * self.ncols]
        return self.mapping[cell[1]] in typejs["type"]

    def Local2Geo(self, x, y):
        bearing = self.tablerotation

        # rotate and scale
        new_x = x * self.cellSize * math.cos(math.radians(bearing)) - y * self.cellSize * math.sin(math.radians(bearing))
        new_y = x * self.cellSize * math.sin(math.radians(bearing)) + y * self.cellSize * math.cos(math.radians(bearing))

        # convert to geo coords
        return (new_x + self.origin[0], new_y + self.origin[1])

def PointToGeoJSON(lat, lon, id, properties):
    ret = "{\"type\": \"Feature\",\"id\": \"" 
    ret += str(id) 
    ret += "\",\"geometry\": {\"type\": \"Point\",\"coordinates\": ["

    ret += str(lat)
    ret += ","
    ret += str(lon)

    ret += "]},"
    ret += "\"properties\": "
    ret += str(properties)
    ret += "}"
    return ret

def LineToGeoJSON(fromPoint, toPoint, id, properties):
    ret = "{\"type\": \"Feature\",\"id\": \"" 
    ret += str(id) 
    ret += "\",\"geometry\": {\"type\": \"LineString\",\"coordinates\": [["

    ret += str(fromPoint[0])
    ret += ","
    ret += str(fromPoint[1])

    ret += "],["

    ret += str(toPoint[0])
    ret += ","
    ret += str(toPoint[1])

    ret += "]]},"
    ret += "\"properties\": "
    ret += str(properties)
    ret += "}"
    return ret

def PolyToGeoJSON(self, points, id, properties):
    ret = "{\"type\": \"Feature\",\"id\": \"" 
    ret += str(id) 
    ret += "\",\"geometry\": {\"type\": \"Polygon\",\"coordinates\": [["

    for p in points:
        ret+="["+str(p[0])+","+str(p[1])+"],"
    ret+="["+str(points[0][0])+","+str(points[0][1])+"]" # closed ring, last one without trailing comma

    ret += "]]},"
    ret += "\"properties\": "
    ret += str(properties)
    ret += "}"
    return ret

def writePointsToFile(points):
        ret = "{\"type\": \"FeatureCollection\",\"features\": ["
        for feature in points[:-1]:
            ret += feature.toGeoJSON() + ","
        if len(points) > 0:
            ret += points[-1].toGeoJSON() # last one without trailing comma
        
        ret+= "]}"
        return ret

def writeFile(filepath, data):
    f= open(filepath,"w+")
    f.write(data)


if __name__ == "__main__":
    data = getCurrentState()
    if not data:
        print("couldn't load input_url!")
        exit()

    gridDef = Grid.fromCityIO(data)
    gridData = data["grid"]

    if gridData:
        print(data["header"]["spatial"])

    typejs = {}
    with open("typedefs.json") as file:
        typejs = json.load(file)

    mapping = data["header"]["mapping"]["type"]
    print(mapping)


    ret = "{\"type\": \"FeatureCollection\",\"features\": ["

    idit = 0

    # find all grid cells with type as in typejs
    for idx in range(len(gridData)):
        x = idx % gridDef.ncols
        y = idx // gridDef.ncols
        cell = gridData[idx]

        print(x,y,":",mapping[cell[1]])

        print(gridDef.RoadAt(typejs,x,y))

        if x >= gridDef.ncols-1:    # don't consider last row
            continue
        if y >= gridDef.nrows-1:    # don't consider last column
            break

        if gridDef.RoadAt(typejs,x,y):  # a road starts here
            if gridDef.RoadAt(typejs, x+1, y): # a road goes to the right
                fromPoint = gridDef.Local2Geo(x,y)
                toPoint = gridDef.Local2Geo(x+1,y)
                ret += LineToGeoJSON(fromPoint, toPoint, idit, [])
                ret +=","

                idit+=1

            if gridDef.RoadAt(typejs, x, y+1): # a road goes down
                fromPoint = gridDef.Local2Geo(x,y)
                toPoint = gridDef.Local2Geo(x,y+1)
                ret += LineToGeoJSON(fromPoint, toPoint, idit, [])
                ret +=","

                idit+=1

            

    ret = ret[:-1]
    ret+= "]}"

    # print(ret)
    writeFile("output.geojson", ret)

    # Also post result to cityIO
    post_address = getFromCfg("output_url")
    print(post_address)
    data= json.loads(ret)
    print(type(data))

    import requests

    r = requests.post(post_address, json=data, headers={'Content-Type': 'application/json'})
    print(r)
    if not r.status_code == 200:
        print("could not post result to cityIO")
        print("Error code", r.status_code)
    else:
        print("Successfully posted to cityIO", r.status_code)

    # r = urllib.request.Request(post_address, data, {'Content-Type': 'application/json'})
    # resp = urllib.request.urlopen(r)
    # print(resp)

    # if not resp == 200:
    #     print("could not post result to cityIO")
    #     print("Error code", resp)
    # else:
    #     print("Successfully posted to cityIO", resp)

    
