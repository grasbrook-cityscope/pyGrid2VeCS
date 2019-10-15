import json
import urllib.request 

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
        return ret



if __name__ == "__main__":
    data = getCurrentState()
    if not data:
        print("couldn't load input_url!")
        exit()

    gridDef = Grid.fromCityIO(data)
    gridData = data["grid"]

    if gridData:
        print("got grid")

