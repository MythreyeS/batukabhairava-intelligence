"""
MarketPulse Test Suite

This package contains all unit tests and integration tests for the trading intelligence platform.

The test suite is organized by component:
- test_agents: Tests for country-specific agents
- test_data_processing: Tests for data validation, normalization, and verification
- test_intelligence_engine: Tests for conviction scoring and recommendation generation
- test_telegram: Tests for Telegram integration

To run the tests:
    python -m unittest discover -s tests

__all__ = [
    'run_all_tests',
    'create_test_suite'
]

__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Test suite for multi-agent trading intelligence platform"

# Import test utilities
import unittest
import sys
import os

# Add project root to path for proper imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_all_tests():
    """Run all tests in the test suite"""
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result

def create_test_suite():
    """Create and return the complete test suite"""
    loader = unittest.TestLoader()
    return loader.discover('tests', pattern='test_*.py')

# Example test case for demonstration
class BasicTest(unittest.TestCase):
    """Basic test case to verify test suite setup"""
    
    def test_basic(self):
        """Test that the test suite is properly configured"""
        self.assertTrue(True, "Test suite is working")

if __name__ == "__main__":
    # Run tests when executed directly
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
