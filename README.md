# Intelligent Route Planning & Adaptive Optimization System

This project implements a full-stack web application for intelligent route planning and dynamic ride-sharing. The backend is built with FastAPI (Python) and the frontend with React. It features two main functional parts:

- **Part A: Sightseeing Route Optimizer:** Optimizes a list of attractions for visiting order using a combination of beam search and simulated annealing, considering location categories, scores, and travel distances.
- **Part B: Dynamic Ride-Sharing:** Matches ride requests to available drivers using a cheapest insertion algorithm, optimizing vehicle utilization while respecting capacity and flexibility constraints.

## Table of Contents

1.  [Project Structure](#project-structure)
2.  [Backend API Endpoints](#backend-api-endpoints)
    *   [Part A: Sightseeing Route Optimizer](#part-a-sightseeing-route-optimizer)
    *   [Part B: Dynamic Ride-Sharing](#part-b-dynamic-ride-sharing)
3.  [Algorithm Descriptions](#algorithm-descriptions)
    *   [Part A: Sightseeing Route Optimizer](#part-a-sightseeing-route-optimizer-1)
    *   [Part B: Dynamic Ride-Sharing](#part-b-dynamic-ride-sharing-1)
4.  [Setup Instructions](#setup-instructions)
    *   [Backend Setup](#backend-setup)
    *   [Frontend Setup](#frontend-setup)
5.  [Test Execution Steps](#test-execution-steps)
    *   [Backend Tests](#backend-tests)
6.  [Known Limitations](#known-limitations)

## Project Structure

```
intelligent-route-planning/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── part_a.py       # Part A algorithms (Beam Search, Simulated Annealing)
│   │   └── part_b.py       # Part B algorithms (Cheapest Insertion)
│   ├── tests/
│   │   ├── test_part_a.py  # Tests for Part A algorithms
│   │   └── test_part_b.py  # Tests for Part B algorithms
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── MapComponent.jsx # Leaflet map component
│   │   ├── pages/
│   │   │   ├── PartA.jsx     # React page for Route Optimizer
│   │   │   └── PartB.jsx     # React page for Ride-Sharing
│   │   ├── styles/
│   │   │   ├── PartA.css     # CSS for Part A page
│   │   │   └── PartB.css     # CSS for Part B page
│   │   ├── App.css         # Global CSS for React app
│   │   ├── App.jsx         # Main React application with routing
│   │   └── main.jsx        # React entry point
│   ├── index.html
│   └── package.json        # Node.js dependencies
├── .gitignore
└── README.md
```

## Backend API Endpoints

The backend API is built with FastAPI and serves endpoints for both Part A and Part B functionalities.

### Part A: Sightseeing Route Optimizer

**POST `/api/part-a/optimize`**

Optimizes a sightseeing route based on a list of locations, a maximum budget, category thresholds, and a decay factor.

-   **Request Body:**

    ```json
    {
      "locations": [
        {
          "id": 0,
          "name": "Location A",
          "category": "historical",
          "score": 8,
          "lat": 34.0522,
          "lon": -118.2437
        }
      ],
      "max_budget": 100,
      "category_threshold": 2,
      "k_decay": 0.1
    }
    ```

    -   `locations`: An array of location objects. Each object must have `id`, `name`, `category` (e.g., "historical", "nature", "food", "cultural", "start", "destination"), `score` (0-10), `lat`, and `lon`.
    -   `max_budget`: Maximum allowed distance for the route.
    -   `category_threshold`: Maximum number of visits allowed for any single category before a penalty is applied.
    -   `k_decay`: Decay factor for satisfaction score based on distance.

-   **Response Body (Success 200):**

    ```json
    {
      "route": [
        {
          "id": 0,
          "name": "Location A",
          "category": "start",
          "score": 0,
          "lat": 34.0522,
          "lon": -118.2437
        }
      ],
      "total_distance": 50.12,
      "total_effective_satisfaction": 75.50,
      "breakdown": [
        {
          "id": 0,
          "base_score": 0,
          "decay_factor": 1.0,
          "penalty_factor": 1.0,
          "effective_score": 0,
          "cumulative_distance": 0
        }
      ]
    }
    ```

    -   `route`: The optimized sequence of locations.
    -   `total_distance`: Total distance of the optimized route in kilometers.
    -   `total_effective_satisfaction`: Total effective satisfaction score for the route.
    -   `breakdown`: Detailed breakdown of scores and distances for each stop.

### Part B: Dynamic Ride-Sharing

**POST `/api/part-b/match`**

Matches ride requests to available drivers based on a cheapest insertion algorithm, considering vehicle capacity.

-   **Request Body:**

    ```json
    {
      "requests": [
        {
          "id": 0,
          "pickup": {"lat": 34.0522, "lon": -118.2437},
          "drop": {"lat": 34.0600, "lon": -118.2500},
          "base_distance": 5,
          "flexibility": 2
        }
      ],
      "drivers": [
        {
          "id": 0,
          "location": {"lat": 34.0500, "lon": -118.2400}
        }
      ],
      "capacity": 4
    }
    ```

    -   `requests`: An array of ride request objects. Each object must have `id`, `pickup` (lat/lon), `drop` (lat/lon), `base_distance` (expected direct distance), and `flexibility` (allowed detour).
    -   `drivers`: An array of driver objects. Each object must have `id` and `location` (lat/lon).
    -   `capacity`: Maximum passenger capacity of each driver's vehicle.

-   **Response Body (Success 200):**

    ```json
    {
      "assignments": [
        {
          "request_id": 0,
          "driver_id": 0,
          "status": "assigned",
          "route": [
            {"lat": 34.0500, "lon": -118.2400},
            {"lat": 34.0522, "lon": -118.2437},
            {"lat": 34.0600, "lon": -118.2500}
          ],
          "total_distance": 10.5
        }
      ],
      "rejected_log": [
        {
          "request_id": 1,
          "reason": "capacity"
        }
      ]
    }
    ```

    -   `assignments`: An array of successful ride assignments, including the driver's optimized route and total distance.
    -   `rejected_log`: An array of rejected ride requests with their corresponding reasons (e.g., "capacity", "flexibility").

## Algorithm Descriptions

### Part A: Sightseeing Route Optimizer

The sightseeing route optimizer employs a two-stage approach to find an optimal visiting order for attractions:

1.  **Stage 1: Beam Search (Exploration)**
    -   A beam search algorithm is used to explore a wide range of promising partial routes. It maintains a fixed number (`beam_width`) of the best partial routes at each step, expanding them by adding unvisited locations. This helps in efficiently pruning less promising paths early on while retaining diversity.

2.  **Stage 2: Simulated Annealing (Refinement)**
    -   The best routes generated by the beam search are then fed into a simulated annealing algorithm. Simulated annealing is a metaheuristic that explores the solution space by making small, random changes to the current route (e.g., swapping two locations). It accepts improvements but also allows for accepting worse solutions with a certain probability, which decreases over time. This helps escape local optima and find a globally better solution.

**Scoring Mechanism:**

-   **Base Score:** Each location has a base satisfaction score.
-   **Decay Factor:** Satisfaction decays exponentially with distance from the previous stop (`exp(-k_decay * distance)`).
-   **Penalty Factor:** A penalty (0.9 multiplier) is applied if the number of visits to a specific category exceeds a predefined `category_threshold`.
-   **Total Effective Satisfaction:** The sum of effective satisfaction scores for all visited locations in the route.

### Part B: Dynamic Ride-Sharing

The dynamic ride-sharing system uses a cheapest insertion algorithm to assign ride requests to drivers.

1.  **Cheapest Insertion:**
    -   For each incoming ride request, the algorithm attempts to insert the pickup and drop-off points into all possible positions within each driver's current route. It calculates the additional distance (cost) incurred for each insertion.
    -   The request is assigned to the driver and route that results in the minimum additional distance, provided that all constraints are met.

2.  **Constraints:**
    -   **Capacity Constraint:** The number of passengers in the vehicle must not exceed the `capacity` at any point in the route.
    -   **Flexibility Constraint:** The total travel distance for a passenger (from their pickup to their drop-off) must not exceed their `base_distance` plus their `flexibility` allowance.

3.  **Rejected Requests:**
    -   If a ride request cannot be accommodated by any driver without violating capacity or flexibility constraints, it is rejected, and the reason for rejection is logged.

## Setup Instructions

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd intelligent-route-planning/backend
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd intelligent-route-planning/frontend
    ```

2.  **Install dependencies:**
    ```bash
    pnpm install
    ```

3.  **Run the React development server:**
    ```bash
    pnpm dev
    ```
    The frontend application will be available at `http://localhost:5173`.

## Test Execution Steps

### Backend Tests

1.  **Navigate to the backend directory:**
    ```bash
    cd intelligent-route-planning/backend
    ```

2.  **Run all tests using pytest:**
    ```bash
    python -m pytest tests/ -v
    ```
    This will execute all tests for both Part A and Part B algorithms and display detailed results.

## Known Limitations

-   **Scalability:** The current algorithms are designed for demonstration purposes and may not scale efficiently to very large numbers of locations or ride requests/drivers. Further optimization and more advanced algorithms would be required for production-level scalability.
-   **Real-time Data:** The system does not integrate with real-time traffic data or dynamic changes in location/driver availability. Distances are pre-calculated based on Haversine formula.
-   **Map Interactivity:** The Leaflet maps currently display routes and markers but lack advanced interactive features like drag-and-drop for locations or real-time driver movement simulation.
-   **Error Handling:** Frontend error handling is basic (using `alert()`). A more robust error display mechanism would be needed for a production application.

---

**Author:** Manus AI
**Date:** July 14, 2026
