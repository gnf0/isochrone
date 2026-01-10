# isochrone generator

Takes a given location within the **Continental United States** and outputs an **isochrone map** based on **road driving transit distance** from that location

*example_visual_output.jpeg*

Simmilar apps exits for shorter transit distances, these generally display walking or biking distances

*simmilar_app_screenshot.jpeg*

Maps at greater distances are often created based on estimates and are not precise

*highlights_of_maps_imprecision.jpeg*

## alpha version specs
* uses h3 hexagons
* isochrone layer distances 500miles or greater
* takes input and displays output on an interactive map

## step 1 - *data*
SQLite Database n-columns * n-rows for n cities in database
- want to maximize n for highest resolution of isochrone
- may run into issues with sufficiently large table

- [ ]  of many city to city road travel distances
  - [x] get csv of city to city straight line distances - [ ] reduce straight line csv to fewer total cities (maintain even geographical distrobution)
  - [ ] get as many 
  - [ ] google maps api
- [ ] put travel distance csv in database
- [ ] create functions to query database

## step 2 - *ui*
- [ ] map
- [ ] user input field
  - [ ] drop down of all cities in csv?
- [ ] run or execute

## step 3 - *execution*
- [ ] map shading
  - [ ]  define map areas (many)
- [ ] query table
  - [ ] for the input city and all distances from

