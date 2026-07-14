"""
Part B: Dynamic Ride-Sharing
Implements cheapest insertion algorithm with correctness fixes
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class RideSharingSession:
    """
    Manages a single ride-sharing session with cheapest insertion algorithm.
    """
    source: int
    destination: int
    capacity: int
    
    route: List[int] = field(default_factory=list)
    manifest: List[Dict] = field(default_factory=list)
    rejected_log: List[Dict] = field(default_factory=list)
    vehicle_departed_index: int = 0
    total_distance: float = 0.0
    distance_matrix: Dict[Tuple[int, int], float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize route with source and destination."""
        self.route = [self.source, self.destination]
        self.total_distance = self.distance_matrix.get((self.source, self.destination), 0.0)
    
    def set_distance_matrix(self, matrix: Dict[Tuple[int, int], float]):
        """Set the distance matrix for all location pairs."""
        self.distance_matrix = matrix
    
    def add_request(self, request) -> Dict:
        """
        Add a new ride request using cheapest insertion algorithm.
        
        Returns: {'accepted': bool, 'reason': optional_rejection_reason}
        """
        pickup_id = request.pickup
        drop_id = request.drop
        base_distance = request.base_distance
        flexibility = request.flexibility
        request_id = request.id
        
        # Try every (i, j) insertion pair starting from vehicle_departed_index + 1
        best_cost = float('inf')
        best_insertion = None
        
        start_search = self.vehicle_departed_index + 1
        
        for i in range(start_search, len(self.route)):
            for j in range(i, len(self.route)):
                # Try inserting pickup at position i and drop at position j
                candidate_route = self._try_insertion(pickup_id, drop_id, i, j)
                
                if candidate_route is None:
                    continue
                
                # Validate candidate
                validation = self._validate_candidate(
                    candidate_route, pickup_id, drop_id, base_distance, flexibility, request_id
                )
                
                if not validation['valid']:
                    continue
                
                # Calculate added distance
                added_distance = validation['added_distance']
                
                if added_distance < best_cost:
                    best_cost = added_distance
                    # Find actual positions in candidate route
                    actual_pickup_pos = None
                    actual_drop_pos = None
                    for idx in range(len(candidate_route) - 1, -1, -1):
                        if candidate_route[idx] == pickup_id and actual_pickup_pos is None:
                            actual_pickup_pos = idx
                        if candidate_route[idx] == drop_id and actual_drop_pos is None:
                            actual_drop_pos = idx
                    
                    best_insertion = {
                        'route': candidate_route,
                        'pickup_pos': actual_pickup_pos,
                        'drop_pos': actual_drop_pos,
                        'added_distance': added_distance
                    }
        
        if best_insertion is None:
            # Rejection - determine reason
            reason = self._determine_rejection_reason(pickup_id, drop_id, base_distance, flexibility)
            self.rejected_log.append({
                'request_id': request_id,
                'pickup': pickup_id,
                'drop': drop_id,
                'reason': reason
            })
            return {'accepted': False, 'reason': reason}
        
        # Accept and commit
        self.route = best_insertion['route']
        self.total_distance += best_insertion['added_distance']
        
        self.manifest.append({
            'request_id': request_id,
            'pickup': pickup_id,
            'drop': drop_id,
            'pickup_pos': best_insertion['pickup_pos'],
            'drop_pos': best_insertion['drop_pos'],
            'base_distance': base_distance,
            'flexibility': flexibility
        })
        
        return {'accepted': True}
    
    def _try_insertion(self, pickup_id: int, drop_id: int, i: int, j: int) -> Optional[List[int]]:
        """
        Try inserting pickup at position i and drop at position j.
        Returns new route if valid structure, None otherwise.
        """
        if i > j:
            return None
        
        # Insert pickup at position i
        new_route = self.route[:i] + [pickup_id] + self.route[i:]
        
        # Check if drop location is already in the route
        if drop_id in new_route:
            # Drop is already in the route, don't insert it again
            return new_route
        
        # Insert drop at position j+1 in the original route indexing
        # After inserting pickup at i, all positions >= i shift by 1
        # So drop_pos in new_route = j + 1 (since j is in original indexing)
        drop_pos = j + 1
        new_route = new_route[:drop_pos] + [drop_id] + new_route[drop_pos:]
        
        return new_route
    
    def _validate_candidate(
        self,
        candidate_route: List[int],
        pickup_id: int,
        drop_id: int,
        base_distance: float,
        flexibility: float,
        request_id: str
    ) -> Dict:
        """
        Validate candidate route against constraints.
        
        Returns: {'valid': bool, 'added_distance': float}
        """
        # Find pickup and drop positions in candidate route
        # Use rfind-like logic: find the last occurrence (for newly inserted items)
        pickup_pos = None
        drop_pos = None
        for idx in range(len(candidate_route) - 1, -1, -1):
            if candidate_route[idx] == pickup_id and pickup_pos is None:
                pickup_pos = idx
            if candidate_route[idx] == drop_id and drop_pos is None:
                drop_pos = idx
        
        if pickup_pos is None or drop_pos is None:
            return {'valid': False}
        
        # Constraint 1: pickup index < drop index
        if pickup_pos >= drop_pos:
            return {'valid': False}
        
        # Constraint 2: capacity never exceeded at any point
        # Build passenger delta map
        passenger_delta = {}
        for item in self.manifest:
            pickup_p = item['pickup_pos']
            drop_p = item['drop_pos']
            
            if pickup_p not in passenger_delta:
                passenger_delta[pickup_p] = 0
            if drop_p not in passenger_delta:
                passenger_delta[drop_p] = 0
            
            passenger_delta[pickup_p] += 1
            passenger_delta[drop_p] -= 1
        
        # Add new request to delta map
        if pickup_pos not in passenger_delta:
            passenger_delta[pickup_pos] = 0
        if drop_pos not in passenger_delta:
            passenger_delta[drop_pos] = 0
        
        passenger_delta[pickup_pos] += 1
        passenger_delta[drop_pos] -= 1
        
        # Walk route once, applying deltas
        current_passengers = 0
        for idx in range(len(candidate_route)):
            if idx in passenger_delta:
                current_passengers += passenger_delta[idx]
            
            if current_passengers > self.capacity:
                return {'valid': False}
        
        # Constraint 3: flexibility constraint
        # Calculate actual traveled distance between pickup and drop
        actual_distance = 0.0
        for k in range(pickup_pos, drop_pos):
            actual_distance += self._get_distance(candidate_route[k], candidate_route[k + 1])
        
        if actual_distance > base_distance + flexibility:
            return {'valid': False}
        
        # Calculate added distance
        old_distance = self.total_distance
        new_distance = self._calculate_route_distance(candidate_route)
        added_distance = new_distance - old_distance
        
        return {'valid': True, 'added_distance': added_distance}
    
    def _get_distance(self, from_id: int, to_id: int) -> float:
        """Get distance between two locations."""
        key = (from_id, to_id)
        if key in self.distance_matrix:
            return self.distance_matrix[key]
        # Symmetric distance
        key = (to_id, from_id)
        if key in self.distance_matrix:
            return self.distance_matrix[key]
        return 0.0
    
    def _calculate_route_distance(self, route: List[int]) -> float:
        """Calculate total distance for a route."""
        total = 0.0
        for i in range(len(route) - 1):
            total += self._get_distance(route[i], route[i + 1])
        return total
    
    def _determine_rejection_reason(
        self, pickup_id: int, drop_id: int, base_distance: float, flexibility: float
    ) -> str:
        """Determine the specific reason for rejection."""
        # Try all possible insertions to find the best rejection reason
        for i in range(self.vehicle_departed_index + 1, len(self.route)):
            for j in range(i, len(self.route)):
                candidate_route = self._try_insertion(pickup_id, drop_id, i, j)
                if candidate_route is None:
                    continue
                
                # Check capacity
                passenger_delta = {}
                for item in self.manifest:
                    pickup_p = item['pickup_pos']
                    drop_p = item['drop_pos']
                    if pickup_p not in passenger_delta:
                        passenger_delta[pickup_p] = 0
                    if drop_p not in passenger_delta:
                        passenger_delta[drop_p] = 0
                    passenger_delta[pickup_p] += 1
                    passenger_delta[drop_p] -= 1
                
                pickup_pos = candidate_route.index(pickup_id)
                drop_pos = candidate_route.index(drop_id)
                if pickup_pos not in passenger_delta:
                    passenger_delta[pickup_pos] = 0
                if drop_pos not in passenger_delta:
                    passenger_delta[drop_pos] = 0
                passenger_delta[pickup_pos] += 1
                passenger_delta[drop_pos] -= 1
                
                current_passengers = 0
                capacity_exceeded = False
                for idx in range(len(candidate_route)):
                    if idx in passenger_delta:
                        current_passengers += passenger_delta[idx]
                    if current_passengers > self.capacity:
                        capacity_exceeded = True
                        break
                
                if capacity_exceeded:
                    return "capacity"
                
                # Check flexibility
                actual_distance = 0.0
                for k in range(pickup_pos, drop_pos):
                    actual_distance += self._get_distance(candidate_route[k], candidate_route[k + 1])
                
                if actual_distance > base_distance + flexibility:
                    return "flexibility"
        
        return "no_valid_slot"
    
    def advance(self):
        """Advance vehicle_departed_index by one stop."""
        self.vehicle_departed_index += 1
    
    def get_passenger_counts(self) -> Dict[int, int]:
        """
        Get passenger count at each route index.
        Returns dict mapping location_id to passenger count.
        """
        counts = {}
        current_passengers = 0
        
        for idx, location_id in enumerate(self.route):
            # Count pickups and dropoffs at this index
            for item in self.manifest:
                if item['pickup_pos'] == idx:
                    current_passengers += 1
                if item['drop_pos'] == idx:
                    current_passengers -= 1
            
            counts[location_id] = current_passengers
        
        return counts
