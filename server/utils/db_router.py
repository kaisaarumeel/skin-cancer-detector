from django.conf import settings
from utils.db_lookup import get_secondary_db_name

class MigrationRouter:
    '''A router to control which models can be migrated to each database.
    \nUses the list of models defined in settings.py under IMAGE_DB_MODELS'''

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Get the list of image DB models (default value empty list)
        image_db_models = getattr(settings, "IMAGE_DB_MODELS", [])

        # If the model is in the list of image DB models, allow migration only to the image DB
        if model_name in image_db_models:
            # Returns false if the target is not the image DB, preventing the table from being added to the default DB
            return db == get_secondary_db_name()
        
        # Otherwise, attempt to migrate model to the default DB
        # Returns false if the target is not the default DB, preventing the table from being added to the image DB
        return db == "default"
