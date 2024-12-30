# Contributors:
# * Contributor: <elindstr@student.chalmers.se>
from django.conf import settings


def get_secondary_db_name():
    """Returns the name of the second database defined in the Django settings.
    \nNote: this function assumes there are only two databases defined"""

    # Iterate over the keys in the DATABASES dictionary from project settings
    # Wrap the DB names that are not the default in a list
    db_names = [db_name for db_name in settings.DATABASES if db_name != "default"]

    # If the list is not empty, return the first element
    if db_names:
        return db_names[0]

    # Otherwise return None
    return None
