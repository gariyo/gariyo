from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    profile_picture = models.ImageField(_('profile picture'), upload_to='profile_pics/', blank=True, null=True)  # New field
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    email_confirmed = models.BooleanField(_('email confirmed'), default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser



from django.db import models

class Parcel(models.Model):
    # Existing fields...
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=20)
    sender_address = models.TextField(blank=True)  # Optional field
    recipient_name = models.CharField(max_length=100)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=20)
    recipient_address = models.TextField()
    delivery_date = models.DateField(null=True, blank=True)  # Optional field
    delivery_time = models.TimeField(null=True, blank=True)  # Optional field
    description = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional field
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    insurance_required = models.BooleanField(default=False)
    signature_confirmation_required = models.BooleanField(default=False)
    tracking_number = models.CharField(max_length=100)
    
    # New field for status
    STATUS_CHOICES = (
        ('in_transit', 'In Transit'),
        ('shipping', 'Shipping'),
        ('reached', 'Reached and Ready for Pick'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.tracking_number
