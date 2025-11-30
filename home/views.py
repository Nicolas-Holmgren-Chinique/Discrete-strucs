from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import json
import heapq

# Approx meters per degree near UCSD
METERS_PER_DEG_LAT = 111320
METERS_PER_DEG_LON = 93340  # longitude meters shrink with latitude




    # Nodes (keep as-is for now)
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

# Undirected connections listed once (names must match NODES)
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

def calculate_distance(lat1, lon1, lat2, lon2):
    dy = (lat2 - lat1) * METERS_PER_DEG_LAT
    dx = (lon2 - lon1) * METERS_PER_DEG_LON
    return round((dx**2 + dy**2) ** 0.5, 2)

def home(request):

    node_lookup = {n["name"]: n for n in NODES}
    EDGES = []


    ADJANCY = {n["name"]: [] for n in NODES}

    for a, b in EDGE_CONNECTIONS:
        na, nb = node_lookup.get(a), node_lookup.get(b)
        if not na or not nb:
            continue
        dist = calculate_distance(na["lat"], na["lng"], nb["lat"], nb["lng"])
        # Add both directions for walking graph
        EDGES.append({"from": a, "to": b, "distance": dist})
        EDGES.append({"from": b, "to": a, "distance": dist})


        ADJANCY[a].append({"to": b, "distance": dist})
        ADJANCY[b].append({"to": a, "distance": dist})

    context = {
        "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        "nodes_json": json.dumps(NODES),
        "edges_json": json.dumps(EDGES),
        "adjacency_json": json.dumps({}),  # optional: build if you need
    }
    return render(request, "home/home.html", context)

def calculate_route(request):
    start_node = request.GET.get('start')
    end_node = request.GET.get('end')



    # Build the graph

    node_lookup = {n['name']: n for n in NODES}
    graph = {n['name']: [] for n in NODES}

    for a, b in EDGE_CONNECTIONS:
        na, nb = node_lookup.get(a), node_lookup.get(b)
        if not na or not nb:
            continue
        dist = calculate_distance(na['lat'], na['lng'], nb['lat'], nb['lng'])
        graph[a].append((b, dist))
        graph[b].append((a, dist))  # Undirected graph


    # Dijkstra's algorithm with a log

    pq = [(0, start_node)]
    distances = {node['name']: float('inf') for node in NODES}
    distances[start_node] = 0
    previous = {}

    # Log to trace computation  
    visted_log = []

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node == end_node:
            break


        if current_dist > distances[current_node]:
            continue


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


    path = []

    curr = end_node

    if distances[end_node] != float('inf'):
        while curr != start_node:
            path.append(curr)
            curr = previous[curr]
        path.insert(0, start_node)

    return JsonResponse({
        "path": path,
        "visited_log": visted_log,
        "distance": distances[end_node]
    })