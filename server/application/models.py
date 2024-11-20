from django.contrib.auth.models import AbstractUser
from django.db import models

# Documentation references:
# https://docs.djangoproject.com/en/5.1/topics/db/models/
# https://docs.djangoproject.com/en/5.1/ref/models/fields/


class Data(models.Model):
    image_id = models.TextField(primary_key=True)
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
    model_id = models.AutoField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    version = models.CharField(max_length=50, unique=True)
    weights = models.BinaryField(null=False)

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    # additional CNN hyperparameters
    input_shape = models.CharField(max_length=20, default="(28, 28, 3)")
    num_filters = models.IntegerField(default=20)  # number of filters in Conv2D layer
    kernel_size = models.IntegerField(default=3)  # kernel size of Conv2D layer
    pool_size = models.IntegerField(default=2)  # pool size for MaxPooling2D
    dropout_rate = models.FloatField(default=0.1)  # dropout rate
    dense_units = models.IntegerField(default=10)  # units in dense layer

    ACTIVATION_CHOICES = [
        ("relu", "ReLU"),
        ("sigmoid", "Sigmoid"),
        ("softmax", "Softmax"),
        ("tanh", "Tanh"),
        ("elu", "ELU"),
        ("selu", "SELU"),
        ("linear", "Linear"),
    ]
    activation_function = models.CharField(
        max_length=20, choices=ACTIVATION_CHOICES, default="softmax"
    )

    OPTIMIZER_CHOICES = [
        ("sgd", "Stochastic Gradient Descent"),
        ("adam", "Adam"),
        ("rmsprop", "RMSprop"),
        ("adagrad", "Adagrad"),
        ("adadelta", "Adadelta"),
        ("adamax", "Adamax"),
        ("nadam", "Nadam"),
    ]
    optimizer = models.CharField(
        max_length=20, choices=OPTIMIZER_CHOICES, default="adam"
    )

    LOSS_CHOICES = [
        ("sparse_categorical_crossentropy", "Sparse Categorical Crossentropy"),
        ("categorical_crossentropy", "Categorical Crossentropy"),
        ("binary_crossentropy", "Binary Crossentropy"),
        ("mean_squared_error", "Mean Squared Error"),
        ("mean_absolute_error", "Mean Absolute Error"),
        ("huber_loss", "Huber Loss"),
        ("hinge", "Hinge"),
        ("kl_divergence", "Kullback-Leibler Divergence"),
    ]
    loss_function = models.CharField(
        max_length=50, choices=LOSS_CHOICES, default="sparse_categorical_crossentropy"
    )

    METRIC_CHOICES = [
        ("accuracy", "Accuracy"),
        ("categorical_accuracy", "Categorical Accuracy"),
        ("sparse_categorical_accuracy", "Sparse Categorical Accuracy"),
        ("AUC", "AUC"),
        ("Precision", "Precision"),
        ("Recall", "Recall"),
        ("mean_squared_error", "Mean Squared Error"),
        ("mean_absolute_error", "Mean Absolute Error"),
        ("mean_absolute_percentage_error", "Mean Absolute Percentage Error"),
        ("top_k_categorical_accuracy", "Top K Categorical Accuracy"),
    ]
    metrics = models.CharField(
        max_length=50, choices=METRIC_CHOICES, default="accuracy"
    )

    batch_size = models.IntegerField(default=1)
    epochs = models.IntegerField(default=5)

    class Meta:
        managed = True
        db_table = "model"


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
        Model, to_field="version", on_delete=models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = True
        db_table = "requests"
