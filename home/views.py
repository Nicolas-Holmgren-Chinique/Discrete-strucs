from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import json
import heapq  #heapq is needed for the priority queue in Dijkstra's algorithm, this queue allows us to efficiently get the next node with the smallest distance

# Approx meters per degree near UCSD

# With these consts we are converting the lat/lngs to meters to calcualte the distances between nodes
METERS_PER_DEG_LAT = 111320
METERS_PER_DEG_LON = 93340  # longitude meters shrink with latitude




"""
this file is the main backend logic for the campus map naviagtion, we have all the nodes and edges defined here with their respective lat/long coordinates
and their connections which are the edges.

We also implement Dijkstra's algorithm to calculate the shortest path between two nodes on the campus map.
and using the lat/long coordinates we calculate the distances between nodes to use as weights for the edges in the graph, to obtain an accurate shortest path.

The home function render the main page and passes the nodes and edges data to the frontend template so that it can be visualized on the map and used in the js code.
"""


    # Nodes, we store each node as a dictionary, each having a name and lat/long pair
    # We need the lat/lng to calcuate distance between nodes
    # We also added an id but we decied to not use it in the end
NODES = [
    {"id": 0, "name": "Geisel Library", "lat": 32.88012, "lng": -117.23401},
    {"id": 1, "name": "Jacobs School of Engineering", "lat": 32.88165, "lng": -117.23530},
    {"id": 2, "name": "Price Center", "lat": 32.87965, "lng": -117.23650},
    {"id": 3, "name": "Library Walk Silent Tree", "lat": 32.88040, "lng": -117.23751},
    {"id": 4, "name": "Starbucks Intersection", "lat": 32.88035, "lng": -117.23632},
    {"id": 5, "name": "Price Center Plaza", "lat": 32.87975, "lng": -117.23695},
    {"id": 6, "name": "Library Walk Fountain", "lat": 32.87935, "lng": -117.23755},
    {"id": 7, "name": "Library Walk Target", "lat": 32.87905, "lng": -117.23755},
    {"id": 8, "name": "Triton Fountain", "lat": 32.87935, "lng": -117.23615},
    {"id": 9, "name": "Price Center East", "lat": 32.87970, "lng": -117.23600},
    {"id": 10, "name": "SERF Building", "lat": 32.87975, "lng": -117.23505},
    {"id": 11, "name": "Warren Mall", "lat": 32.88115, "lng": -117.23460},
    {"id": 12, "name": "Snake Path", "lat": 32.88110, "lng": -117.23660},
    {"id": 13, "name": "Warren Intersection", "lat": 32.88115, "lng": -117.23415},
    {"id": 14, "name": "UCSD Bear Statue", "lat": 32.88195, "lng": -117.23415},
    {"id": 15, "name": "CS and Engineering Building", "lat": 32.88185, "lng": -117.23365},
    {"id": 16, "name": "Atkinson Hall", "lat": 32.88245, "lng": -117.23465},
    {"id": 17, "name": "Engineers Pl", "lat": 32.88185, "lng": -117.23585},
    {"id": 18, "name": "Engineers Ln", "lat": 32.88205, "lng": -117.23505},
    {"id": 19, "name": "Warren Lecture Hall", "lat": 32.88065, "lng": -117.23435},
    {"id": 20, "name": "Engineering Building", "lat": 32.88115, "lng": -117.23335},
    {"id": 21, "name": "Halıcıoğlu Data Science Institute", "lat": 32.88065, "lng": -117.23385},
    {"id": 22, "name": "Struc and Materials Eng Bldg", "lat": 32.87985, "lng": -117.23275},
    {"id": 23, "name": "Amphitheater", "lat": 32.87925, "lng": -117.23315},
    {"id": 24, "name": "Visual Arts Bldg", "lat": 32.87915, "lng": -117.23405},
]

# Undirected connections listed once, these are the edges, which connect each node
EDGE_CONNECTIONS = [
    ("Geisel Library", "Library Walk Silent Tree"),
    ("Geisel Library", "Snake Path"),

    ("Jacobs School of Engineering", "Snake Path"),
    ("Jacobs School of Engineering", "Engineers Pl"),
    ("Jacobs School of Engineering", "Engineers Ln"),
    ("Jacobs School of Engineering", "Warren Mall"),
    ("Jacobs School of Engineering", "Starbucks Intersection"),

    ("Price Center", "Price Center Plaza"),
    ("Price Center", "Price Center East"),
    ("Price Center", "Triton Fountain"),
    ("Price Center", "Starbucks Intersection"),

    ("Library Walk Silent Tree", "Library Walk Fountain"),
    ("Library Walk Silent Tree", "Starbucks Intersection"),
    ("Library Walk Silent Tree", "Price Center Plaza"),
    ("Library Walk Fountain", "Library Walk Target"),
    ("Library Walk Fountain", "Price Center Plaza"),
    ("Library Walk Target", "Triton Fountain"),

    ("Triton Fountain", "Price Center East"),
    ("Triton Fountain", "SERF Building"),

    ("Price Center East", "SERF Building"),
    ("Price Center East", "Warren Lecture Hall"),
    ("SERF Building", "Warren Lecture Hall"),

    ("Warren Mall", "Warren Intersection"),
    ("Warren Mall", "Starbucks Intersection"),
    ("Warren Mall", "Warren Lecture Hall"),

    ("Warren Intersection", "UCSD Bear Statue"),
    ("Warren Intersection", "Warren Lecture Hall"),
    ("Warren Intersection", "Halıcıoğlu Data Science Institute"),

    ("UCSD Bear Statue", "CS and Engineering Building"),
    ("UCSD Bear Statue", "Atkinson Hall"),
    ("Engineers Pl", "Engineers Ln"),
    ("Engineers Ln", "Atkinson Hall"),

    ("CS and Engineering Building", "Engineering Building"),
    ("Engineering Building", "Halıcıoğlu Data Science Institute"),
    ("Halıcıoğlu Data Science Institute", "Struc and Materials Eng Bldg"),
    ("Struc and Materials Eng Bldg", "Amphitheater"),
    ("Struc and Materials Eng Bldg", "Visual Arts Bldg"),
    ("Amphitheater", "Visual Arts Bldg"),
    ("Visual Arts Bldg", "SERF Building"),
]

"""
This function calcualtes the distance between two nodes using their lat/long coordinates
we use pythagorean theorem to calcualte the distance in meters between two points
"""
def calculate_distance(lat1, lon1, lat2, lon2):
    dy = (lat2 - lat1) * METERS_PER_DEG_LAT
    dx = (lon2 - lon1) * METERS_PER_DEG_LON
    return round((dx**2 + dy**2) ** 0.5, 2)


"""
This function renders the home page, and adds the backend data needed for the map into the page context
"""
def home(request):
# We look up each node by name and then get its lat/long to calculate distances for the edge weights
    
    node_lookup = {n["name"]: n for n in NODES}
    EDGES = []
    VIS_EDGES = [] # visualization edges

    ADJANCY = {n["name"]: [] for n in NODES}

# for each edge connection we calculate the distance between the two nodes

    """
    for example a is "Geisel Library" and b is "Library Walk Silent Tree", then na and nb are the actual nodes from the NODES list
    we then use their lat/long to calculate the distance between them
    """
    for a, b in EDGE_CONNECTIONS:
        na, nb = node_lookup.get(a), node_lookup.get(b)
        if not na or not nb:
            continue

        # We call the distance calc function, passing in the lat/long of each node
        dist = calculate_distance(na["lat"], na["lng"], nb["lat"], nb["lng"])

        # These are the edges for the map visualization which will show on the frontend
        # we have two versions as this is an undirected graph
        EDGES.append({"from": a, "to": b, "distance": dist})
        EDGES.append({"from": b, "to": a, "distance": dist})

# this is the adjacency list for the backend graph representation

        VIS_EDGES.append({"from": a, "to": b, "distance": dist})

        ADJANCY[a].append({"to": b, "distance": dist})
        ADJANCY[b].append({"to": a, "distance": dist})


# This dict will be passed to the frontend template html
    context = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "nodes_json": json.dumps(NODES),
        "edges_json": json.dumps(VIS_EDGES),
        "adjacency_json": json.dumps({}),  # optional: build if you need
    }
    return render(request, "home/home.html", context)

# This function calculates the shortest route between two nodes using Dijkstra's algorithm
def calculate_route(request):
    start_node = request.GET.get('start')
    end_node = request.GET.get('end')



    # Build the graph
    """
    this builds the graph as an adjacency list from the NODES and EDGE_CONNECTIONS constants, each
    node points to a list of tuples containing its neighbors and the weight to that neighbor,
    """
    node_lookup = {n['name']: n for n in NODES}
    graph = {n['name']: [] for n in NODES}

    for a, b in EDGE_CONNECTIONS:
        na, nb = node_lookup.get(a), node_lookup.get(b)
        if not na or not nb:
            continue
        dist = calculate_distance(na['lat'], na['lng'], nb['lat'], nb['lng'])
        graph[a].append((b, dist))
        graph[b].append((a, dist))  # Undirected graph


    # Dijkstra's algorithm with a log using a priotiry queue which is more efficient and allows us to do better pathfinding

    pq = [(0, start_node)]
    distances = {node['name']: float('inf') for node in NODES}
    distances[start_node] = 0
    previous = {}

    # Log to trace computation and track each visited node 
    visted_log = []

#   We process the priority queue until it's empty
    while pq:
        current_dist, current_node = heapq.heappop(pq)

        # If we reached the destination node, we can stop
        if current_node == end_node:
            break

# if we have already found a better path, skip processing
        if current_dist > distances[current_node]:
            continue

# for each neighbor of the current node, we check if we can improve the distance to that neigbor
        for neigbor, weight in graph[current_node]:

            visted_log.append({
                "from": current_node,
                "to": neigbor,
                # "weight": weight
            })

# After visting each node we have to add the cost to reach its neighbors
            new_dist = current_dist + weight
            if new_dist < distances[neigbor]:
                distances[neigbor] = new_dist
                previous[neigbor] = current_node
                heapq.heappush(pq, (new_dist, neigbor))


    """
    This reconstructs the shortest path from the start_node to the end_node,
    by backtracking using the pre dict of previous nodes
    """
    path = []

    curr = end_node
# if we find a valid path then we backtrack to build the path list
    if distances[end_node] != float('inf'):
        while curr != start_node:
            path.append(curr)
            curr = previous[curr]
        path.insert(0, start_node)



# this json response is sent back to the frontend with the path and visited log
    return JsonResponse({
        "path": path,
        "visited_log": visted_log,
        "distance": distances[end_node]
    })