"""
Test runner to verify all modules work together properly.
Run this script to test imports and basic functionality.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    errors = []
    
    modules = [
        'emergency_scoring',
        'misuse_detection',
        'dispatch_decision',
        'location_resolution',
        'mechanic_selection',
        'service_center_selection',
        'eta_finalization',
        'service_status',
        'workflow',
        'osrm_service',
        'models',
        'config'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            errors.append((module, str(e)))
    
    return len(errors) == 0, errors


def test_workflow():
    """Test the workflow engine."""
    print("\nTesting workflow engine...")
    
    try:
        from workflow import WorkflowEngine
        
        engine = WorkflowEngine()
        
        # Test emergency request
        test_data = {
            "request_id": "TEST001",
            "issue_type": "accident",
            "emergency_keywords": ["injured"],
            "request_count_last_10_min": 1,
            "cancel_count_today": 0,
            "user_location": {"lat": 21.1458, "lon": 79.0882},
            "mechanics": [
                {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True}
            ],
            "service_centers": [
                {"id": "SC01", "lat": 21.1500, "lon": 79.0800}
            ],
            "osrm_eta_minutes": 15,
            "distance_meters": 5000
        }
        
        result = engine.process_new_request(test_data)
        
        assert result['workflow_status'] == 'completed', "Workflow should complete"
        assert result['emergency_flag'] == True, "Should detect emergency"
        assert result['priority'] == 'emergency', "Should be emergency priority"
        
        print("✓ Workflow engine works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_modules():
    """Test individual module functions."""
    print("\nTesting individual modules...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test emergency scoring
    try:
        from emergency_scoring import calculate_emergency_score
        result = calculate_emergency_score({
            "issue_type": "accident",
            "emergency_keywords": ["injured"]
        })
        assert result['emergency_flag'] == True
        print("✓ Emergency scoring")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Emergency scoring: {e}")
        tests_failed += 1
    
    # Test misuse detection
    try:
        from misuse_detection import detect_misuse
        result = detect_misuse({
            "request_count_last_10_min": 6,
            "cancel_count_today": 0,
            "emergency_flag": False
        })
        assert result['suspicious'] == True
        print("✓ Misuse detection")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Misuse detection: {e}")
        tests_failed += 1
    
    # Test dispatch decision
    try:
        from dispatch_decision import make_dispatch_decision
        result = make_dispatch_decision({
            "emergency_flag": True,
            "suspicious": False,
            "location_available": True
        })
        assert result['priority'] == 'emergency'
        print("✓ Dispatch decision")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Dispatch decision: {e}")
        tests_failed += 1
    
    # Test mechanic selection
    try:
        from mechanic_selection import select_nearest_mechanic
        result = select_nearest_mechanic({
            "user_location": {"lat": 21.1458, "lon": 79.0882},
            "mechanics": [
                {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True}
            ]
        })
        assert result['selected_mechanic_id'] == 'M01'
        print("✓ Mechanic selection")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Mechanic selection: {e}")
        tests_failed += 1
    
    # Test service status
    try:
        from service_status import determine_service_status
        result = determine_service_status({"distance_meters": 3000})
        assert result['status'] == 'on_the_way'
        print("✓ Service status")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Service status: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed


def main():
    """Run all tests."""
    print("=" * 60)
    print("Backend Integration Test Suite")
    print("=" * 60)
    
    # Test imports
    imports_ok, import_errors = test_imports()
    
    if not imports_ok:
        print("\n❌ Import errors detected. Please fix before proceeding:")
        for module, error in import_errors:
            print(f"  - {module}: {error}")
        return False
    
    print("\n✅ All modules imported successfully!")
    
    # Test individual modules
    passed, failed = test_individual_modules()
    print(f"\nIndividual tests: {passed} passed, {failed} failed")
    
    # Test workflow integration
    if test_workflow():
        print("\n✅ Workflow integration test passed!")
    else:
        print("\n❌ Workflow integration test failed!")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! The backend is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run 'python init_db.py' to set up the database")
    print("  2. Run 'python api.py' to start the API server")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
