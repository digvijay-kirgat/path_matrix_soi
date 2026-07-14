import { useState, useEffect } from 'react';
import MapComponent from '../components/MapComponent';
import '../styles/PartB.css';

export default function PartB() {
  const [requests, setRequests] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [formData, setFormData] = useState({
    requestPickupLat: 0,
    requestPickupLon: 0,
    requestDropLat: 0,
    requestDropLon: 0,
    requestBase: 10,
    requestFlex: 5,
    driverLat: 0,
    driverLon: 0,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [runtime, setRuntime] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('Lat') || name.includes('Lon') || name.includes('Base') || name.includes('Flex')
        ? parseFloat(value)
        : value
    }));
  };

  const handleAddRequest = () => {
    setRequests(prev => [...prev, {
      id: prev.length,
      pickup: { lat: formData.requestPickupLat, lon: formData.requestPickupLon },
      drop: { lat: formData.requestDropLat, lon: formData.requestDropLon },
      base_distance: formData.requestBase,
      flexibility: formData.requestFlex,
    }]);
    setFormData(prev => ({
      ...prev,
      requestPickupLat: 0,
      requestPickupLon: 0,
      requestDropLat: 0,
      requestDropLon: 0,
      requestBase: 10,
      requestFlex: 5,
    }));
  };

  const handleRemoveRequest = (index) => {
    setRequests(prev => prev.filter((_, i) => i !== index));
  };

  const handleAddDriver = () => {
    setDrivers(prev => [...prev, {
      id: prev.length,
      location: { lat: formData.driverLat, lon: formData.driverLon },
    }]);
    setFormData(prev => ({
      ...prev,
      driverLat: 0,
      driverLon: 0,
    }));
  };

  const handleRemoveDriver = (index) => {
    setDrivers(prev => prev.filter((_, i) => i !== index));
  };

  const handleMatch = async () => {
    if (requests.length === 0 || drivers.length === 0) {
      alert('Please add at least 1 request and 1 driver');
      return;
    }

    setLoading(true);
    const startTime = performance.now();

    try {
      const response = await fetch('http://localhost:8000/api/part-b/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requests: requests.map((r, idx) => ({
            id: idx,
            pickup: r.pickup,
            drop: r.drop,
            base_distance: r.base_distance,
            flexibility: r.flexibility,
          })),
          drivers: drivers.map((d, idx) => ({
            id: idx,
            location: d.location,
          })),
          capacity: 4,
        }),
      });

      const data = await response.json();
      const endTime = performance.now();
      setRuntime(Math.round(endTime - startTime));
      setResult(data);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="part-b-container">
      <h1>Part B: Dynamic Ride-Sharing</h1>
      
      <div className="content">
        <div className="form-section">
          <div className="form-subsection">
            <h2>Add Ride Requests</h2>
            
            <div className="form-group">
              <label>Pickup Latitude:</label>
              <input
                type="number"
                name="requestPickupLat"
                step="0.001"
                value={formData.requestPickupLat}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Pickup Longitude:</label>
              <input
                type="number"
                name="requestPickupLon"
                step="0.001"
                value={formData.requestPickupLon}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Drop Latitude:</label>
              <input
                type="number"
                name="requestDropLat"
                step="0.001"
                value={formData.requestDropLat}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Drop Longitude:</label>
              <input
                type="number"
                name="requestDropLon"
                step="0.001"
                value={formData.requestDropLon}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Base Distance:</label>
              <input
                type="number"
                name="requestBase"
                value={formData.requestBase}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Flexibility:</label>
              <input
                type="number"
                name="requestFlex"
                value={formData.requestFlex}
                onChange={handleInputChange}
              />
            </div>

            <button onClick={handleAddRequest} className="btn-add">Add Request</button>

            <div className="items-list">
              <h3>Requests ({requests.length})</h3>
              {requests.map((req, idx) => (
                <div key={idx} className="item">
                  <span>Request {idx + 1}: ({req.pickup.lat.toFixed(3)}, {req.pickup.lon.toFixed(3)}) → ({req.drop.lat.toFixed(3)}, {req.drop.lon.toFixed(3)})</span>
                  <button onClick={() => handleRemoveRequest(idx)} className="btn-remove">Remove</button>
                </div>
              ))}
            </div>
          </div>

          <div className="form-subsection">
            <h2>Add Drivers</h2>
            
            <div className="form-group">
              <label>Driver Latitude:</label>
              <input
                type="number"
                name="driverLat"
                step="0.001"
                value={formData.driverLat}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Driver Longitude:</label>
              <input
                type="number"
                name="driverLon"
                step="0.001"
                value={formData.driverLon}
                onChange={handleInputChange}
              />
            </div>

            <button onClick={handleAddDriver} className="btn-add">Add Driver</button>

            <div className="items-list">
              <h3>Drivers ({drivers.length})</h3>
              {drivers.map((driver, idx) => (
                <div key={idx} className="item">
                  <span>Driver {idx + 1}: ({driver.location.lat.toFixed(3)}, {driver.location.lon.toFixed(3)})</span>
                  <button onClick={() => handleRemoveDriver(idx)} className="btn-remove">Remove</button>
                </div>
              ))}
            </div>
          </div>

          <button 
            onClick={handleMatch} 
            disabled={loading || requests.length === 0 || drivers.length === 0}
            className="btn-match"
          >
            {loading ? 'Matching...' : 'Match Rides'}
          </button>

          {runtime && <p className="runtime">Runtime: {runtime}ms</p>}
        </div>

        <div className="results-section">
          <h2>Results</h2>
          {result ? (
            <div className="results">
              <div className="result-summary">
                <p><strong>Total Assignments:</strong> {result.assignments?.length || 0}</p>
                <p><strong>Accepted Requests:</strong> {result.accepted || 0}</p>
                <p><strong>Rejected Requests:</strong> {result.rejected || 0}</p>
              </div>

              <div className="route-map">
                <h3>Assignments Map</h3>
                <div className="map-container">
                  <MapComponent 
                    drivers={drivers.map((d, idx) => ({ id: idx, location: d.location }))}
                    assignments={result && result.assignments ? result.assignments.map(assign => ({
                      request: requests[assign.request_id],
                      driver: drivers[assign.driver_id],
                    })) : []}
                    center={drivers.length > 0 ? [drivers[0].location.lat, drivers[0].location.lon] : [0, 0]}
                    zoom={drivers.length > 0 ? 10 : 2}
                  />
                </div>
              </div>

              {result.assignments && result.assignments.length > 0 && (
                <div className="assignments-table">
                  <h3>Assignments</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Request ID</th>
                        <th>Driver ID</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.assignments.map((assign, idx) => (
                        <tr key={idx}>
                          <td>{assign.request_id}</td>
                          <td>{assign.driver_id}</td>
                          <td>{assign.status || 'Assigned'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {result.rejected_log && result.rejected_log.length > 0 && (
                <div className="rejected-table">
                  <h3>Rejected Requests</h3>
                  <table>
                    <thead>
                      <tr>
                        <th>Request ID</th>
                        <th>Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.rejected_log.map((reject, idx) => (
                        <tr key={idx}>
                          <td>{reject.request_id}</td>
                          <td>{reject.reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ) : (
            <p className="placeholder">Add requests and drivers, then click "Match Rides" to see results</p>
          )}
        </div>
      </div>
    </div>
  );
}
