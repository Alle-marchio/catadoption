from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Cat, CatPhoto, CustomUser, Shelter,
    AdoptionRequest, Adoption, Post, Event, Donation
)


class CatPhotoInline(admin.TabularInline):
    model = CatPhoto
    extra = 1


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'age', 'breed', 'adoption_status', 'shelter')
    list_filter = ('gender', 'adoption_status', 'neutered', 'vaccinated', 'shelter')
    search_fields = ('name', 'breed', 'color', 'description')
    inlines = [CatPhotoInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'gender', 'age', 'birth_date', 'breed', 'color')
        }),
        (_('Health & Status'), {
            'fields': ('health_status', 'vaccinated', 'neutered', 'adoption_status')
        }),
        (_('Background'), {
            'fields': ('description', 'history', 'personality')
        }),
        (_('Shelter Information'), {
            'fields': ('shelter', 'arrival_date')
        }),
    )


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'photo')}),
        (_('Role'), {'fields': ('role',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email')
    search_fields = ('name', 'address', 'description')
    filter_horizontal = ('staff',)


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'cat', 'user', 'request_date', 'status')
    list_filter = ('status', 'request_date')
    search_fields = ('cat__name', 'user__username', 'user__email')
    readonly_fields = ('id', 'request_date')
    fieldsets = (
        (_('Request Information'), {
            'fields': ('id', 'cat', 'user', 'request_date', 'status')
        }),
        (_('Applicant Information'), {
            'fields': ('living_situation', 'experience', 'reason')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
    )


@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ('request', 'adoption_date', 'processed_by', 'follow_up_date')
    list_filter = ('adoption_date', 'follow_up_date')
    search_fields = ('request__cat__name', 'request__user__username')
    raw_id_fields = ('request', 'processed_by')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'is_published')
    list_filter = ('is_published', 'published_date')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'image')
        }),
        (_('Publication'), {
            'fields': ('author', 'is_published')
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'shelter', 'is_active')
    list_filter = ('is_active', 'date', 'shelter')
    search_fields = ('name', 'description', 'location')
    fieldsets = (
        (None, {
            'fields': ('name', 'date', 'location', 'description', 'image')
        }),
        (_('Organization'), {
            'fields': ('organizer', 'shelter', 'is_active')
        }),
    )


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_type', 'get_donor_name', 'amount', 'date', 'shelter')
    list_filter = ('donation_type', 'date', 'shelter', 'is_anonymous')
    search_fields = ('donor__username', 'description', 'message')

    def get_donor_name(self, obj):
        if obj.is_anonymous or not obj.donor:
            return _('Anonymous')
        return obj.donor.username

    get_donor_name.short_description = _('Donor')


# Register CatPhoto model separately if needed
admin.site.register(CatPhoto)