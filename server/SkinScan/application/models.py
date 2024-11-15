from django.db import models

# Documentation references:
# https://docs.djangoproject.com/en/5.1/topics/db/models/
# https://docs.djangoproject.com/en/5.1/ref/models/fields/

class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    # Note: This can be modified to "auto_now" or added as a new field,
    # if we instead want a timestamp for when the model was last modified
    created_at = models.DateTimeField(auto_now_add=True) # Sets unmodifiable timestamp at creation
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
    created_at = models.DateTimeField(auto_now_add=True) # Sets unmodifiable timestamp at creation
    image = models.BinaryField(blank=False, null=False)
    probability = models.IntegerField(blank=True, null=True)

    CANCER_TYPE_CHOICES = [
        ('benign', 'Benign'),
        ('malignant', 'Malignant')
    ]
    cancer_type = models.CharField(
        max_length=9,
        choices=CANCER_TYPE_CHOICES,
        blank=True, 
        null=True
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
