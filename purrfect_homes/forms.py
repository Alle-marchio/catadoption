from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    AdoptionRequest, Donation, CustomUser, Cat, Post, Event
)


class CustomUserCreationForm(UserCreationForm):
    # Aggiunto campo per la foto di profilo (opzionale)
    photo = forms.ImageField(
        required=False,
        label="Foto di profilo",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )

    class Meta:
        model = CustomUser
        # Estesi i campi includendo 'photo'
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'phone', 'address', 'photo',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendi obbligatoria l'email
        self.fields['email'].required = True

        # Aggiungi placeholder e classe CSS a tutti i widget (tranne photo già configurato)
        for field_name, field in self.fields.items():
            if field_name != 'photo':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': field.label
                })

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'address', 'photo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600',
            'placeholder': _('Nome utente'),
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600',
            'placeholder': _('Password'),
        })
    )

class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ('living_situation', 'experience', 'reason')
        widgets = {
            'living_situation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Descrivi la tua abitazione (appartamento, casa, campagna, etc.)'),
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Dicci qualcosa sulla tua esperienza con gli animali'),
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Perchè vuoi adottare uno dei nostri gatti?'),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['living_situation'].label = _('Dimmi qualcosa su casa tua')
        self.fields['experience'].label = _('La tua esperienza con gli animali')
        self.fields['reason'].label = _('Perchè adottare questo gatto?')


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('donation_type', 'amount', 'description', 'shelter', 'message', 'is_anonymous')
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '0.01',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Please describe what you are donating'),
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Any message you would like to share'),
            }),
            'shelter': forms.Select(attrs={'class': 'form-control'}),
            'donation_type': forms.Select(attrs={'class': 'form-control'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make amount required only for money donations
        self.fields['amount'].required = False
        self.fields['description'].required = False

        # Add JavaScript to show/hide amount field based on donation type
        self.fields['donation_type'].widget.attrs.update({
            'onchange': 'toggleAmountField(this.value)'
        })

    def clean(self):
        cleaned_data = super().clean()
        donation_type = cleaned_data.get('donation_type')
        amount = cleaned_data.get('amount')
        description = cleaned_data.get('description')

        if donation_type == 'money' and not amount:
            self.add_error('amount', _('Please specify an amount for money donations'))

        if donation_type in ['food', 'supplies', 'other'] and not description:
            self.add_error('description', _('Please describe what you are donating'))

        return cleaned_data


class CatFilterForm(forms.Form):
    GENDER_CHOICES = [
        ('', _('All')),
        ('M', _('Male')),
        ('F', _('Female')),
    ]

    AGE_CHOICES = [
        ('', _('All')),
        ('kitten', _('Kitten (< 1 year)')),
        ('young', _('Young (1-7 years)')),
        ('adult', _('Adult (7+ years)')),
    ]

    q = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search by name, breed, color...'),
        })
    )

    gender = forms.ChoiceField(
        required=False,
        label=_('Gender'),
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    age = forms.ChoiceField(
        required=False,
        label=_('Age'),
        choices=AGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    shelter = forms.ModelChoiceField(
        required=False,
        label=_('Shelter'),
        queryset=None,
        empty_label=_('All Shelters'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        shelters = kwargs.pop('shelters', None)
        super().__init__(*args, **kwargs)

        if shelters is not None:
            self.fields['shelter'].queryset = shelters


class CatCreateForm(forms.ModelForm):
    class Meta:
        model = Cat
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'breed': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'health_status': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'personality': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'arrival_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'adoption_status': forms.Select(attrs={'class': 'form-control'}),
            'shelter': forms.Select(attrs={'class': 'form-control'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'image', 'is_published', 'slug')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('name', 'date', 'location', 'description', 'image', 'shelter', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'shelter': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CatPhotoForm(forms.Form):
    image = forms.ImageField(widget=forms.ClearableFileInput())
    is_primary = forms.BooleanField(required=False, initial=False)
    caption = forms.CharField(max_length=255, required=False)