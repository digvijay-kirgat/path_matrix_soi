import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';

// Fix for default marker icon issue with Webpack
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const MapComponent = ({ locations = [], route = [], drivers = [], assignments = [], center = [0, 0], zoom = 2 }) => {
  const mapRef = useRef();

  useEffect(() => {
    if (mapRef.current && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => [loc.lat, loc.lon]));
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [locations]);

  return (
    <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }} ref={mapRef}>
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Locations/Attractions for Part A */}
      {locations.map((loc, idx) => (
        <Marker key={loc.id || idx} position={[loc.lat, loc.lon]}>
          <Popup>
            <b>{loc.name}</b><br/>
            Category: {loc.category}<br/>
            Score: {loc.score}<br/>
            Lat: {loc.lat.toFixed(4)}, Lon: {loc.lon.toFixed(4)}
          </Popup>
        </Marker>
      ))}

      {/* Route Polyline for Part A */}
      {route.length > 1 && (
        <Polyline positions={route.map(loc => [loc.lat, loc.lon])} color="blue" weight={5} />
      )}

      {/* Drivers for Part B */}
      {drivers.map(driver => (
        <Marker key={driver.id} position={[driver.location.lat, driver.location.lon]} icon={L.divIcon({
          className: 'custom-driver-icon',
          html: `<div style="background-color: green; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold;">${driver.id}</div>`,
          iconSize: [20, 20],
        })}>
          <Popup>
            <b>Driver {driver.id}</b><br/>
            Lat: {driver.location.lat.toFixed(4)}, Lon: {driver.location.lon.toFixed(4)}
          </Popup>
        </Marker>
      ))}

      {/* Ride Requests for Part B (pickups and drops) */}
      {assignments.map(assignment => {
        const request = assignment.request;
        const driver = assignment.driver;
        if (!request || !driver) return null;

        const pickupCoords = [request.pickup.lat, request.pickup.lon];
        const dropCoords = [request.drop.lat, request.drop.lon];
        const driverCoords = [driver.location.lat, driver.location.lon];

        return (
          <React.Fragment key={request.id}>
            {/* Pickup Marker */}
            <Marker position={pickupCoords} icon={L.divIcon({
              className: 'custom-pickup-icon',
              html: `<div style="background-color: orange; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P${request.id}</div>`,
              iconSize: [20, 20],
            })}>
              <Popup>
                <b>Request {request.id} Pickup</b><br/>
                Lat: {pickupCoords[0].toFixed(4)}, Lon: {pickupCoords[1].toFixed(4)}
              </Popup>
            </Marker>

            {/* Drop Marker */}
            <Marker position={dropCoords} icon={L.divIcon({
              className: 'custom-drop-icon',
              html: `<div style="background-color: red; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-weight: bold;">D${request.id}</div>`,
              iconSize: [20, 20],
            })}>
              <Popup>
                <b>Request {request.id} Drop</b><br/>
                Lat: {dropCoords[0].toFixed(4)}, Lon: {dropCoords[1].toFixed(4)}
              </Popup>
            </Marker>

            {/* Polyline from driver to pickup, then to drop */}
            <Polyline positions={[driverCoords, pickupCoords, dropCoords]} color="purple" dashArray="5, 5" weight={3} />
          </React.Fragment>
        );
      })}

    </MapContainer>
  );
};

export default MapComponent;
