import { useState, useEffect } from 'react';
import MapComponent from '../components/MapComponent';
import '../styles/PartA.css';

export default function PartA() {
  const [locations, setLocations] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    category: 'historical',
    score: 5,
    lat: 0,
    lon: 0,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [runtime, setRuntime] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'score' || name === 'lat' || name === 'lon' 
        ? parseFloat(value) 
        : value
    }));
  };

  const handleAddLocation = () => {
    if (!formData.name) {
      alert('Please enter a location name');
      return;
    }
    setLocations(prev => [...prev, { ...formData, id: prev.length }]);
    setFormData({
      name: '',
      category: 'historical',
      score: 5,
      lat: 0,
      lon: 0,
    });
  };

  const handleRemoveLocation = (index) => {
    setLocations(prev => prev.filter((_, i) => i !== index));
  };

  const handleOptimize = async () => {
    if (locations.length < 2) {
      alert('Please add at least 2 locations');
      return;
    }

    setLoading(true);
    const startTime = performance.now();

    try {
      const response = await fetch('http://localhost:8000/api/part-a/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          locations: locations.map((loc, idx) => ({
            id: idx,
            name: loc.name,
            category: idx === 0 ? 'start' : idx === locations.length - 1 ? 'destination' : loc.category,
            score: idx === 0 || idx === locations.length - 1 ? 0 : loc.score,
            lat: loc.lat,
            lon: loc.lon,
          })),
          max_budget: 100,
          category_threshold: 2,
          k_decay: 0.1,
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
    <div className="part-a-container">
      <h1>Part A: Sightseeing Route Optimizer</h1>
      
      <div className="content">
        <div className="form-section">
          <h2>Add Locations</h2>
          
          <div className="form-group">
            <label>Location Name:</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="e.g., Museum"
            />
          </div>

          <div className="form-group">
            <label>Category:</label>
            <select name="category" value={formData.category} onChange={handleInputChange}>
              <option value="historical">Historical</option>
              <option value="nature">Nature</option>
              <option value="food">Food</option>
              <option value="cultural">Cultural</option>
            </select>
          </div>

          <div className="form-group">
            <label>Score (0-10):</label>
            <input
              type="number"
              name="score"
              min="0"
              max="10"
              value={formData.score}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label>Latitude:</label>
            <input
              type="number"
              name="lat"
              step="0.001"
              value={formData.lat}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label>Longitude:</label>
            <input
              type="number"
              name="lon"
              step="0.001"
              value={formData.lon}
              onChange={handleInputChange}
            />
          </div>

          <button onClick={handleAddLocation} className="btn-add">Add Location</button>

          <div className="locations-list">
            <h3>Locations ({locations.length})</h3>
            {locations.map((loc, idx) => (
              <div key={idx} className="location-item">
                <span>{loc.name} ({loc.category})</span>
                <button onClick={() => handleRemoveLocation(idx)} className="btn-remove">Remove</button>
              </div>
            ))}
          </div>

          <button 
            onClick={handleOptimize} 
            disabled={loading || locations.length < 2}
            className="btn-optimize"
          >
            {loading ? 'Optimizing...' : 'Optimize Route'}
          </button>

          {runtime && <p className="runtime">Runtime: {runtime}ms</p>}
        </div>

        <div className="results-section">
          <h2>Results</h2>
          {result ? (
            <div className="results">
              <div className="result-summary">
                <p><strong>Total Distance:</strong> {result.total_distance.toFixed(2)} km</p>
                <p><strong>Total Satisfaction:</strong> {result.total_effective_satisfaction.toFixed(2)}</p>
              </div>

              <div className="route-map">
                <h3>Route Map</h3>
                <div className="map-container">
                  <MapComponent 
                    locations={locations}
                    route={result ? result.route.map(loc => ({ lat: loc.lat, lon: loc.lon })) : []}
                    center={locations.length > 0 ? [locations[0].lat, locations[0].lon] : [0, 0]}
                    zoom={locations.length > 0 ? 10 : 2}
                  />
                </div>
              </div>

              <div className="breakdown-table">
                <h3>Route Breakdown</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Stop</th>
                      <th>Base Score</th>
                      <th>Decay Factor</th>
                      <th>Penalty Factor</th>
                      <th>Effective Score</th>
                      <th>Cumulative Distance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.breakdown.map((item, idx) => (
                      <tr key={idx}>
                        <td>{locations[item.id]?.name || 'Stop ' + item.id}</td>
                        <td>{item.base_score.toFixed(2)}</td>
                        <td>{item.decay_factor.toFixed(4)}</td>
                        <td>{item.penalty_factor.toFixed(2)}</td>
                        <td>{item.effective_score.toFixed(2)}</td>
                        <td>{item.cumulative_distance.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <p className="placeholder">Add locations and click "Optimize Route" to see results</p>
          )}
        </div>
      </div>
    </div>
  );
}
