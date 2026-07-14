"""
Part B Tests: Dynamic Ride-Sharing
Tests for cheapest insertion algorithm
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.part_b import RideSharingSession

class Request:
    """Mock request object."""
    def __init__(self, id, pickup, drop, base_distance, flexibility):
        self.id = id
        self.pickup = pickup
        self.drop = drop
        self.base_distance = base_distance
        self.flexibility = flexibility

class TestPartBMandatoryTest:
    """
    Mandatory Test: Locations S, A, B, C, D with exact distance matrix
    
    Distance matrix:
         S   A   B   C   D
    S    0   4   8   6   10
    A    4   0   5   3   7
    B    8   5   0   4   2
    C    6   3   4   0   6
    D    10  7   2   6   0
    
    Capacity=2
    Request 1: A→B, base_distance=5, flexibility=3
    Request 2: C→D, base_distance=6, flexibility=2
    
    Expected final route: S → A → C → B → D
    Total distance: 13
    Request 1: A→C→B = 7 <= 8 (5+3)
    Request 2: C→B→D = 6 <= 8 (6+2)
    """
    
    def test_mandatory_test_part_b(self):
        """Test cheapest insertion with mandatory test case."""
        # Create distance matrix
        distance_matrix = {
            (0, 1): 4, (1, 0): 4,
            (0, 2): 8, (2, 0): 8,
            (0, 3): 6, (3, 0): 6,
            (0, 4): 10, (4, 0): 10,
            (1, 2): 5, (2, 1): 5,
            (1, 3): 3, (3, 1): 3,
            (1, 4): 7, (4, 1): 7,
            (2, 3): 4, (3, 2): 4,
            (2, 4): 2, (4, 2): 2,
            (3, 4): 6, (4, 3): 6,
        }
        
        # Initialize session: S=0, D=4, capacity=2
        session = RideSharingSession(source=0, destination=4, capacity=2)
        session.set_distance_matrix(distance_matrix)
        
        # Add Request 1: A(1) → B(2), base=5, flex=3
        req1 = Request(id="req1", pickup=1, drop=2, base_distance=5, flexibility=3)
        result1 = session.add_request(req1)
        
        assert result1['accepted'], f"Request 1 should be accepted, got: {result1}"
        
        # Add Request 2: C(3) → D(4), base=6, flex=2
        req2 = Request(id="req2", pickup=3, drop=4, base_distance=6, flexibility=2)
        result2 = session.add_request(req2)
        
        assert result2['accepted'], f"Request 2 should be accepted, got: {result2}"
        
        # Verify final route
        assert session.route == [0, 1, 3, 2, 4], \
            f"Expected route [0, 1, 3, 2, 4] (S→A→C→B→D), got {session.route}"
        
        # Verify total distance
        expected_distance = 4 + 3 + 4 + 2  # S→A: 4, A→C: 3, C→B: 4, B→D: 2
        assert session.total_distance == pytest.approx(expected_distance), \
            f"Expected distance {expected_distance}, got {session.total_distance}"
        
        # Verify flexibility constraints
        # Request 1: A(pos 1) → B(pos 3)
        # Path: A→C→B = 3 + 4 = 7 <= 8 (base 5 + flex 3)
        actual_dist_req1 = distance_matrix[(1, 3)] + distance_matrix[(3, 2)]
        assert actual_dist_req1 <= 5 + 3, \
            f"Request 1 flexibility violated: {actual_dist_req1} > {5 + 3}"
        
        # Request 2: C(pos 2) → D(pos 4)
        # Path: C→B→D = 4 + 2 = 6 <= 8 (base 6 + flex 2)
        actual_dist_req2 = distance_matrix[(3, 2)] + distance_matrix[(2, 4)]
        assert actual_dist_req2 <= 6 + 2, \
            f"Request 2 flexibility violated: {actual_dist_req2} > {6 + 2}"
        
        # Verify capacity never exceeded
        # S: 0 passengers
        # A: +1 (pickup) = 1 passenger
        # C: +1 (pickup) = 2 passengers
        # B: -1 (dropoff req1) +1 (dropoff req2) = 2 passengers (wait, req2 drops at D)
        # Actually: B has -1 (dropoff req1) = 1 passenger
        # D: -1 (dropoff req2) = 0 passengers
        
        # Let me recalculate: req1 is A→B, req2 is C→D
        # Route: S → A → C → B → D
        # At S: 0 passengers
        # At A: +1 (req1 pickup) = 1
        # At C: +1 (req2 pickup) = 2
        # At B: -1 (req1 dropoff) = 1
        # At D: -1 (req2 dropoff) = 0
        # Max capacity: 2 ✓

class TestPartBFlexibilityConstraint:
    """Test flexibility constraint enforcement."""
    
    def test_flexibility_exceeded(self):
        """Test that requests exceeding flexibility are rejected."""
        distance_matrix = {
            (0, 1): 1, (1, 0): 1,
            (0, 2): 1, (2, 0): 1,
            (0, 3): 1, (3, 0): 1,
            (1, 2): 10, (2, 1): 10,  # Long detour
            (1, 3): 1, (3, 1): 1,
            (2, 3): 1, (3, 2): 1,
        }
        
        session = RideSharingSession(source=0, destination=3, capacity=2)
        session.set_distance_matrix(distance_matrix)
        
        # Add request with tight flexibility
        req1 = Request(id="req1", pickup=1, drop=2, base_distance=1, flexibility=1)
        result1 = session.add_request(req1)
        assert not result1['accepted']
        assert result1['reason'] == 'flexibility'

class TestPartBVehicleDepartedIndex:
    """Test vehicle_departed_index tracking."""
    
    def test_vehicle_departed_index_advance(self):
        """Test that vehicle_departed_index advances correctly."""
        distance_matrix = {
            (0, 1): 1, (1, 0): 1,
            (0, 2): 1, (2, 0): 1,
            (1, 2): 1, (2, 1): 1,
        }
        
        session = RideSharingSession(source=0, destination=2, capacity=2)
        session.set_distance_matrix(distance_matrix)
        
        assert session.vehicle_departed_index == 0
        
        session.advance()
        assert session.vehicle_departed_index == 1
        
        session.advance()
        assert session.vehicle_departed_index == 2

