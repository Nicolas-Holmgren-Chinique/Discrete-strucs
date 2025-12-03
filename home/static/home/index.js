// This js file contains the logic for the home page, and the is the code for the frontend visualization of the Dijkstras algorithm
// in this file, we init the google maps api, vis.js graph. We also handle the user interactions, the dropdown selections of location

let map;
let network;
let visNodes, visEdges;
let searchPolylines = []; // Track "Checking" lines 
let pathPolylines = [];   // Track "Final Path" lines 
let activeGraphHighlights = []; // Track highlights on Vis.js Graph
let currentAnimationId = 0; // Counter to track active animations and prevent race conditions


// setting the google maps api bounds, so that it mainly focuses on the UCSD campus area
const UCSD_BOUNDS = {
    north: 32.9000, south: 32.8600,
    east: -117.2000, west: -117.2700
};

// Display node names abbreviations on the map

const NODE_LABELS = {
  "Geisel Library": "Geisel",
    "Jacobs School of Engineering": "Jac",
    "Price Center": "PC",
    "Library Walk Silent Tree": "Tree",
    "Starbucks Intersection": "Strb",
    "Price Center Plaza": "PCP",
    "Library Walk Fountain": "LiF",
    "Library Walk Target": "trgt",
    "Triton Fountain": "tri",
    "Price Center East": "PCE",
    "SERF Building": "SRF",
    "Warren Mall": "Mall",
    "Snake Path": "Snk",
    "Warren Intersection": "Wrn",
    "UCSD Bear Statue": "Bear",
    "CS and Engineering Building": "CS",
    "Atkinson Hall": "Atk",
    "Engineers Pl": "Pl",
    "Engineers Ln": "Ln",
    "Warren Lecture Hall": "Hall",
    "Engineering Building": "Eng",
    "Halıcıoğlu Data Science Institute": "Data",
    "Struc and Materials Eng Bldg": "SME",
    "Amphitheater": "Amp",
    "Visual Arts Bldg": "art"
}

// custom map style for the google maps api
const CAMPUS_MAP_STYLE = [
    { featureType: 'poi.business', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    { featureType: 'transit', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    { featureType: 'road', elementType: 'labels.icon', stylers: [{ visibility: 'off' }] }
];

// MAIN INITIALIZATION
document.addEventListener('DOMContentLoaded', async () => {
    console.log("Document Loaded");

  // populate the dropdows on page load so the user can select start and end points
    populateDropdowns();

    // This calls the function to set the theme based on user preference
    initTheme();

    // This calls the function to initialize the Vis.js graph
    initVisGraph();

    try {
        // Wait for Google Maps Components to load
        await customElements.whenDefined('gmp-map');
        const mapEl = document.querySelector('gmp-map');
        if (mapEl) {
            map = mapEl.innerMap;
            
            // google map settings 
            map.setOptions({
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: false,
                minZoom: 15,
                maxZoom: 20,
                restriction: { latLngBounds: UCSD_BOUNDS, strictBounds: false },
                styles: CAMPUS_MAP_STYLE,
            });
            console.log("Google Map Initialized");
            
            // Draw Static Elements on Map (Nodes and gray connection lines)
            drawStaticMapElements();
        } else {
            console.error("gmp-map element not found!");
            document.getElementById('map-fallback').style.display = 'block';
            document.getElementById('map-fallback').innerText = "Map Element Not Found";
        }
    } catch (e) {
        console.error("Error initializing Google Map:", e);
        document.getElementById('map-fallback').style.display = 'block';
        document.getElementById('map-fallback').innerText = "Error loading Google Maps. Check API Key.";
    }
    

});

// vis.js graph setup

function initVisGraph() {
    const nodesData = CAMPUS_NODES.map(n => ({
        id: n.name,
        label: NODE_LABELS[n.name] || n.name.substring(0, 4),
        title: n.name,
        shape: 'circle',
        color: { background: '#1E293B', border: '#0F172A' }, // Slate 800 (Dark Blue-Grey)
        font: { color: '#ffffff', size: 16 } // White text
    }));

    // edges data for the grpah visualization
    const edgesData = [];
    CAMPUS_EDGES.forEach((e, index) => {
        // Add edge (undirected for visualization) by pushing to the edgesData array
        edgesData.push({
            id: `edge_${index}`,
            from: e.from,
            to: e.to,
            label: Math.round(e.distance).toString(), // Show distance
            color: { color: '#94A3B8' }, // Slate 400 (Light Grey-Blue)
            width: 2,
            font: { color: '#1E293B', strokeWidth: 0, size: 14, align: 'horizontal', background: 'rgba(255,255,255,0.7)' } // Dark text with light background
        });
    });

    visNodes = new vis.DataSet(nodesData);
    visEdges = new vis.DataSet(edgesData);

    const container = document.getElementById('mynetwork');

    // Determine if dark mode is active
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // createing the visualization of the nodes and edges using vis.js
    const data = { nodes: visNodes, edges: visEdges };
    const options = {
      nodes: {
        shape: 'circle',
        size: 25,
        font: { size: 14, color: '#ffffff' },
        borderWidth: 2
      },

      edges: {
        smooth: false
    },
      physics: {
        enabled: true,
        stabilization: { iterations: 100 }
      },
      interaction: {
        dragNodes: true,
        zoomView: true,
        dragView: true,
      }
    };
    network = new vis.Network(container, data, options); 
}


// Draw static map elements: nodes as markers and edges as gray lines
function drawStaticMapElements() {
    // Draw all nodes as markers
    CAMPUS_NODES.forEach(n => {
        const pinView = document.createdElement("div");
        pinView.className = "map-node-marker";
        pinView.textContent = NODE_LABELS[n.name] || n.name.substring(0, 3);

        new google,amps.marker.AdvancedMarkerElement({
            map: map,
            position: { lat: n.lat, lng: n.lng},
            title: n.name,
            content: pinView,
        });
    });

    //  draw all the edges as grey lines on the map
    CAMPUS_EDGES.forEach(e => {
        const fromNode = CAMPUS_NODES.find(n => n.name === e.from);
        const toNode = CAMPUSE_NODES.find(n => n.name === e.to);

// this draws the grey lines between the nodes on the google map, path using the latitude and longitude of each node
        if (fromNode && toNode) {
            new google.maps.Polyline({
                map: map,
                path: [{ lat: fromNode.lat, lng: fromNode.lng }, { lat: toNode.lat, lng: toNode.lng }],
                strokeColor: '#888888',
                strokeOpacity: 0.3,
                strokeWeight: 2,
                clickable: false
            });
        }
    });
}


// this function populates the start and end dropdowns with the campus nodes which are locations/destinations
function populateDropdowns() {
    const startSelect = document.getElementById('start-node');
    const endSelect = document.getElementById('end-node');
    const sortedNodes = [...CAMPUS_NODES].sort((a, b) => a.name.localeCompare(b.name));

    sortedNodes.forEach(node => {
        startSelect.add(new Option(node.name, node.name));
        endSelect.add(new Option(node.name, node.name));
    });
}


const sleep = (ms) => new Promise(r => setTimeout(r, ms));

// this is the main function that starts the dijkstra algorithm visualization for the google maps and vis.js graph
async function startDijkstra() {
    // Increment animation ID. This invalidates any previous running loops.
    const myAnimationId = ++currentAnimationId;

    // Reset previous runs
    clearOverlays();

    const startName = document.getElementById('start-node').value;
    const endName = document.getElementById('end-node').value;
    const statusText = document.getElementById('status-text');
    const timeText = document.getElementById('time-text');
    const tableBody = document.querySelector('#log-table tbody');

    if (startName === endName) {
        statusText.innerText = "Start and End are the same!";
        return;
    }

    statusText.innerText = "Calculating path...";
    timeText.innerText = "";
    tableBody.innerHTML = ""; // Clear table

    try {
        // Call Backend API
        const response = await fetch(`/calculate_route/?start=${encodeURIComponent(startName)}&end=${encodeURIComponent(endName)}`);
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Server Error");
        }

        const data = await response.json();

        // Check if a new animation started while we were fetching
        if (myAnimationId !== currentAnimationId) return;

        statusText.innerText = "Visualizing Search...";

        // --- ANIMATION LOOP ---
        // We iterate through the 'visited_log' returned by the server.
        // This shows every step the algorithm took.
        let stepCount = 1;
        const speed = parseInt(document.getElementById('speed-select').value) || 50;

        for (let step of data.visited_log) {
            // Check if a new animation started during the sleep
            if (myAnimationId !== currentAnimationId) return;

            // 1. Update Table
            const row = tableBody.insertRow(0); // Insert at top
            row.innerHTML = `
                <td>${stepCount++}</td>
                <td>${step.from}</td>
                <td>${step.to}</td>
                <td class="status-visiting">Checking</td>
            `;

            // 2. Update Map (Amber Line = "I am checking this path")
            // We push these to 'searchPolylines' so we can clear them later
            drawPolyline(step.from, step.to, "#F59E0B", 3, 0.8, 1, searchPolylines);

            // 3. Update Graph (Highlight Nodes/Edge)
            highlightGraphConnection(step.from, step.to, "#F59E0B");

            await sleep(speed); // Pause for visual effect
        }

        // Check again before drawing final path
        if (myAnimationId !== currentAnimationId) return;

        // --- FINAL PATH ---
        if (data.path && data.path.length > 0) {
            // Clear ONLY the "Checking" (Amber) lines from the map.
            searchPolylines.forEach(line => line.setMap(null));
            searchPolylines = [];

            statusText.innerText = `Path Found! Distance: ${Math.round(data.distance)}m`;
            
            // Calculate Walking Time (approx 1.4 m/s)
            const minutes = Math.ceil((data.distance / 1.4) / 60);
            timeText.innerText = `Est. Walking Time: ${minutes} min`;

            // Highlight Path on Map (Blue)
            // We push these to 'pathPolylines'
            for (let i = 0; i < data.path.length - 1; i++) {
                drawPolyline(data.path[i], data.path[i+1], "#3B82F6", 6, 1.0, 10, pathPolylines);
                highlightGraphConnection(data.path[i], data.path[i+1], "#3B82F6", 4);
            }
            
            // Highlight Path Nodes on Graph
            data.path.forEach(nodeName => {
                visNodes.update({ id: nodeName, color: { background: '#3B82F6', border: '#1D4ED8' } });
            });

        } else {
            statusText.innerText = "No path found.";
        }

    } catch (error) {
        console.error("Error:", error);
        statusText.innerText = "Error connecting to server.";
    }
}

function drawPolyline(nodeNameA, nodeNameB, color, weight, opacity, zIndex = 1, storageArray = null) {
    const nodeA = CAMPUS_NODES.find(n => n.name === nodeNameA);
    const nodeB = CAMPUS_NODES.find(n => n.name === nodeNameB);

    if (!nodeA || !nodeB) return;

    const line = new google.maps.Polyline({
        path: [{ lat: nodeA.lat, lng: nodeA.lng }, { lat: nodeB.lat, lng: nodeB.lng }],
        strokeColor: color,
        strokeOpacity: opacity,
        strokeWeight: weight,
        zIndex: zIndex,
        map: map
    });
    
    // If a storage array is provided, push the line to it for tracking
    if (storageArray) {
        storageArray.push(line);
    }
}

function highlightGraphConnection(from, to, color, width = 1) {
    // Find edge id (Vis.js edges need IDs or we search)
    // Since we didn't store edge IDs by node pair easily, we can just add a temporary edge or update if we find it.
    // Simpler: Update the nodes to show activity
    visNodes.update({ id: from, color: { border: color } });
    visNodes.update({ id: to, color: { border: color } });
    
    // Try to find the edge to color it
    const edges = visEdges.get({
        filter: function (item) {
            return (item.from === from && item.to === to) || (item.from === to && item.to === from);
        }
    });

    if (edges.length > 0) {
        edges.forEach(edge => {
            visEdges.update({ id: edge.id, color: { color: color }, width: width });
            activeGraphHighlights.push({ id: edge.id, originalColor: '#848484', originalWidth: 1 });
        });
    }
}

function clearOverlays() {
    // Clear Search Lines (Amber)
    searchPolylines.forEach(line => line.setMap(null));
    searchPolylines = [];

    // Clear Path Lines (Blue)
    pathPolylines.forEach(line => line.setMap(null));
    pathPolylines = [];

    // Clear Graph Highlights (Reset to default style)
    const allNodes = visNodes.getIds();
    const updates = allNodes.map(id => ({ 
        id: id, 
        color: { background: '#1E293B', border: '#0F172A' },
        font: { color: '#ffffff' }
    }));
    visNodes.update(updates);

    const allEdges = visEdges.getIds();
    const edgeUpdates = allEdges.map(id => ({ 
        id: id, 
        color: { color: '#94A3B8' }, 
        width: 2 
    }));
    visEdges.update(edgeUpdates);
    
    activeGraphHighlights = [];
}

// Expose functions to global scope
window.startDijkstra = startDijkstra;
window.clearMap = clearOverlays;
window.toggleTheme = toggleTheme;

// --- THEME LOGIC ---
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.getElementById('theme-toggle').innerText = "Light Mode";
    }
}


// this function is to allow the user to change between light and dark mode thems 

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const btn = document.getElementById('theme-toggle');
    btn.innerText = newTheme === 'dark' ? "Light Mode" : "Dark Mode";

    
}

