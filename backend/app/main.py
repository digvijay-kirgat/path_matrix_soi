"""
Intelligent Route Planning & Adaptive Optimization System
Main FastAPI application with Part A and Part B endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import uuid

# Import Part A and Part B modules
from . import part_a, part_b

app = FastAPI(
    title="Route Planning API",
    description="Sightseeing Route Optimizer and Dynamic Ride-Sharing System",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PART A: Sightseeing Route Optimizer
# ============================================================================

class Location(BaseModel):
    id: int
    name: str
    category: str
    score: float
    lat: float
    lon: float

class PartARequest(BaseModel):
    locations: List[Location]
    max_budget: float
    category_threshold: int
    k_decay: float = 0.1

class PerStopBreakdown(BaseModel):
    id: int
    base_score: float
    decay_factor: float
    penalty_factor: float
    effective_score: float
    cumulative_distance: float

class PartAResponse(BaseModel):
    route: List[int]
    total_distance: float
    total_effective_satisfaction: float
    runtime_ms: float
    per_stop_breakdown: List[PerStopBreakdown]

@app.post("/api/part-a/optimize", response_model=PartAResponse)
async def optimize_route(request: PartARequest):
    """
    Optimize a sightseeing route using beam search and simulated annealing.
    
    Input:
    - locations: List of Location objects (index 0 = start, last = destination)
    - max_budget: Maximum total distance allowed
    - category_threshold: Threshold for applying category penalty
    - k_decay: Decay constant for distance-based score reduction
    
    Output:
    - route: Ordered list of location IDs
    - total_distance: Total distance of the route
    - total_effective_satisfaction: Sum of effective scores
    - runtime_ms: Computation time in milliseconds
    - per_stop_breakdown: Detailed scoring for each stop
    """
    start_time = time.time()
    
    try:
        result = part_a.optimize_route(
            locations=request.locations,
            max_budget=request.max_budget,
            category_threshold=request.category_threshold,
            k_decay=request.k_decay
        )
        
        runtime_ms = (time.time() - start_time) * 1000
        
        # Convert breakdown to response format
        breakdown = [
            PerStopBreakdown(
                id=item['id'],
                base_score=item['base_score'],
                decay_factor=item['decay_factor'],
                penalty_factor=item['penalty_factor'],
                effective_score=item['effective_score'],
                cumulative_distance=item['cumulative_distance']
            )
            for item in result['breakdown']
        ]
        
        return PartAResponse(
            route=result['route'],
            total_distance=result['total_distance'],
            total_effective_satisfaction=result['total_effective_satisfaction'],
            runtime_ms=runtime_ms,
            per_stop_breakdown=breakdown
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# PART B: Dynamic Ride-Sharing
# ============================================================================

class Request(BaseModel):
    id: str
    pickup: int  # location_id
    drop: int    # location_id
    base_distance: float
    flexibility: float

class PartBInitRequest(BaseModel):
    source: int
    destination: int
    capacity: int

class PartBRequestRequest(BaseModel):
    session_id: str
    request: Request

class PassengerCount(BaseModel):
    route_index: int
    location_id: int
    count: int

class PartBRequestResponse(BaseModel):
    accepted: bool
    route: List[int]
    total_distance: float
    passenger_counts: List[PassengerCount]
    reason_if_rejected: Optional[str]
    runtime_ms: float

class PartBStateResponse(BaseModel):
    session_id: str
    route: List[int]
    manifest: List[dict]
    rejected_log: List[dict]
    vehicle_departed_index: int
    total_distance: float

# In-memory session storage (for demo; use database in production)
_sessions = {}

@app.post("/api/part-b/init")
async def init_ride_sharing(request: PartBInitRequest):
    """Initialize a new ride-sharing session."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = part_b.RideSharingSession(
        source=request.source,
        destination=request.destination,
        capacity=request.capacity
    )
    return {"session_id": session_id}

@app.post("/api/part-b/request", response_model=PartBRequestResponse)
async def add_ride_request(request: PartBRequestRequest):
    """Add a new ride request to an active session."""
    start_time = time.time()
    
    if request.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _sessions[request.session_id]
    result = session.add_request(request.request)
    
    runtime_ms = (time.time() - start_time) * 1000
    
    passenger_counts = [
        PassengerCount(
            route_index=idx,
            location_id=loc_id,
            count=count
        )
        for idx, (loc_id, count) in enumerate(session.get_passenger_counts().items())
    ]
    
    return PartBRequestResponse(
        accepted=result['accepted'],
        route=session.route,
        total_distance=session.total_distance,
        passenger_counts=passenger_counts,
        reason_if_rejected=result.get('reason'),
        runtime_ms=runtime_ms
    )

@app.post("/api/part-b/advance")
async def advance_vehicle(session_id: str):
    """Advance the vehicle_departed_index by one stop."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _sessions[session_id]
    session.advance()
    
    return {"success": True, "vehicle_departed_index": session.vehicle_departed_index}

@app.get("/api/part-b/state", response_model=PartBStateResponse)
async def get_ride_state(session_id: str):
    """Get the current state of a ride-sharing session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = _sessions[session_id]
    
    return PartBStateResponse(
        session_id=session_id,
        route=session.route,
        manifest=session.manifest,
        rejected_log=session.rejected_log,
        vehicle_departed_index=session.vehicle_departed_index,
        total_distance=session.total_distance
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
