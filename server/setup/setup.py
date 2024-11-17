from .data import assert_or_get_training_data
from .admin import create_admin_user

# Setup function that is run when the server starts
def setup():
    create_admin_user("admin", "admin", 20, "male")
    assert_or_get_training_data()
    print("Setup complete")