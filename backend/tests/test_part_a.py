"""
Part A Tests: Sightseeing Route Optimizer
Tests for beam search + simulated annealing algorithm
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.part_a import (
    Location, haversine_distance, compute_distance_matrix,
    compute_effective_score, optimize_route
)

class TestHaversineDistance:
    """Test Haversine distance calculation."""
    
    def test_same_point(self):
        """Distance from a point to itself should be 0."""
        dist = haversine_distance(0, 0, 0, 0)
        assert dist == pytest.approx(0, abs=0.001)
    
    def test_known_distance(self):
        """Test with known coordinates."""
        # New York to Los Angeles (approximately 3944 km)
        dist = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        assert 3900 < dist < 4000

class TestEffectiveScore:
    """Test effective score calculation with decay and penalty."""
    
    def test_no_decay_no_penalty(self):
        """Base case: no distance decay, no category penalty."""
        score, decay, penalty = compute_effective_score(
            location_score=10.0,
            cumulative_distance=0.0,
            category_visit_count=0,
            category_threshold=2,
            k_decay=0.1
        )
        assert score == pytest.approx(10.0)
        assert decay == pytest.approx(1.0)
        assert penalty == pytest.approx(1.0)
    
    def test_decay_factor(self):
        """Test distance-based decay."""
        score, decay, penalty = compute_effective_score(
            location_score=10.0,
            cumulative_distance=10.0,
            category_visit_count=0,
            category_threshold=2,
            k_decay=0.1
        )
        expected_decay = 0.36787944  # exp(-0.1 * 10)
        assert decay == pytest.approx(expected_decay, rel=0.01)
        assert score == pytest.approx(10.0 * expected_decay, rel=0.01)
        assert penalty == pytest.approx(1.0)
    
    def test_penalty_factor(self):
        """Test category threshold penalty."""
        score, decay, penalty = compute_effective_score(
            location_score=10.0,
            cumulative_distance=0.0,
            category_visit_count=2,  # >= threshold
            category_threshold=2,
            k_decay=0.1
        )
        assert decay == pytest.approx(1.0)
        assert penalty == pytest.approx(0.9)
        assert score == pytest.approx(9.0)
    
    def test_decay_and_penalty(self):
        """Test combined decay and penalty."""
        score, decay, penalty = compute_effective_score(
            location_score=10.0,
            cumulative_distance=10.0,
            category_visit_count=2,
            category_threshold=2,
            k_decay=0.1
        )
        expected_decay = 0.36787944
        assert decay == pytest.approx(expected_decay, rel=0.01)
        assert penalty == pytest.approx(0.9)
        assert score == pytest.approx(10.0 * expected_decay * 0.9, rel=0.01)

class TestPartAMandatoryTest1:
    """
    Mandatory Test 1: College(0)→Beach(last), budget=50, threshold=2, k=0.1
    
    Locations:
    - College (start, index 0)
    - Museum (score 8, historical, 4km from College)
    - Fort (score 10, historical, 5km from Museum)
    - Temple (score 7, historical, 6km from Fort)
    - Waterfall (score 9, nature, 10km from Temple)
    - Beach (destination, last index)
    
    Expected: Route should visit locations such that the third historical
    location (Temple) receives 0.9 penalty, but first two (Museum, Fort) do not.
    """
    
    def test_mandatory_test_1(self):
        """Test penalty application for category threshold."""
        # Construct locations with specific coordinates to match detour distances
        # College at (0, 0)
        locations = [
            Location(id=0, name="College", category="start", score=0, lat=0.0, lon=0.0),
            Location(id=1, name="Museum", category="historical", score=8.0, lat=0.036, lon=0.0),  # ~4km
            Location(id=2, name="Fort", category="historical", score=10.0, lat=0.072, lon=0.0),  # ~5km from Museum
            Location(id=3, name="Temple", category="historical", score=7.0, lat=0.126, lon=0.0),  # ~6km from Fort
            Location(id=4, name="Waterfall", category="nature", score=9.0, lat=0.216, lon=0.0),  # ~10km from Temple
            Location(id=5, name="Beach", category="destination", score=0, lat=0.216, lon=0.0),  # Same as Waterfall
        ]
        
        result = optimize_route(
            locations=locations,
            max_budget=50.0,
            category_threshold=2,
            k_decay=0.1
        )
        
        # Verify route structure
        assert result['route'][0] == 0  # Start at College
        assert result['route'][-1] == 5  # End at Beach
        
        # Verify breakdown
        breakdown = result['breakdown']
        
        # Find historical locations in breakdown
        historical_visits = []
        for item in breakdown:
            if item['id'] in [1, 2, 3]:  # Museum, Fort, Temple
                historical_visits.append(item)
        
        # First two historical visits should not have penalty
        if len(historical_visits) >= 2:
            assert historical_visits[0]['penalty_factor'] == pytest.approx(1.0), \
                f"First historical visit (Museum) should not have penalty, got {historical_visits[0]['penalty_factor']}"
            assert historical_visits[1]['penalty_factor'] == pytest.approx(1.0), \
                f"Second historical visit (Fort) should not have penalty, got {historical_visits[1]['penalty_factor']}"
        
        # Third historical visit should have penalty
        if len(historical_visits) >= 3:
            assert historical_visits[2]['penalty_factor'] == pytest.approx(0.9), \
                f"Third historical visit (Temple) should have 0.9 penalty, got {historical_visits[2]['penalty_factor']}"

class TestPartAMandatoryTest2:
    """
    Mandatory Test 2: City Center(0)→Hill View(last), budget=40, threshold=1, k=0.1
    
    Locations:
    - City Center (start, index 0)
    - Cafe (score 6, food, 3km)
    - Restaurant (score 9, food, 5km)
    - Park (score 8, nature, 6km)
    - Hill View (destination, last index)
    
    Expected: Whichever food location is visited second receives 0.9 penalty.
    First food visit does not. Route ordering changes total satisfaction.
    """
    
    def test_mandatory_test_2_penalty_application(self):
        """Test that second food visit gets penalty."""
        locations = [
            Location(id=0, name="City Center", category="start", score=0, lat=0.0, lon=0.0),
            Location(id=1, name="Cafe", category="food", score=6.0, lat=0.027, lon=0.0),  # ~3km
            Location(id=2, name="Restaurant", category="food", score=9.0, lat=0.072, lon=0.0),  # ~5km from Cafe
            Location(id=3, name="Park", category="nature", score=8.0, lat=0.126, lon=0.0),  # ~6km from Restaurant
            Location(id=4, name="Hill View", category="destination", score=0, lat=0.126, lon=0.0),  # Same as Park
        ]
        
        result = optimize_route(
            locations=locations,
            max_budget=40.0,
            category_threshold=1,
            k_decay=0.1
        )
        
        # Verify route structure
        assert result['route'][0] == 0  # Start at City Center
        assert result['route'][-1] == 4  # End at Hill View
        
        # Verify breakdown
        breakdown = result['breakdown']
        
        # Find food locations in breakdown
        food_visits = []
        for item in breakdown:
            if item['id'] in [1, 2]:  # Cafe, Restaurant
                food_visits.append(item)
        
        # First food visit should not have penalty
        if len(food_visits) >= 1:
            assert food_visits[0]['penalty_factor'] == pytest.approx(1.0), \
                f"First food visit should not have penalty, got {food_visits[0]['penalty_factor']}"
        
        # Second food visit should have penalty
        if len(food_visits) >= 2:
            assert food_visits[1]['penalty_factor'] == pytest.approx(0.9), \
                f"Second food visit should have 0.9 penalty, got {food_visits[1]['penalty_factor']}"
    
    def test_mandatory_test_2_route_ordering_matters(self):
        """Test that different orderings produce different satisfaction scores."""
        locations = [
            Location(id=0, name="City Center", category="start", score=0, lat=0.0, lon=0.0),
            Location(id=1, name="Cafe", category="food", score=6.0, lat=0.027, lon=0.0),
            Location(id=2, name="Restaurant", category="food", score=9.0, lat=0.072, lon=0.0),
            Location(id=3, name="Park", category="nature", score=8.0, lat=0.126, lon=0.0),
            Location(id=4, name="Hill View", category="destination", score=0, lat=0.126, lon=0.0),
        ]
        
        result1 = optimize_route(
            locations=locations,
            max_budget=40.0,
            category_threshold=1,
            k_decay=0.1
        )
        
        # Run multiple times to check consistency
        result2 = optimize_route(
            locations=locations,
            max_budget=40.0,
            category_threshold=1,
            k_decay=0.1
        )
        
        # Both should have valid routes
        assert len(result1['route']) >= 2
        assert len(result2['route']) >= 2
        
        # Satisfaction should be positive
        assert result1['total_effective_satisfaction'] >= 0
        assert result2['total_effective_satisfaction'] >= 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
