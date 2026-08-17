# Isochrone Generation for Simulation of Over The Road Transportation Networks

**iso (ἴσος) = “equal"**

**chrone (χρόνος) = “time”**




<div align="left">
  <img src="photos/example_isochrone_generation.png">
  <p>
    <i>Example Output: An Isochrone Map of the United States. Isochrones here use Los Angeles, CA as an origin point and show road driving increments of 500 miles.</i>
  </p>
</div>
<br>

An **Isochrone Map** simulates geographic areas reachable within a specified time or distance. Real-world data such as road networks and/or traffic are used to map true accessibility (e.g., a 30-minute commute or 2‑day transit).

---

This tool can be used to create **continental-scale** isochrones with high **precision** and **resolution**. The methods used here uniquely allow for simulation and analysis of *Over The Road* (OTR) transportation, where service is generally provided at a standard distance per day (e.g., 500 or 1000 miles).

-### What makes the methods used here unique?

- Continental scale
- High precision
- Based on actual road distance (not on historical transit data or a specific carrier's geographic service areas)

### Benefits of these methods

- Ability to vary origin location and isochrone distance (miles per day)
- No Google Maps API or other paid services — all dependencies are free and open source.  
- Isochrones can be used instead of an "Origin / Destination pairing table" in many applications. Alternatively, isochrones can help with maintenance of these tables.
- Extensibility: The map & underlying data can be enhanced and contextualized with other supply chain data & visuals.

#### *Jump to Bottom for Quick Start*

___

## Methods & Considerations

Generally, the methods used here can be summarized into 3 steps.


### Step 1 - Divide a given geographic area into even-sized cells (h3 Hexagons)

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/resolution 3 example.png" style= object-fit:contain;">
</div>

#### Hexagons simplify analysis of 2D movement

To cover a geographic area in even-sized cells, a polygon that tiles regularly should be used (no gaps, no overlaps, identical orientation at each vertex).

| Hexagon ✅ | Triangle ❌ | Square ❌ |
|----------|---------|----------|
| ![](photos/neighbors-hexagon.png) | ![](photos/neighbors-triangle.png) | ![](photos/neighbors-square.png) |
| Hexagons have 6 *equidistant* neighbors | Triangles have 12 neighbors at 3 unique distances | Squares have 8 neighbors at 2 unique distances |



### Step 2 - Identify a Road Point inside each cell


<div align="left">
  <img src="photos/road_snapped_points_example_res4.png" alt="Road-snapped points example">

  <p>
    <i>
      Green: Valid Road-Snapped Point (road point is within cell)<br>
      Red: Invalid Road-Snapped Point (road point falls outside cell)
    </i>
  </p>
</div>

When selecting a road-snapped point, priority is given to points close to the center of the cell. There is also some preference given to major highways over side roads and neighborhood roads. 

*"Road snapping" can also be configured to include or exclude railways and waterways.*

#### Road point identification is enabled by a GIS database.
<div align="left">
  <img src="photos/database_ploted_example.png">
  <p>
    <i> Example rendering of data contained in a PostGIS database.</i>
  </p>
</div>
<br>


### Step 3 - Cell to Cell Transit

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/cell_labels_los_angles.png" style="object-fit:contain;">
</div>

<br>

Once the distance from each road-snapped point to neighboring road-snapped points has been calculated for all cells, Dijkstra's algorithm is used to find the shortest paths from an origin cell to all other cells.

<div style="display:flex; gap:5px;">
  <img src="photos/Dijkstra_Animation.gif" style="object-fit:contain;">
</div>



#### Cells Grouped Based on Distance from Origin

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/isochrone_res_4_dark_denver_example.png" style= object-fit:contain;">
</div>

This map and the underlying data create a single framework that can be used to analyze

1. Current state 
2. Historical data
3. Forecasts and Simulations  

The ability to change isochrone distance (miles per day) and resolution (cell size) remains consistent across all uses.

## Appendix

### Exploring Existing Isochrone Applications & Methods

Isochrone maps are most often created for short transit distances, typically for intercity transit applications such as city planning, Uber, Zillow, and public transit.

#### Uber – San Francisco 

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/h3_sanfran_iso.png" style="object-fit:contain;">
  <!-- <img src="photos/Uber_Bangalore_isochrone.png" style="height:500px; object-fit:contain;"> -->
</div>

##### Application

- Is there an available driver within 5 minutes of a user?
- Where can a driver travel within 5 minutes?

Determining whether a user falls within a precomputed area is much easier than finding the distance to the nearest driver.

#### Zillow - Beaverton


<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/zillow_map.png" style="object-fit:contain;">
</div>

##### Application

- Users can filter listings based on commute distance

#### Public Transit – London (The Tube)

<div style="display:flex; gap:5px; justify-content:center;">
  <img src="photos/london_public_transit_iso.png" style="height:auto; object-fit:contain;">
</div>
Source: traveltime.com

##### Application

- City planners can identify gaps in accessibility of public transit

Note: Precise subway isochrones often show “islands” of accessibility, as underground travel can be used to reach isolated pockets that are farther from the origin than geographically closer but unreachable areas (e.g., Hampstead is farther from central London than the London Zoo but can be reached sooner by public transit).

#### Supply Chain Final Mile Delivery - United States

Isochrones can also be generated for greater distances (often with less precision).

<div style="display:flex; gap:2px; justify-content:center;">
  <img src="photos/simple_conus_isochrone.png" style="height:350; object-fit:contain;">
  <img src="photos/Pixilated_UPS_Ground_Transit_Time_Shipping_Map-01_1024x1024.webp" style=height:350; object-fit:contain;">
  <!-- <img src="photos/fedex-shipping-map-72034.jpg" style="max-width:38%; height:auto; object-fit:contain;"> -->
</div>
<div style="text-align:center; font-weight:300; margin-bottom:6px;">
  <!-- Precision/Resolution: Low to High -->
</div>

Isochrone lines landing exactly on state borders indicate these isochrones were likely created using estimates or are based on specific third‑party service areas, which often extend exactly to state borders and other arbitrary boundaries (FedEx/UPS).

### Limitations of Existing Methods

#### Scaling to continental size

Current methods used to generate isochrones for intercity transit are too resource-intensive to scale to continental size. Isochrone generation tools available online usually allow isochrones representing driving distances up to 60 minutes (3 hours max). Current methods to generate larger isochrones rely on specific carriers' geographical service areas and/or historical transportation data. These methods are not well suited for simulating large-scale logistics networks or testing hypothetical isochrone origin locations. Current methods must trade precision and resolution for larger geographic scale.

<div style="display:flex; gap:5px;justify-content:center;">
  <img src="photos/res_vs_scale.png" style="object-fit:contain;">
</div>

## Quick Start

1. `pip install -r requirements.txt`
2. Download Database dump file here https://zenodo.org/records/21645628 
3. Create a PostgreSQL database (e.g. osm_routing)
4. Restore the downloaded database dump into the database
5. Add a `config.py` file with your database connection info:

   ```python
   DATABASE_URL = "postgresql+psycopg2://postgres:password@192.168.0.123:5432/osm_routing"
   ```

6. Open the notebook `isochrone.ipynb` and run all cells

## Credits

"Dijkstra_Animation.gif" by User: Ibmua,
from Wikimedia Commons:
https://commons.wikimedia.org/wiki/File:Dijkstra_Animation.gif

Licensed under CC BY-SA 3.0:
https://creativecommons.org/licenses/by-sa/3.0/

---

"london_public_transit_iso.png"
from traveltime.com
https://traveltime.com/blog/free-isochrone-map-generator

---