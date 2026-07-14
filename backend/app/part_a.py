"""
Part A: Sightseeing Route Optimizer
Implements beam search (Stage 1) and simulated annealing (Stage 2)
"""

import math
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Location:
    id: int
    name: str
    category: str
    score: float
    lat: float
    lon: float

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula (in km).
    """
    R = 6371  # Earth's radius in km
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def compute_distance_matrix(locations: List[Location]) -> List[List[float]]:
    """
    Compute distance matrix from location coordinates using Haversine formula.
    """
    n = len(locations)
    matrix = [[0.0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine_distance(
                locations[i].lat, locations[i].lon,
                locations[j].lat, locations[j].lon
            )
            matrix[i][j] = dist
            matrix[j][i] = dist
    
    return matrix

def compute_effective_score(
    location_score: float,
    cumulative_distance: float,
    category_visit_count: int,
    category_threshold: int,
    k_decay: float
) -> Tuple[float, float, float]:
    """
    Compute effective score with decay and penalty.
    
    Returns: (effective_score, decay_factor, penalty_factor)
    """
    decay_factor = math.exp(-k_decay * cumulative_distance)
    penalty_factor = 0.9 if category_visit_count >= category_threshold else 1.0
    effective_score = location_score * decay_factor * penalty_factor
    
    return effective_score, decay_factor, penalty_factor

def route_distance(route: List[int], distance_matrix: List[List[float]]) -> float:
    """Calculate total distance of a route."""
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i]][route[i + 1]]
    return total

def can_reach_destination(
    current_distance: float,
    current_index: int,
    next_candidate: int,
    destination_index: int,
    distance_matrix: List[List[float]],
    max_budget: float
) -> bool:
    """Check if we can reach destination after visiting next_candidate."""
    step_distance = distance_matrix[current_index][next_candidate]
    distance_to_dest = distance_matrix[next_candidate][destination_index]
    return current_distance + step_distance + distance_to_dest <= max_budget

def beam_search_stage(
    locations: List[Location],
    distance_matrix: List[List[float]],
    max_budget: float,
    category_threshold: int,
    k_decay: float
) -> List[int]:
    """
    Stage 1: Beam search to grow partial routes from start to destination.
    """
    n = len(locations)
    start_idx = 0
    dest_idx = n - 1
    
    beam_width = max(3, n // 5 + 2)
    
    # Each partial route: (route_list, cumulative_distance, category_counts_dict)
    candidates = [([start_idx], 0.0, {})]
    best_complete_route = None
    best_complete_score = -float('inf')
    
    # Grow routes step by step
    for step in range(n - 2):  # We have n-2 intermediate stops to consider
        next_candidates = []
        
        for route, cum_dist, cat_counts in candidates:
            current_idx = route[-1]
            visited = set(route)
            
            # Try adding each unvisited location
            for next_idx in range(n):
                if next_idx in visited:
                    continue
                
                # Check if we can reach destination after this candidate
                if not can_reach_destination(
                    cum_dist, current_idx, next_idx, dest_idx, distance_matrix, max_budget
                ):
                    continue
                
                step_distance = distance_matrix[current_idx][next_idx]
                new_cum_dist = cum_dist + step_distance
                
                # Update category counts
                new_cat_counts = cat_counts.copy()
                category = locations[next_idx].category
                new_cat_counts[category] = new_cat_counts.get(category, 0) + 1
                
                # Compute effective score
                cat_visit_count = new_cat_counts[category]
                eff_score, _, _ = compute_effective_score(
                    locations[next_idx].score,
                    new_cum_dist,
                    cat_visit_count,
                    category_threshold,
                    k_decay
                )
                
                # Rank by effective_score / step_distance
                if step_distance > 0:
                    rank_score = eff_score / step_distance
                else:
                    rank_score = eff_score
                
                new_route = route + [next_idx]
                next_candidates.append((new_route, new_cum_dist, new_cat_counts, rank_score))
        
        # Keep top beam_width candidates
        next_candidates.sort(key=lambda x: x[3], reverse=True)
        candidates = [
            (route, cum_dist, cat_counts)
            for route, cum_dist, cat_counts, _ in next_candidates[:beam_width]
        ]
        
        # Check for complete routes (ending at destination)
        for route, cum_dist, cat_counts in candidates:
            if route[-1] == dest_idx:
                # Calculate total score
                total_score = 0.0
                for loc_idx in route[1:-1]:  # Exclude start and destination
                    category = locations[loc_idx].category
                    cat_visit_count = cat_counts[category]
                    eff_score, _, _ = compute_effective_score(
                        locations[loc_idx].score,
                        cum_dist,  # Approximate
                        cat_visit_count,
                        category_threshold,
                        k_decay
                    )
                    total_score += eff_score
                
                if total_score > best_complete_score:
                    best_complete_score = total_score
                    best_complete_route = route
    
    # If no complete route found, try to append destination to best partial route
    if best_complete_route is None and candidates:
        best_partial = candidates[0]
        route, cum_dist, _ = best_partial
        
        # Try to reach destination
        current_idx = route[-1]
        step_distance = distance_matrix[current_idx][dest_idx]
        if cum_dist + step_distance <= max_budget:
            best_complete_route = route + [dest_idx]
        else:
            # Fallback: return start and destination only
            best_complete_route = [start_idx, dest_idx]
    
    return best_complete_route if best_complete_route else [start_idx, dest_idx]

def simulated_annealing_stage(
    locations: List[Location],
    distance_matrix: List[List[float]],
    initial_route: List[int],
    max_budget: float,
    category_threshold: int,
    k_decay: float
) -> List[int]:
    """
    Stage 2: Simulated annealing to refine the route.
    """
    n = len(locations)
    start_idx = 0
    dest_idx = n - 1
    
    current_route = initial_route[:]
    best_route = current_route[:]
    
    def compute_route_score(route: List[int]) -> float:
        """Compute total effective satisfaction for a route."""
        if len(route) < 2:
            return 0.0
        
        # Build category counts
        cat_counts = {}
        for idx in route[1:-1]:  # Exclude start and destination
            category = locations[idx].category
            cat_counts[category] = cat_counts.get(category, 0) + 1
        
        total_score = 0.0
        cum_dist = 0.0
        
        for i in range(len(route) - 1):
            cum_dist += distance_matrix[route[i]][route[i + 1]]
        
        # Recompute with cumulative distances
        cum_dist = 0.0
        for i in range(1, len(route) - 1):  # Exclude start and destination
            idx = route[i]
            category = locations[idx].category
            cat_visit_count = cat_counts[category]
            
            eff_score, _, _ = compute_effective_score(
                locations[idx].score,
                cum_dist,
                cat_visit_count,
                category_threshold,
                k_decay
            )
            total_score += eff_score
            cum_dist += distance_matrix[route[i - 1]][route[i]]
        
        return total_score
    
    current_score = compute_route_score(current_route)
    best_score = current_score
    
    T = 1.0
    alpha_high = 0.98
    alpha_low = 0.993
    max_iterations = 5000
    iteration = 0
    
    while T > 1e-6 and iteration < max_iterations:
        # Choose mutation type
        mutation_type = random.choice(['swap', 'invert', 'toggle'])
        
        if mutation_type == 'swap':
            # SWAP: swap two intermediate stops
            if len(current_route) > 3:
                i = random.randint(1, len(current_route) - 2)
                j = random.randint(1, len(current_route) - 2)
                if i != j:
                    new_route = current_route[:]
                    new_route[i], new_route[j] = new_route[j], new_route[i]
                else:
                    new_route = current_route[:]
            else:
                new_route = current_route[:]
        
        elif mutation_type == 'invert':
            # INVERT: reverse a segment of intermediate stops
            if len(current_route) > 3:
                i = random.randint(1, len(current_route) - 2)
                j = random.randint(i, len(current_route) - 2)
                new_route = current_route[:i] + current_route[i:j+1][::-1] + current_route[j+1:]
            else:
                new_route = current_route[:]
        
        else:  # toggle
            # TOGGLE: insert unvisited or remove visited
            visited = set(current_route)
            unvisited = [idx for idx in range(n) if idx not in visited]
            
            if random.random() < 0.5 and unvisited:
                # Insert unvisited
                candidate = random.choice(unvisited)
                pos = random.randint(1, len(current_route) - 1)
                new_route = current_route[:pos] + [candidate] + current_route[pos:]
            elif len(current_route) > 3:
                # Remove visited (but keep start and destination)
                pos = random.randint(1, len(current_route) - 2)
                new_route = current_route[:pos] + current_route[pos+1:]
            else:
                new_route = current_route[:]
        
        # Validate new route
        if len(new_route) < 2 or new_route[0] != start_idx or new_route[-1] != dest_idx:
            iteration += 1
            continue
        
        # Check budget constraint
        new_distance = route_distance(new_route, distance_matrix)
        if new_distance > max_budget:
            iteration += 1
            continue
        
        # Compute new score
        new_score = compute_route_score(new_route)
        delta = new_score - current_score
        
        # Metropolis-Hastings acceptance
        if delta > 0 or random.random() < math.exp(delta / T):
            current_route = new_route
            current_score = new_score
            
            if current_score > best_score:
                best_score = current_score
                best_route = current_route[:]
        
        # Update temperature
        if T > 0.1:
            T *= alpha_high
        else:
            T *= alpha_low
        
        iteration += 1
    
    return best_route

def optimize_route(locations, max_budget, category_threshold, k_decay):
    """
    Main optimization function combining beam search and simulated annealing.
    """
    # Convert input to Location objects
    loc_objects = [
        Location(
            id=loc.id,
            name=loc.name,
            category=loc.category,
            score=loc.score,
            lat=loc.lat,
            lon=loc.lon
        )
        for loc in locations
    ]
    
    n = len(loc_objects)
    if n < 2:
        raise ValueError("Need at least start and destination")
    
    # Compute distance matrix
    distance_matrix = compute_distance_matrix(loc_objects)
    
    # Stage 1: Beam Search
    best_route = beam_search_stage(
        loc_objects, distance_matrix, max_budget, category_threshold, k_decay
    )
    
    # Stage 2: Simulated Annealing
    best_route = simulated_annealing_stage(
        loc_objects, distance_matrix, best_route, max_budget, category_threshold, k_decay
    )
    
    # Compute final metrics
    total_distance = route_distance(best_route, distance_matrix)
    
    # Compute per-stop breakdown with running category counts
    breakdown = []
    cum_dist = 0.0
    total_score = 0.0
    cat_counts = {}  # Track category counts as we iterate
    
    for i, loc_idx in enumerate(best_route):
        if i == 0:
            # Start location
            breakdown.append({
                'id': loc_objects[loc_idx].id,
                'base_score': loc_objects[loc_idx].score,
                'decay_factor': 1.0,
                'penalty_factor': 1.0,
                'effective_score': 0.0,
                'cumulative_distance': 0.0
            })
        elif i == len(best_route) - 1:
            # Destination
            cum_dist += distance_matrix[best_route[i-1]][loc_idx]
            breakdown.append({
                'id': loc_objects[loc_idx].id,
                'base_score': loc_objects[loc_idx].score,
                'decay_factor': 1.0,
                'penalty_factor': 1.0,
                'effective_score': 0.0,
                'cumulative_distance': cum_dist
            })
        else:
            # Intermediate stop
            cum_dist += distance_matrix[best_route[i-1]][loc_idx]
            category = loc_objects[loc_idx].category
            
            # Get current count for this category (before incrementing)
            cat_visit_count = cat_counts.get(category, 0)
            
            eff_score, decay_factor, penalty_factor = compute_effective_score(
                loc_objects[loc_idx].score,
                cum_dist,
                cat_visit_count,
                category_threshold,
                k_decay
            )
            
            breakdown.append({
                'id': loc_objects[loc_idx].id,
                'base_score': loc_objects[loc_idx].score,
                'decay_factor': decay_factor,
                'penalty_factor': penalty_factor,
                'effective_score': eff_score,
                'cumulative_distance': cum_dist
            })
            
            # Increment category count after processing
            cat_counts[category] = cat_counts.get(category, 0) + 1
            total_score += eff_score
    
    return {
        'route': best_route,
        'total_distance': total_distance,
        'total_effective_satisfaction': total_score,
        'breakdown': breakdown
    }
