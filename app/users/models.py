from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models

class User(AbstractUser):
    """
    User model used in application
    User is defined by login / password pair
    """
    
    """
    Meta information on user
    Permissions list is defined here
    """
    class Meta:
        permissions = (('can_behave_as_contractor', "To provide emulation of access as contractor"),
                       ('can_behave_as_citizen', "To provide amulation of access as citizen"),
                       ('can_behave_as_governor', "To provide admin-like access to dashboard, etc."))

