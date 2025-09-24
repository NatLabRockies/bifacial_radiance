#!/usr/bin/env python3
"""
Test script to verify pyradiance integration in bifacial_radiance

This script tests the basic functionality to ensure pyradiance is properly
integrated and can be used as a replacement for subprocess calls.
"""

import sys
import os

# Add the bifacial_radiance path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bifacial_radiance'))

def test_pyradiance_import():
    """Test if pyradiance can be imported and is available"""
    print("Testing pyradiance import...")
    
    try:
        from bifacial_radiance.main import PYRADIANCE_AVAILABLE
        print(f"PYRADIANCE_AVAILABLE = {PYRADIANCE_AVAILABLE}")
        
        if PYRADIANCE_AVAILABLE:
            import pyradiance
            print(f"PyRadiance version info: {pyradiance.__file__}")
            print("✓ PyRadiance is available and can be imported")
            return True
        else:
            print("⚠ PyRadiance is not available - will use subprocess fallback")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import pyradiance functionality: {e}")
        return False

def test_basic_radiance_functions():
    """Test basic RADIANCE function availability in pyradiance"""
    print("\nTesting basic RADIANCE functions availability...")
    
    try:
        import pyradiance
        
        # Test if key functions are available
        functions_to_test = [
            'oconv', 'rpict', 'rtrace', 'falsecolor', 
            'gendaylit', 'gensky', 'pvalue'
        ]
        
        available_functions = []
        missing_functions = []
        
        for func_name in functions_to_test:
            if hasattr(pyradiance, func_name):
                available_functions.append(func_name)
                print(f"✓ {func_name} is available")
            else:
                missing_functions.append(func_name)
                print(f"✗ {func_name} is NOT available")
        
        print(f"\nSummary: {len(available_functions)}/{len(functions_to_test)} functions available")
        return len(available_functions) > 0
        
    except ImportError:
        print("✗ Cannot test functions - pyradiance not available")
        return False

def test_bifacial_radiance_import():
    """Test if bifacial_radiance can be imported with pyradiance integration"""
    print("\nTesting bifacial_radiance import with pyradiance integration...")
    
    try:
        import bifacial_radiance
        print("✓ bifacial_radiance imported successfully")
        
        # Test if we can create a RadianceObj
        demo = bifacial_radiance.RadianceObj('test')
        print("✓ RadianceObj created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to import bifacial_radiance: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Testing PyRadiance Integration in Bifacial_Radiance")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_pyradiance_import()
    test2_passed = test_basic_radiance_functions() if test1_passed else False
    test3_passed = test_bifacial_radiance_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"PyRadiance Import: {'PASS' if test1_passed else 'FAIL'}")
    print(f"RADIANCE Functions: {'PASS' if test2_passed else 'FAIL/SKIP'}")
    print(f"Bifacial_Radiance Integration: {'PASS' if test3_passed else 'FAIL'}")
    
    if test1_passed and test3_passed:
        print("\n✓ Integration tests PASSED - PyRadiance integration is working!")
        if not test2_passed:
            print("⚠ Some RADIANCE functions may not be available - fallback will be used")
    else:
        print("\n✗ Integration tests FAILED - check installation")
    
    return test1_passed and test3_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)