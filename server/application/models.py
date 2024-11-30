from django.contrib.auth.models import AbstractUser
from django.db import models

# Documentation references:
# https://docs.djangoproject.com/en/5.1/topics/db/models/
# https://docs.djangoproject.com/en/5.1/ref/models/fields/


class Data(models.Model):
    image_id = models.TextField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    image = models.BinaryField(blank=False, null=False)
    age = models.IntegerField(null=True)

    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, null=False)

    LOCALIZATION_CHOICES = [
        # Head and Neck region
        ("ear", "Ear"),
        ("face", "Face"),
        ("neck", "Neck"),
        ("scalp", "Scalp"),
        # Trunk region
        ("abdomen", "Abdomen"),
        ("back", "Back"),
        ("chest", "Chest"),
        ("trunk", "Trunk - Other"),
        # Upper limbs
        ("acral", "Acral (Fingers/Toes)"),
        ("hand", "Hand"),
        ("upper_extremity", "Upper Extremity (Arm)"),
        # Lower limbs
        ("foot", "Foot"),
        ("lower_extremity", "Lower Extremity (Leg)"),
        # Other locations
        ("genital", "Genital Area"),
    ]
    localization = models.CharField(
        max_length=15, choices=LOCALIZATION_CHOICES, null=True
    )

    LESION_TYPE_CHOICES = [
        # Benign lesions
        ("nv", "Melanocytic nevi"),
        ("bkl", "Benign keratosis-like lesions"),
        ("df", "Dermatofibroma"),
        ("vasc", "Vascular lesions"),
        # Malignant/Potentially Malignant lesions
        ("mel", "Melanoma"),
        ("bcc", "Basal cell carcinoma"),
        ("akiec", "Actinic keratoses and intraepithelial carcinoma"),
    ]
    lesion_type = models.CharField(
        max_length=5, choices=LESION_TYPE_CHOICES, blank=False, null=False
    )

    class Meta:
        managed = True
        db_table = "images"


class Model(models.Model):
    version = models.AutoField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    weights = models.BinaryField(null=False)
    hyperparameters = models.TextField(default="default", null=False, blank=False)

    class Meta:
        managed = True
        db_table = "models"


class ActiveModel(models.Model):
    model = models.OneToOneField(
        Model,
        on_delete=models.CASCADE,
    )
    updated_at = models.IntegerField(null=False, blank=False)

    class Meta:
        managed = True
        db_table = "model_active"
        constraints = [
            models.CheckConstraint(
                check=models.Q(id=1),  # ensure primary key is always 1
                name="single_active_model_constraint",
            )
        ]

    # override default save method to prevent multiple active models
    # supplements the 1-row constraint to ensure data integrity
    def save(self, *args, **kwargs):
        # prevents creation of a second row if it doesn't exist yet
        # allows updating existing model by checking primary keys
        if not self.pk and ActiveModel.objects.exists():
            raise ValueError("Only one active model entry is allowed.")
        super().save(*args, **kwargs)


# This class inherits from the AbstractUser class, which is a built-in
# Django model that provides basic fields for user authentication
# and authorization. We override the email, first_name, and last_name
# fields inherited from AbstractUser, and add custom fields for our
# application. We inherit it to reduce repetition.
class Users(AbstractUser):

    username = models.CharField(max_length=150, unique=True, primary_key=True)

    # Overriding the email, first_name, last_name fields
    # inherited from AbstractUser
    email = None
    first_name = None
    last_name = None

    is_admin = models.BooleanField(default=False)

    age = models.IntegerField(null=False, blank=False)

    SEX_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, null=False, blank=False)

    # Since our model is a subclass of AbstractUser, we need to
    # relate it to the Group and Permission models but with
    # different related names
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="skinscan_user_set",
        related_query_name="skinscan_user",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="skinscan_user_set",
        related_query_name="skinscan_user",
    )

    # Specify required fields for createsuperuser command
    REQUIRED_FIELDS = ["age", "sex"]
    # USERNAME_FIELD is already 'username' by default

    class Meta:
        managed = True
        db_table = "users"


class Requests(models.Model):
    request_id = models.AutoField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    probability = models.IntegerField(blank=True, null=True)
    image = models.BinaryField(blank=False, null=False)

    LOCALIZATION_CHOICES = [
        # Head and Neck region
        ("ear", "Ear"),
        ("face", "Face"),
        ("neck", "Neck"),
        ("scalp", "Scalp"),
        # Trunk region
        ("abdomen", "Abdomen"),
        ("back", "Back"),
        ("chest", "Chest"),
        ("trunk", "Trunk - Other"),
        # Upper limbs
        ("acral", "Acral (Fingers/Toes)"),
        ("hand", "Hand"),
        ("upper_extremity", "Upper Extremity (Arm)"),
        # Lower limbs
        ("foot", "Foot"),
        ("lower_extremity", "Lower Extremity (Leg)"),
        # Other locations
        ("genital", "Genital Area"),
    ]
    localization = models.CharField(
        max_length=15,
        choices=LOCALIZATION_CHOICES,
        blank=False,
        null=False,
    )

    LESION_TYPE_CHOICES = [
        # Benign lesions
        ("nv", "Melanocytic nevi"),
        ("bkl", "Benign keratosis-like lesions"),
        ("df", "Dermatofibroma"),
        ("vasc", "Vascular lesions"),
        # Malignant/Potentially Malignant lesions
        ("mel", "Melanoma"),
        ("bcc", "Basal cell carcinoma"),
        ("akiec", "Actinic keratoses and intraepithelial carcinoma"),
    ]
    lesion_type = models.CharField(
        max_length=5,
        choices=LESION_TYPE_CHOICES,
        blank=False,
        null=False,
    )

    # Foreign Keys
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    # Sets the foreign key to be the Model version column, so that the model version
    # used for the prediction can be found even if the Model itself is deleted
    model = models.ForeignKey(
        Model, on_delete=models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = True
        db_table = "requests"
