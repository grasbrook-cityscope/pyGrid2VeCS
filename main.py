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

        proj = Transformer.from_crs(getFromCfg("input_crs"), getFromCfg("output_crs"))
        ret.origin = proj.transform(data["header"]["spatial"]["latitude"], data["header"]["spatial"]["longitude"])

        return ret

    def RoadAt(self, typejs, x, y):
        cell = gridData[x + y * self.ncols]
        return self.mapping[cell[1]] in typejs["type"]

    def Local2Geo(self, x, y):
        bearing = self.tablerotation

        x += 0.5 # connect midpoints
        y += 0.5

        x *= self.cellSize
        y *= -self.cellSize # flip y axis (for northern hemisphere)

        # rotate and scale
        new_x = x * math.cos(math.radians(bearing)) - y * math.sin(math.radians(bearing))
        new_y = x * math.sin(math.radians(bearing)) + y * math.cos(math.radians(bearing))

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
        print("got grid:", data["header"]["spatial"])

    typejs = {}
    with open("typedefs.json") as file:
        typejs = json.load(file)

    ret = "{\"type\": \"FeatureCollection\",\"features\": [" # geojson front matter

    idit = 0

    # find all grid cells with type as in typejs
    for idx in range(len(gridData)):
        x = idx % gridDef.ncols
        y = idx // gridDef.ncols
        cell = gridData[idx]    # content of current cell

        if x >= gridDef.ncols-1:    # don't consider last row
            continue
        if y >= gridDef.nrows-1:    # don't consider last column
            break

        if gridDef.RoadAt(typejs,x,y):  # a road starts here
            if gridDef.RoadAt(typejs, x+1, y): # a road goes to the right
                fromPoint = gridDef.Local2Geo(x,y)
                toPoint = gridDef.Local2Geo(x+1,y)
                ret += LineToGeoJSON(fromPoint, toPoint, idit, []) # append feature
                ret +=","

                idit+=1

            if gridDef.RoadAt(typejs, x, y+1): # a road goes down
                fromPoint = gridDef.Local2Geo(x,y)
                toPoint = gridDef.Local2Geo(x,y+1)
                ret += LineToGeoJSON(fromPoint, toPoint, idit, []) # append feature
                ret +=","

                idit+=1

    ret = ret[:-1] # trim trailing comma
    ret+= "]}" # geojson end matter

    writeFile("output.geojson", ret)

    # Also post result to cityIO
    post_address = getFromCfg("output_url")
    data= json.loads(ret)

    import requests
    r = requests.post(post_address, json=data, headers={'Content-Type': 'application/json'})
    print(r)
    if not r.status_code == 200:
        print("could not post result to cityIO")
        print("Error code", r.status_code)
    else:
        print("Successfully posted to cityIO", r.status_code)


    
