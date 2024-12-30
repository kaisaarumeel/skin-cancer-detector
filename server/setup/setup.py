# Contributors:
# * Contributor: <elindstr@student.chalmers.se>
# * Contributor: <alexandersafstrom@proton.me>
from setup.admin import create_admin_user
from setup.data import assert_or_get_training_data


# Setup function that is run when the server starts
def setup():
    create_admin_user("admin", "admin", 20, "male")
    assert_or_get_training_data()
    print("Setup complete")
