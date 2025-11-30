let map;
let activePolylines = []; // Track lines so we can clear them later

// 1. CONSTANTS (Your Map Setup)
const UCSD_BOUNDS = {
    north: 32.9000, south: 32.8600,
    east: -117.2000, west: -117.2700
};

const CAMPUS_MAP_STYLE = [
    { featureType: 'poi.business', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    { featureType: 'transit', elementType: 'labels', stylers: [{ visibility: 'off' }] },
    { featureType: 'road', elementType: 'labels.icon', stylers: [{ visibility: 'off' }] }
];

// 2. MAIN INITIALIZATION
document.addEventListener('DOMContentLoaded', async () => {
    // Wait for Google Maps Components to load
    await customElements.whenDefined('gmp-map');
    
    const mapEl = document.querySelector('gmp-map');
    map = mapEl.innerMap; // Access the JS API map object

    // Apply your settings
    map.setOptions({
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
        minZoom: 15,
        maxZoom: 20,
        restriction: { latLngBounds: UCSD_BOUNDS, strictBounds: false },
        styles: CAMPUS_MAP_STYLE,
    });

    // A. Draw the Static Graph (Nodes & Edges)
    drawStaticGraph();

    // B. Populate the Dropdowns for the user
    populateDropdowns();
});

// --- HELPER FUNCTIONS ---

function drawStaticGraph() {
    // Note: CAMPUS_NODES comes from the <script> tag in your HTML
    CAMPUS_NODES.forEach(n => {
        // Draw Marker
        new google.maps.marker.AdvancedMarkerElement({
            map: map,
            position: { lat: n.lat, lng: n.lng },
            title: n.name,
        });
    });

    CAMPUS_EDGES.forEach(e => {
        // Draw static connections (Grey lines)
        // Find the full node object using the name
        const fromNode = CAMPUS_NODES.find(n => n.name === e.from);
        const toNode = CAMPUS_NODES.find(n => n.name === e.to);

        if (fromNode && toNode) {
            new google.maps.Polyline({
                map: map,
                path: [{ lat: fromNode.lat, lng: fromNode.lng }, { lat: toNode.lat, lng: toNode.lng }],
                strokeColor: '#888888', // Grey color for "possible paths"
                strokeOpacity: 0.3,
                strokeWeight: 2,
                clickable: false
            });
        }
    });
}

function populateDropdowns() {
    const startSelect = document.getElementById('start-node');
    const endSelect = document.getElementById('end-node');

    // Sort alphabetically so it's easier to find buildings
    const sortedNodes = [...CAMPUS_NODES].sort((a, b) => a.name.localeCompare(b.name));

    sortedNodes.forEach(node => {
        let option1 = new Option(node.name, node.name);
        let option2 = new Option(node.name, node.name);
        startSelect.add(option1);
        endSelect.add(option2);
    });
}

// --- DIJKSTRA ANIMATION LOGIC ---

// Helper: Sleep function for animation delay
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function startDijkstra() {
    clearOverlays(); // Clear previous green/red lines

    const startName = document.getElementById('start-node').value;
    const endName = document.getElementById('end-node').value;
    const statusText = document.getElementById('status-text');

    if (startName === endName) {
        statusText.innerText = "Start and End are the same!";
        return;
    }

    statusText.innerText = "Calculating path on server...";

    try {
        // 1. Call Python Backend
        // IMPORTANT: Ensure your URL matches your urls.py path
        const response = await fetch(`/calculate-path/?start=${encodeURIComponent(startName)}&end=${encodeURIComponent(endName)}`);
        const data = await response.json();

        // 2. Animate the "Search" (Red Lines)
        statusText.innerText = "Visualizing Search Algorithm...";
        
        for (let step of data.visited_log) {
            drawPolyline(step.from, step.to, "#FF0000", 2, 0.6); // Red, Thin, Semi-transparent
            await sleep(50); // 50ms pause per step
        }

        // 3. Draw the Final Path (Green Line)
        if (data.path && data.path.length > 0) {
            statusText.innerText = `Found! Distance: ${Math.round(data.distance)} meters`;
            
            for (let i = 0; i < data.path.length - 1; i++) {
                drawPolyline(data.path[i], data.path[i+1], "#00FF00", 6, 1.0, 10); // Green, Thick, Opaque, Top Z-Index
            }
        } else {
            statusText.innerText = "No path found.";
        }

    } catch (error) {
        console.error("Error:", error);
        statusText.innerText = "Error connecting to server.";
    }
}

function drawPolyline(nodeNameA, nodeNameB, color, weight, opacity, zIndex = 1) {
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
    activePolylines.push(line);
}

function clearOverlays() {
    activePolylines.forEach(line => line.setMap(null));
    activePolylines = [];
}

// Make startDijkstra global so the HTML button can click it
window.startDijkstra = startDijkstra;
window.clearMap = clearOverlays;