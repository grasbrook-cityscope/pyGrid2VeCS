# pyGrid2VeCS
## The python Grid to Vector conversion tool for road networks

Input: CityIO-compatible grid

Output: GeoJSON containing connected road topology

### Installation

Requires
* python3


### Usage

```python main.py```


### Description

Reads grid from CityIO (define table-URL in config.json) and parses all cells with types as in typedef.json.
Stores and posts (define output URL in config.json) LineString Collection of road segments to CityIO.

### Open Questions
* connect 4-neighbourhoods only or also 8-neighbourhoods?