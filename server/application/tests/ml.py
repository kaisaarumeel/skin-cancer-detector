# Contributors:
# * Contributor: <alexandersafstrom@proton.me>
from django.test import TestCase

# Use a symlinked ML module to trick Django
from ..mlsym.train import train


class MLTests(TestCase):
    # Setup the tests
    def setUp(self):
        super().setUp()

    # Test the ML pipeline
    def test_ml_pipeline(self):
        try:
            # Run training in test mode
            train(test=True)
            test_passed = True
        except Exception as e:
            test_passed = False
            print(f"> MLTEST ERROR: {str(e)}")

        self.assertTrue(
            test_passed,
            "ML Pipeline validation has failed. Please review the code... :()",
        )

    # Add some teardown here later if needed
    def tearDown(self):
        pass
