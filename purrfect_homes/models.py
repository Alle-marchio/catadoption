from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid


class Cat(models.Model):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
    ]

    ADOPTION_STATUS = [
        ('available', _('Available')),
        ('reserved', _('Reserved')),
        ('adopted', _('Adopted')),
    ]

    name = models.CharField(_('Name'), max_length=100)
    age = models.PositiveIntegerField(_('Age in months'), null=True, blank=True)
    birth_date = models.DateField(_('Birth date'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
    breed = models.CharField(_('Breed'), max_length=100, blank=True, null=True)
    color = models.CharField(_('Color'), max_length=100)
    description = models.TextField(_('Description'))
    health_status = models.TextField(_('Health status'), blank=True)
    vaccinated = models.BooleanField(_('Vaccinated'), default=False)
    neutered = models.BooleanField(_('Neutered/Spayed'), default=False)
    history = models.TextField(_('Personal history'), blank=True)
    personality = models.TextField(_('Personality'), blank=True)
    arrival_date = models.DateField(_('Arrival date'))
    adoption_status = models.CharField(
        _('Adoption status'),
        max_length=10,
        choices=ADOPTION_STATUS,
        default='available'
    )
    shelter = models.ForeignKey('Shelter', on_delete=models.CASCADE, related_name='cats')

    def formatted_age(self):
        if self.age < 12:
            return f"{self.age} mes{'i' if self.age != 1 else 'e'}"
        else:
            years = self.age // 12
            remaining_months = self.age % 12
            if remaining_months == 0:
                return f"{years} ann{'i' if years > 1 else 'o'}"
            else:
                return f"{years} ann{'i' if years > 1 else 'o'} e {remaining_months} mes{'i' if remaining_months > 1 else 'e'}"

    def __str__(self):
        return self.name
    """
    # le query sono ordinate tramite l'id
    class Meta:
        ordering = ['id']
    """


class CustomUser(AbstractUser):
    USER_ROLES = [
        ('admin', _('Administrator')),
        ('staff', _('Shelter Staff')),
        ('adopter', _('Adopter')),
    ]

    phone = models.CharField(_('Phone number'), max_length=20, blank=True)
    address = models.TextField(_('Address'), blank=True)
    role = models.CharField(_('Role'), max_length=10, choices=USER_ROLES, default='adopter')
    photo = models.ImageField(_('Profile photo'), upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.username


class Shelter(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    address = models.TextField(_('Address'))
    phone = models.CharField(_('Phone number'), max_length=20)
    email = models.EmailField(_('Email'), blank=True)
    description = models.TextField(_('Description'), blank=True)
    opening_hours = models.TextField(_('Opening hours'), blank=True)
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='staffed_shelters',
        limit_choices_to={'role': 'staff'},
        blank=True
    )

    def __str__(self):
        return self.name


class CatPhoto(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(_('Image'), upload_to='cat_photos/')
    is_primary = models.BooleanField(_('Primary photo'), default=False)
    caption = models.CharField(_('Caption'), max_length=255, blank=True)
    uploaded_at = models.DateTimeField(_('Uploaded at'), auto_now_add=True)

    def __str__(self):
        return f"Photo of {self.cat.name}"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='adoption_requests'
    )
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='adoption_requests')
    request_date = models.DateTimeField(_('Request date'), auto_now_add=True)
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(_('Notes'), blank=True)
    living_situation = models.TextField(_('Living situation'), help_text=_('Describe your home, yard, etc.'))
    experience = models.TextField(_('Experience with pets'), help_text=_('Previous experience with pets'))
    reason = models.TextField(_('Reason for adoption'), help_text=_('Why do you want to adopt this cat?'))

    def __str__(self):
        return f"Request for {self.cat.name} by {self.user.username}"


class Adoption(models.Model):
    request = models.OneToOneField(
        AdoptionRequest,
        on_delete=models.CASCADE,
        related_name='adoption'
    )
    adoption_date = models.DateField(_('Adoption date'))
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_adoptions',
        limit_choices_to={'role__in': ['admin', 'staff']}
    )
    follow_up_date = models.DateField(_('Follow-up date'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)

    def __str__(self):
        return f"{self.request.cat.name} adopted by {self.request.user.username}"


class Post(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    content = models.TextField(_('Content'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    published_date = models.DateTimeField(_('Published date'), auto_now_add=True)
    updated_date = models.DateTimeField(_('Updated date'), auto_now=True)
    image = models.ImageField(_('Image'), upload_to='post_images/', null=True, blank=True)
    is_published = models.BooleanField(_('Published'), default=True)
    slug = models.SlugField(_('Slug'), unique=True)

    def __str__(self):
        return self.title


class Event(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    date = models.DateTimeField(_('Date and time'))
    location = models.CharField(_('Location'), max_length=255)
    description = models.TextField(_('Description'))
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    image = models.ImageField(_('Image'), upload_to='event_images/', null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return self.name


class Donation(models.Model):
    DONATION_TYPES = [
        ('money', _('Money')),
        ('food', _('Food')),
        ('supplies', _('Supplies')),
        ('other', _('Other')),
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations'
    )
    donation_type = models.CharField(_('Donation type'), max_length=10, choices=DONATION_TYPES)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(_('Description'), blank=True)
    date = models.DateField(_('Donation date'), auto_now_add=True)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='donations')
    message = models.TextField(_('Message'), blank=True)
    is_anonymous = models.BooleanField(_('Anonymous'), default=False)

    def __str__(self):
        if self.donor and not self.is_anonymous:
            return f"{self.donation_type} donation by {self.donor.username}"
        return f"Anonymous {self.donation_type} donation"