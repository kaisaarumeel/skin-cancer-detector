from setup.data import assert_or_get_training_data

# Setup function that is run when the server starts
def setup():
    assert_or_get_training_data()
    print("Setup complete")