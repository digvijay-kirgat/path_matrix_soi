import { useState } from 'react';
import PartA from './pages/PartA';
import PartB from './pages/PartB';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  return (
    <div className="app">
      <nav className="navbar">
        <div className="nav-container">
          <h1 className="logo">Route Planning & Ride-Sharing</h1>
          <ul className="nav-menu">
            <li>
              <button 
                className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
                onClick={() => setCurrentPage('home')}
              >
                Home
              </button>
            </li>
            <li>
              <button 
                className={`nav-link ${currentPage === 'part-a' ? 'active' : ''}`}
                onClick={() => setCurrentPage('part-a')}
              >
                Route Optimizer
              </button>
            </li>
            <li>
              <button 
                className={`nav-link ${currentPage === 'part-b' ? 'active' : ''}`}
                onClick={() => setCurrentPage('part-b')}
              >
                Ride-Sharing
              </button>
            </li>
          </ul>
        </div>
      </nav>

      <main className="main-content">
        {currentPage === 'home' && (
          <div className="home-page">
            <div className="hero">
              <h1>Intelligent Route Planning & Adaptive Optimization System</h1>
              <p>Optimize sightseeing routes and manage dynamic ride-sharing with advanced algorithms</p>
            </div>

            <div className="features">
              <div className="feature-card">
                <h2>Part A: Sightseeing Route Optimizer</h2>
                <p>
                  Optimize your sightseeing routes using beam search and simulated annealing algorithms.
                  Consider location categories, scores, and travel distances to create the perfect itinerary.
                </p>
                <button onClick={() => setCurrentPage('part-a')} className="btn-feature">
                  Go to Route Optimizer
                </button>
              </div>

              <div className="feature-card">
                <h2>Part B: Dynamic Ride-Sharing</h2>
                <p>
                  Match ride requests to drivers using the cheapest insertion algorithm.
                  Optimize vehicle utilization while respecting capacity and flexibility constraints.
                </p>
                <button onClick={() => setCurrentPage('part-b')} className="btn-feature">
                  Go to Ride-Sharing
                </button>
              </div>
            </div>

            <div className="info-section">
              <h2>How It Works</h2>
              <div className="info-grid">
                <div className="info-item">
                  <h3>Part A: Route Optimization</h3>
                  <ul>
                    <li><strong>Stage 1:</strong> Beam search finds promising initial routes</li>
                    <li><strong>Stage 2:</strong> Simulated annealing refines the solution</li>
                    <li><strong>Metrics:</strong> Considers distance, satisfaction scores, and category diversity</li>
                  </ul>
                </div>
                <div className="info-item">
                  <h3>Part B: Ride-Sharing Matching</h3>
                  <ul>
                    <li><strong>Algorithm:</strong> Cheapest insertion for optimal assignments</li>
                    <li><strong>Constraints:</strong> Vehicle capacity and passenger flexibility</li>
                    <li><strong>Output:</strong> Assignments with rejection reasons for failed matches</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'part-a' && <PartA />}
        {currentPage === 'part-b' && <PartB />}
      </main>

      <footer className="footer">
        <p>&copy; 2026 Intelligent Route Planning System. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;
