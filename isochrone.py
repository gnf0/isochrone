#%%
import numpy as np      # Math
from sqlalchemy import create_engine, text  # Database
import pandas as pd     # Dataframe
import folium           # Map
import h3               # Map Cells
from shapely.ops import unary_union # Isochrone Geometries
from shapely.geometry import Polygon, MultiPolygon, mapping
import matplotlib.colors as mcolors
import matplotlib.cm as cm

# --- MAP CONFIG ---
ORIGIN_CITY_STATE = "Denver, CO" # Any in Continental United States
ISOLAYER_INCREMENT = 500 # Miles
ISOCHRONE_RESOLUTION = 5 # 3-very_low, 4-low, 5-med, 6-high
MAP_TILE_THEME = "OpenStreetMap"

ISOCHRONE_COLOR_SCHEME = "Spectral"
# ISOCHRONE_COLOR_SCHEME = "HSV"
# ISOCHRONE_COLOR_SCHEME = "RdYlGn_r"

# --- SQL ---
ENGINE = create_engine(
    "postgresql+psycopg2://postgres:password@192.168.0.102:5432/osm"
)

BATCH_SIZE = 5750

# --- DATA SETS ---
CITY_LAT_LNG = pd.read_csv("datasets/city_lat_long.csv") # Contains all US Cities, Towns, etc.

# --- Verify CONFIG ---
VERIFY_CONFIG = True

def verify_config():
    print(f"""
    🌎🌏 Generating Isochrone Map 🌎🌏

    Origin:         {ORIGIN_CITY_STATE}
    Iso-Layers:     Increments of {ISOLAYER_INCREMENT} Miles
    Iso-Resolution: {ISOCHRONE_RESOLUTION}
    """)

if VERIFY_CONFIG: verify_config()


# --- Sub-Functions ---
def identify_origin_cell(origin: str, resolution: int):
    ORIGIN_STATE = ORIGIN_CITY_STATE[-2:]
    ORIGIN_CITY = ORIGIN_CITY_STATE[:-4]

    # - 1 - find origin coordinates from origin name
    origin_df = CITY_LAT_LNG.loc[
        (CITY_LAT_LNG["city"] == ORIGIN_CITY) &
        (CITY_LAT_LNG["state"] == ORIGIN_STATE)
    ].reset_index(drop=True)
    
    ORIGIN_LAT = origin_df.loc[0, "latitude"]
    ORIGIN_LNG = origin_df.loc[0, "longitude"]

    # - 2 - find origin cell from coordinates
    ORIGIN_CELL = h3.latlng_to_cell(
        lat=ORIGIN_LAT,
        lng=ORIGIN_LNG,
        res=ISOCHRONE_RESOLUTION
    )    

    return ORIGIN_CELL


ORIGIN_CELL = identify_origin_cell(ORIGIN_CITY_STATE, ISOCHRONE_RESOLUTION)


def query_nodes(origin_cell, resolution):
    # - 1 - load node cache with road snapped points for resolution
    nodes_df = pd.read_csv(f"datasets/initial_res_{ISOCHRONE_RESOLUTION}_points.csv")
    nodes_df = nodes_df.loc[nodes_df["ValidSnap"] == True]

    nodes_df = nodes_df.drop(
        columns=[
            "neighbors",
            "ValidNeighbors",
            "ValidSnap",
            "RSCellID",
            "RSDistance",
        ]
    )

    # Road snapped center point of origin cell
    ORIGIN_ROAD_SNAP_LAT = float(
        nodes_df.loc[nodes_df["CellID"] == ORIGIN_CELL, "RSLatitude"].iloc[0]
    )
    ORIGIN_ROAD_SNAP_LNG = float(
        nodes_df.loc[nodes_df["CellID"] == ORIGIN_CELL, "RSLongitude"].iloc[0]
    )

    # Prep dataframe for transit distance query
    nodes_df = nodes_df[["CellID", "RSLatitude", "RSLongitude"]].rename(
        columns={
            "CellID": "cell_id",
            "RSLatitude": "lat",
            "RSLongitude": "lng",
        }
    )
    
    # - 2 - batch query transit distances for all nodes
    with ENGINE.begin() as conn:
        # 1️⃣ Create temp table for raw destination points
        conn.execute(text("""
            CREATE TEMP TABLE destination_points (
                cell_id TEXT,
                lat DOUBLE PRECISION,
                lng DOUBLE PRECISION
            ) ON COMMIT DROP;
        """))

        nodes_df.to_sql(
            "destination_points",
            conn,
            if_exists="append",
            index=False,
            method="multi"
        )

        # 2️⃣ Materialize nearest node for each destination
        conn.execute(text("""
            CREATE TEMP TABLE destinations AS
            SELECT
                d.cell_id,
                r.target AS node_id
            FROM destination_points d
            JOIN LATERAL (
                SELECT target
                FROM routing_roads
                ORDER BY geom <-> ST_Transform(
                    ST_SetSRID(ST_Point(d.lng, d.lat), 4326),
                    3857
                )
                LIMIT 1
            ) r ON true;
        """))

        conn.execute(text("""
            CREATE INDEX ON destinations (node_id);
        """))

        # 3️⃣ Fetch distinct node_ids
        node_ids = pd.read_sql(
            "SELECT DISTINCT node_id FROM destinations",
            conn
        )["node_id"].tolist()

        print(f"Routing 1 origin to {len(node_ids)} destinations")

        # 4️⃣ Prepare batched Dijkstra SQL
        batch_sql = text("""
        WITH origin AS (
            SELECT source AS id
            FROM routing_roads
            ORDER BY geom <-> ST_Transform(
                ST_SetSRID(ST_Point(:lng1, :lat1), 4326),
                3857
            )
            LIMIT 1
        )
        SELECT
            r.end_vid AS node_id,
            SUM(r.cost) AS driving_distance_m
        FROM pgr_dijkstra(
            'SELECT id, source, target, cost,
                    COALESCE(reverse_cost, cost) AS reverse_cost
            FROM routing_roads',
            (SELECT id FROM origin),
            :node_array,
            true
        ) r
        GROUP BY r.end_vid;
        """)

        # 5️⃣ Run in batches
        all_results = []

        for i in range(0, len(node_ids), BATCH_SIZE):
            batch = node_ids[i:i+BATCH_SIZE]

            print(f"Batch {i//BATCH_SIZE + 1} ({len(batch)} nodes)")

            result = pd.read_sql(
                batch_sql,
                conn,
                params={
                    "lat1": ORIGIN_ROAD_SNAP_LAT,
                    "lng1": ORIGIN_ROAD_SNAP_LNG,
                    "node_array": batch
                }
            )

            all_results.append(result)

        # 6️⃣ Combine batch results
        result_df = pd.concat(all_results, ignore_index=True)

        # 7️⃣ Load mapping: cell_id -> node_id
        cell_to_node = pd.read_sql(
            "SELECT cell_id, node_id FROM destinations",
            conn
        )

        # 8️⃣ Attach distances to each cell via node_id
        cell_distances = cell_to_node.merge(
            result_df,
            on="node_id",
            how="left"
        )

        # 9️⃣ Merge back onto nodes dataframe
        nodes_df = nodes_df.merge(
            cell_distances[["cell_id", "driving_distance_m"]],
            on="cell_id",
            how="left"
        )

        print("Done.")

    nodes_df["driving_distance_miles"] = nodes_df["driving_distance_m"]/1608.344

    nodes_df["driving_distance_days"] = (
        pd.to_numeric(nodes_df["driving_distance_miles"], errors="coerce")
        / ISOLAYER_INCREMENT
    ).apply(np.ceil)

    return nodes_df


# nodes_df = query_nodes(ORIGIN_CELL, ISOCHRONE_RESOLUTION)

def get_unique_day_polygon(df, transit_day):
    filtered_df = df.loc[df["driving_distance_days"] == transit_day]
    h3_indexes = filtered_df["cell_id"].unique()

    polygons = []

    for h in h3_indexes:
        boundary = h3.cell_to_boundary(h)
        polygons.append(Polygon(boundary))

    merged = unary_union(polygons)

    if isinstance(merged, Polygon):
        merged = MultiPolygon([merged])

    return merged

def flip_coords(geom):
    """Swap (x, y) → (y, x) recursively for Polygon/MultiPolygon"""
    if geom.is_empty:
        return geom

    geom = geom.buffer(0.001).buffer(-0.001) # remove multipolygon internal artifacts

    if geom.geom_type == "Polygon":
        exterior = [(y, x) for x, y in geom.exterior.coords]
        interiors = [[(y, x) for x, y in i.coords] for i in geom.interiors]
        return Polygon(exterior, interiors)
    elif geom.geom_type == "MultiPolygon":
        return MultiPolygon([flip_coords(p) for p in geom.geoms])
    else:
        return geom

def set_isochrone_geometries(map_nodes_df, isolayer_increment):
    # - 1 - define each isochrone color based on min/max of transit distances & isolayer_increment
    map_nodes_df = map_nodes_df.dropna(subset=["driving_distance_days"])

    unique_transit_days = map_nodes_df["driving_distance_days"].unique()


    # - 2 - define multipolygons for each isolayer
    geometries = {
        day: get_unique_day_polygon(map_nodes_df, day)
        for day in unique_transit_days
    }

    for day in geometries:
        geometries[day] = flip_coords(geometries[day])  # swap coords for Folium

    return geometries # this needs to be something that can just be "add to m"

# ISOCHRONE_GEOMETRIES = set_isochrone_geometries(nodes_df, ISOLAYER_INCREMENT)

def innitalize_map(map_tiles, origin_cell, isochrone_geometries):
    cmap = cm.get_cmap(ISOCHRONE_COLOR_SCHEME)

    norm_transit_days = mcolors.Normalize(vmin=1, vmax=max(isochrone_geometries))
    
    # - 1 - define blank map
    m = folium.Map(
        location=(40, -100), 
        zoom_start=5, 
        tiles=map_tiles
        )
    # - 2 - add isochrones to map
    for day, polygons in isochrone_geometries.items():

        isochrone_color = mcolors.to_hex(cmap(norm_transit_days(day)))
        folium.GeoJson(
            data={
                "type": "Feature",
                "geometry": mapping(polygons),
                "properties": {}
            },
            style_function=lambda feature, col=isochrone_color: {
                "fill": True,
                "color": col,
                "fill_opacity": 0.9,
                "weight": 1
            }
        ).add_to(m)    

    return m

# m = innitalize_map(MAP_TILE_THEME, ORIGIN_CELL, ISOCHRONE_GEOMETRIES)

# --- Main Function ---
def generate_isochrone_map(origin, resolution, isolayer_increment, map_tiles="cartoDBdarkmatter"):
    """
    Main Function
    Takes map CONFIG and returns a map
    """

    ORIGIN_CELL = identify_origin_cell(origin, resolution)

    MAP_NODES_DF = query_nodes(ORIGIN_CELL, resolution)

    ISOCHRONE_GEOMETRIES = set_isochrone_geometries(MAP_NODES_DF, isolayer_increment)

    map = innitalize_map(map_tiles, ORIGIN_CELL, ISOCHRONE_GEOMETRIES)

    return map

#%%
# --- Main Function Call ---
m = generate_isochrone_map(
    origin=ORIGIN_CITY_STATE, 
    miles_per_day=ISOLAYER_INCREMENT, 
    resolution=ISOCHRONE_RESOLUTION, 
    isolayer_increment=ISOLAYER_INCREMENT,
    map_tiles=MAP_TILE_THEME)

#%%
m