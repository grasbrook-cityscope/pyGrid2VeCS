# pyStoCS
## The python storm water calculation module for CityScopes

Input: CityIO-compatible grid, stormwater event
Output: Amount of retained/drained white-/graywater

### Installation

Requires
* python3


### Usage

```python main.py```


### Description

Rainwater is distributed uniformly across all surface areas.
Rainwater that is collected on street surfaces will have to be treated before disposal.
Rainwater collected from roofs can be disposed of untreated (white water) or reused for flushing toilets etc (turns into black water, but dropped out of calculation because it is there anyway).
Rainwater infiltration vanishes untreated :)

Calculates:
* m³ of white water that needs to be disposed of (after retention and reuse)
* m³ of gray water to be disposed of