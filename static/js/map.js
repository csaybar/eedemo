var osmUrl = 'https://{s}.tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey={apikey}',
    osmAttrib = '&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    osm = L.tileLayer(osmUrl, { maxZoom: 22, attribution: osmAttrib,apikey: 'e1a6f570a6da41b0bc359fc143966469'}),
    map = new L.Map('map', { center: new L.LatLng(-8.1, -75.2), zoom: 5}),
    drawnItems = L.featureGroup().addTo(map);

L.control.layers({
    'Topo': osm.addTo(map),
    "Satelite": L.tileLayer('http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}', {
    attribution: 'google'
    })}, { 'drawlayer': drawnItems }, { position: 'topleft', collapsed: false }).addTo(map);


var drawControl =  new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
    poly: {
        allowIntersection: true,
        }
    },
    draw: {
        polygon: {
            allowIntersection: true,
            showArea: true
        }
    }
})

map.addControl(drawControl);

map.on('draw:created', function (e) {
    var type = e.layerType,
        layer = e.layer;
    drawnItems.addLayer(layer);
});
