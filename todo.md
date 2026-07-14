# Intelligent Route Planning & Adaptive Optimization System - TODO

## Phase 1: Project Skeleton & Setup
- [x] Create backend requirements.txt with FastAPI, pytest, numpy, scipy
- [ ] Create frontend package.json with React, Vite, Leaflet
- [x] Set up .gitignore for Python and Node
- [x] Create main.py FastAPI app structure
- [ ] Create Vite React app structure

## Phase 2: Part A Backend (Beam Search + Simulated Annealing)
- [x] Implement haversine distance calculation
- [x] Implement distance matrix computation
- [x] Implement effective score calculation with decay and penalty
- [x] Implement beam search algorithm (Stage 1)
- [x] Implement simulated annealing algorithm (Stage 2)
- [x] Create POST /api/part-a/optimize endpoint
- [x] Test endpoint with manual requests

## Phase 3: Part A Tests
- [x] Implement test_part_a.py with Test 1 (College→Beach, historical/nature mix)
- [x] Implement test_part_a.py with Test 2 (City Center→Hill View, food/nature mix)
- [x] Verify penalty factor application (0.9 for over-threshold visits)
- [x] Verify decay factor application (exp(-k*distance))
- [x] Run all Part A tests and ensure they pass

## Phase 4: Part B Backend (Cheapest Insertion)
- [x] Implement cheapest insertion algorithm
- [x] Implement vehicle_departed_index tracking
- [x] Implement passenger count validation
- [x] Implement flexibility constraint validation
- [x] Create POST /api/part-b/init endpoint
- [x] Create POST /api/part-b/request endpoint
- [x] Create POST /api/part-b/advance endpoint
- [x] Create GET /api/part-b/state endpoint
- [x] Implement rejected request logging with reasons

## Phase 5: Part B Tests
- [x] Implement test_part_b.py with mandatory test case (S→A→C→B→D)
- [x] Verify distance matrix handling
- [x] Verify capacity constraints
- [x] Verify flexibility constraints (actual_distance <= base_distance + flexibility)
- [x] Verify route correctness (S→A→C→B→D with distance=13)
- [x] Run all Part B tests and ensure they pass

## Phase 6: Frontend Development
- [x] Create Part A page (PartA.jsx) with form for locations
- [x] Create Part B page (PartB.jsx) with form for requests
- [x] Integrate Leaflet.js map component for Part A
- [x] Integrate Leaflet.js map component for Part B
- [x] Implement results table for Part A (breakdown, distance, satisfaction)
- [x] Implement results table for Part B (passenger counts, accepted/rejected log)
- [x] Add runtime display (ms) for both pages
- [x] Style both pages with clean CSS
- [x] Create App.jsx with routing to both pages

## Completed Milestones
- [x] Frontend React app scaffolded
- [x] Part A and Part B pages created
- [x] Leaflet maps integrated into both pages
- [x] Frontend styling applied

## Phase 7: Documentation
- [x] Write README.md with algorithm descriptions
- [x] Document all API endpoints in README
- [x] Document complexity notes for Part B
- [x] Document how to run backend locally
- [x] Document how to run frontend locally
- [x] Document how to run tests
- [x] Document known limitations

## Phase 8: Deployment
- [x] Create deployment guide for Render/Railway + Vercel/Netlify
- [x] Create .env.example file
- [ ] Deploy backend to Render or Railway (user action)
- [ ] Deploy frontend to Vercel or Netlify (user action)
- [ ] Verify both deployments work (user action)
- [ ] Update README with deployed URLs (user action)

## Completed Milestones
- [x] Project directory structure created
- [x] Git repository initialized
- [x] Backend requirements.txt created
- [x] .gitignore configured
- [x] FastAPI main.py with Part A and Part B endpoints created
- [x] Part A implementation (beam search + simulated annealing) complete
- [x] Part B implementation (cheapest insertion) complete
- [x] Python dependencies installed
