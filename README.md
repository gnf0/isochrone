# Isochrone Map Generation

### iso (ἴσος) = “equal" / "same”

### chrone (χρόνος) = “time”

<div style="text-align:center; justify-content:center;">
  <img src="photos/example_isochrone_generation.png"
       style="object-fit:contain;">
  <div style="margin-top:8px; font-size:14px; color:#555;">
    <i>An Isochrone Map of the United States. Isochrones here use Los Angeles, CA as an origin point and show road driving increments of 500 miles.</i>
  </div>
</div>
<br>

An **Isochrone Map** is a visualization displaying the geographic area reachable within a specified time or distance. Real-world data such as road networks, traffic, and public transport schedules are used to map true accessibility (e.g., a 30-minute commute or 2‑day delivery).

---

This tool can be used to create <u>continental scale</u> Isochrones with higher <u>precision</u> and <u>resolution</u> than existing resources available online. Methods used here uniquely allow for simulation and analysis of *Over The Road* (OTR) transportation where service is generally provided at a standard distance per day (e.g., 500 or 1000 miles).

### What makes the methods used here unique?

- Scale to continent size
- Maintain high precision and resolution
- Not based on a specific carrier's geographic service area
- Not based on historical transit data

### Benefits of these methods

- Ability to generate isochrones for any given city within the continental United States  
- Specify isochrone distance (miles per day)  
- Not based on historical transit data — can plot a proposed or potential origin
- No Google Maps API or other paid resources required  
- No creation or maintenance of a large "Origin / Destination pairing table" required 
- Interactive map (zoom and add other elements)

## Quick Start

1. `pip install -r requirements.txt`
2. Set up a PostGIS database (PostgreSQL + PostGIS + pgrouting + hstore). (Full US OSM data = ~150GB, loading can take days.)
3. Download US OSM data: https://download.geofabrik.de (North America → United States, ~11GB)
4. Load with `osm2pgsql` (see online guides for details)
5. Add a `config.py` file with your database connection info:

   ```python
   DATABASE_URL = "postgresql+psycopg2://postgres:password@192.168.0.123:5432/osm_routing"
   ```

6. Open notebook `isochrone.ipynb` and Run All)

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/osm_data_example_points.png" style="max-width:50%;">
  <!-- <img src="photos/osm_data_example_geometries_lines.png" style="max-width:50%;"> -->
</div>
<br>

## Methods & Considerations

Generally, the methods used here can be summarized into the following steps

### These steps are run once, "precomputed"
1. Divide a given geographic area (Continental United States) into even-sized areas - <u>Cells</u>
2. Identify a <u>road point</u> inside each <u>cell</u>
3. For each <u>cell's</u> <u>road point</u>, measure & log the transit distance to each neighboring <u>cell's</u> <u>road point</u> - <u>Cell Traversal Log</u>


### These steps are run each time an isochrone map is generated. For a given Isochrone origin & Isochrone increment:
1. Identify which <u>cell</u> contains the <u>origin</u>
2. Use the <u>Cell Traversal Log</u> to find travel distance from the origin cell across all cells in the given geographic area 
3. Group <u>Cells</u> by their <u>Isochrone increment</u> (if the <u>isochrone increment</u> is 500 miles, all cells with a transit distance of 0-499 miles from the origin cell are grouped together, same for all cells at 500-999 miles, etc.)
4. Convert each <u>cell group</u> into <u>Polygons</u>
5. Plot the <u>polygons</u> on a <u>map</u>


### Cells: H3 Hexagons

To cover a geographic area in relatively even-sized cells, a polygon that tiles regularly should be used. Only 3 polygons tile regularly: Triangles, Hexagons & Squares.

A polygon tiles regularly if there are
- No gaps
- No overlaps
- Identical orientation at every vertex (same angle pattern everywhere)

| Hexagon ✅ | Triangle ❌ | Square ❌ |
|----------|---------|----------|
| ![](photos/neighbors-hexagon.png) | ![](photos/neighbors-triangle.png) | ![](photos/neighbors-square.png) |
| Hexagons have 6 *equidistant* neighbors | Triangles have 12 neighbors at 3 unique distances | Squares have 8 neighbors at 2 unique distances |

Because hexagons have the fewest neighbors & only have equidistant neighbors, hexagons allow for the simplest analysis of 2D movement. Hexagons also look the best.

### Identifying Road Snapped Points

In each Hexagon, "Road Snapped Points" are identified (green dots). When selecting a road snapped point, priority is given to points close to the center of the cell (red dots). There is also some preference given to major highways over side roads and neighborhood roads.

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/road_snapped_point_vegas_big_dots.png" style= object-fit:contain;">
</div>

### Cell to Cell Transit

Once the distance from road snapped point to neighboring road snapped point has been found for all cells, Dijkstra's Algorithm can be used to find the shortest path from an origin cell to all other cells.

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/Dijkstra_Animation.gif" style= object-fit:contain;">
</div>

## Appendix

### Exploring Existing Applications & Methods

Isochrone maps are most often created for short transit distances, typically intercity transit applications such as city planning, Uber, Zillow, and public transit.

#### Uber – San Francisco 

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/h3_sanfran_iso.png" style="object-fit:contain;">
  <!-- <img src="photos/Uber_Bangalore_isochrone.png" style="height:500px; object-fit:contain;"> -->
</div>

##### Application

- Is there an available driver within 5 minutes of a user?
- Where can a driver travel within 5 min?

#### Zillow - Beaverton


<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/zillow_map.png" style="object-fit:contain;">
</div>

##### Application

- Users can filter listings based on commute distance

#### Public Transit – London (The Tube)

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/london_public_transit_iso copy.png" style="height:auto; object-fit:contain;">
</div>

##### Application

- City planners can identify gaps in accessibility of public transit

Note: Precise subway isochrones often show “islands” of accessibility as underground travel can be used to reach isolated pockets that are farther from the origin than geographically closer but unreachable areas (e.g., Hampstead is farther from central London than the London Zoo but can be reached sooner by public transit).

#### Supply Chain Final Mile Delivery - United States

Isochrones can also be generated for greater distances (often with less precision)

<div style="display:flex; gap:2px; justify-content:center;">
  <!-- <img src="photos/simple_conus_isochrone.png" style="max-width:47%; height:auto; object-fit:contain;"> -->
  <img src="photos/Pixilated_UPS_Ground_Transit_Time_Shipping_Map-01_1024x1024.webp" style=height:auto; object-fit:contain;">
  <!-- <img src="photos/fedex-shipping-map-72034.jpg" style="max-width:38%; height:auto; object-fit:contain;"> -->
</div>
<div style="text-align:center; font-weight:300; margin-bottom:6px;">
  <!-- Precision/Resolution: Low to High -->
</div>

Isochrone lines landing exactly on state borders indicate these isochrones were likely created using estimates or are based on specific third‑party service areas which often extend exactly to state borders or other arbitrary boundaries (FedEx/UPS)

### Limitations of Existing Methods

#### Scaling to continental size

Current methods used to generate isochrones for intercity transit are too resource intensive to scale to continental size. Isochrone generation tools available online usually allow isochrones up to 60 min (3 hours max). Current methods to generate larger isochrones rely on specific carriers' geographical service areas and/or historical transportation data. These methods are not well suited for simulating large-scale logistics networks or testing hypothetical isochrone origin locations. Current methods must trade precision & resolution for larger geographic scale.

<div style="display:flex; gap:5px;justify-content:center;">
  <img src="photos/res_vs_scale.png" style="height:400; object-fit:contain;">
</div>
