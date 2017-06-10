# Transit Network Add-and-Remove

Idea is to adapt some aspects of the UrbanAccess library to allow people to modify existing transit and walk networks, and produce fresh isochrones each time. Current tools tend to either prohibit network modification or only allow for removal. With a tool like Pandana, it's easy to simply introduce new edges to the network and compute the output resulting. 

## Generating Data
Run the `generate.py` file to create OSM network data relevant to the area that you are looking to analyze. Update the bounding box paramter accordingly.