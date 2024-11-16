from django.db import models

# Documentation references:
# https://docs.djangoproject.com/en/5.1/topics/db/models/
# https://docs.djangoproject.com/en/5.1/ref/models/fields/

class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    version = models.CharField(max_length=50, unique=True)
    weights = models.BinaryField(null=False)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='draft'
    )

    class Meta:
        managed = True
        db_table = 'model'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.TextField(null=False)
    age = models.IntegerField(blank=False, null=False)
    session = models.TextField(null=True, blank=True)
    session_exp = models.IntegerField(null=True, blank=True)

    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    sex = models.CharField(
        max_length=6,
        choices=SEX_CHOICES,
        null=False
    )

    is_admin = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'users'


class Requests(models.Model):
    request_id = models.AutoField(primary_key=True)
    created_at = models.IntegerField(null=False, blank=False)
    probability = models.IntegerField(blank=True, null=True)
    image = models.BinaryField(blank=False, null=False)

    LOCALIZATION_CHOICES = [
        # Head and Neck region
        ('ear', 'Ear'),
        ('face', 'Face'),
        ('neck', 'Neck'),
        ('scalp', 'Scalp'),
        
        # Trunk region
        ('abdomen', 'Abdomen'),
        ('back', 'Back'),
        ('chest', 'Chest'),
        ('trunk', 'Trunk - Other'),

        # Upper limbs
        ('acral', 'Acral (Fingers/Toes)'),
        ('hand', 'Hand'),
        ('upper_extremity', 'Upper Extremity (Arm)'),
        
        # Lower limbs
        ('foot', 'Foot'),
        ('lower_extremity', 'Lower Extremity (Leg)'),
        
        # Other locations
        ('genital', 'Genital Area')
    ]
    localization = models.CharField(
        max_length=15,
        choices=LOCALIZATION_CHOICES,
        blank=False,
        null=False
    )
    
    LESION_TYPE_CHOICES = [
        # Benign lesions
        ('nv', 'Melanocytic nevi'),
        ('bkl', 'Benign keratosis-like lesions'),
        ('df', 'Dermatofibroma'),
        ('vasc', 'Vascular lesions'),
        
        # Malignant/Potentially Malignant lesions
        ('mel', 'Melanoma'),
        ('bcc', 'Basal cell carcinoma'),
        ('akiec', 'Actinic keratoses and intraepithelial carcinoma')
    ]
    lesion_type = models.CharField(
        max_length=5,
        choices=LESION_TYPE_CHOICES,
        blank=False, 
        null=False
    )

    # Foreign Keys
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    # Sets the foreign key to be the Model version column, so that the model version
    # used for the prediction can be found even if the Model itself is deleted
    model = models.ForeignKey(
        Model, 
        to_field='version',
        on_delete=models.DO_NOTHING, 
        blank=True, 
        null=True
    )

    class Meta:
        managed = True
        db_table = 'requests'
