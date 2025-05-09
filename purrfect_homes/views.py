from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .forms import CustomUserCreationForm

from .models import (
    Cat, CatPhoto, CustomUser, Shelter,
    AdoptionRequest, Adoption, Post, Event, Donation
)
from .forms import (
    AdoptionRequestForm, DonationForm,
    # Assumo che creerai questi form
)


# Home view
def home_view(request):
    # Get cats available for adoption (limit to 3)
    available_cats = Cat.objects.filter(adoption_status='available').order_by('?')[:3]

    # Get latest news/posts (limit to 3)
    latest_posts = Post.objects.filter(is_published=True).order_by('-published_date')[:3]

    # Get upcoming events (limit to 3)
    upcoming_events = Event.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:3]

    # Get adoption statistics
    adoption_stats = {
        'total_cats': Cat.objects.count(),
        'available_cats': Cat.objects.filter(adoption_status='available').count(),
        'adopted_cats': Cat.objects.filter(adoption_status='adopted').count(),
    }

    context = {
        'available_cats': available_cats,
        'latest_posts': latest_posts,
        'upcoming_events': upcoming_events,
        'adoption_stats': adoption_stats,
    }

    return render(request, 'home/home.html', context)

#register view
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def form_valid(self, form):
        # Imposta automaticamente il ruolo a 'adopter' per i nuovi utenti
        form.instance.role = 'adopter'
        return super().form_valid(form)

# Cat Views
class CatListView(ListView):
    model = Cat
    template_name = 'cats/cat_list.html'
    context_object_name = 'cats'
    paginate_by = 12

    def get_queryset(self):
        queryset = Cat.objects.filter(adoption_status='available').select_related('shelter')

        # Filter by search query if provided
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(breed__icontains=query) |
                Q(color__icontains=query) |
                Q(description__icontains=query)
            )

        # Filter by age if provided
        age_filter = self.request.GET.get('age')
        if age_filter:
            if age_filter == 'kitten':
                queryset = queryset.filter(age__lt=12)  # Under 1 year
            elif age_filter == 'young':
                queryset = queryset.filter(age__gte=12, age__lt=84)  # 1-7 years
            elif age_filter == 'adult':
                queryset = queryset.filter(age__gte=84)  # 7+ years

        # Filter by gender if provided
        gender = self.request.GET.get('gender')
        if gender:
            queryset = queryset.filter(gender=gender)

        # Filter by shelter if provided
        shelter_id = self.request.GET.get('shelter')
        if shelter_id:
            queryset = queryset.filter(shelter_id=shelter_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shelters'] = Shelter.objects.all()
        return context


class CatDetailView(DetailView):
    model = Cat
    template_name = 'cats/cat_detail.html'
    context_object_name = 'cat'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if user has already requested to adopt this cat
        if self.request.user.is_authenticated:
            context['has_requested'] = AdoptionRequest.objects.filter(
                user=self.request.user,
                cat=self.object,
                status='pending'
            ).exists()

        # Get similar cats
        similar_cats = Cat.objects.filter(
            adoption_status='available',
            breed=self.object.breed
        ).exclude(id=self.object.id)[:4]

        context['similar_cats'] = similar_cats
        context['adoption_form'] = AdoptionRequestForm()

        return context


# Adoption Request Views
class AdoptionRequestCreateView(LoginRequiredMixin, CreateView):
    model = AdoptionRequest
    form_class = AdoptionRequestForm
    template_name = 'adoption/adoption_request_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.cat = get_object_or_404(Cat, pk=self.kwargs['cat_id'])

        # Check if cat is still available
        if form.instance.cat.adoption_status != 'available':
            messages.error(self.request, _('Mi dispiace, questo gatto non è più disponibile per l\'adozione.'))
            return redirect('cat-detail', pk=form.instance.cat.pk)

        # Check if user has already submitted a request for this cat
        if AdoptionRequest.objects.filter(user=self.request.user, cat=form.instance.cat, status='pending').exists():
            messages.error(self.request, _('Hai già fatto una richiesta per questo gatto.'))
            return redirect('cat-detail', pk=form.instance.cat.pk)

        response = super().form_valid(form)

        # Update cat status to reserved
        cat = form.instance.cat
        cat.adoption_status = 'reserved'
        cat.save()

        messages.success(self.request, _('La tua richiesta di adozione è andata a buon fine.'))
        return response

    def get_success_url(self):
        return reverse('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recupera il gatto dal database usando l'ID nell'URL
        context['cat'] = get_object_or_404(Cat, pk=self.kwargs['cat_id'])
        return context
@login_required
def user_profile_view(request):
    # Get user's adoption requests
    adoption_requests = AdoptionRequest.objects.filter(user=request.user)

    # Get user's adopted cats
    adopted_cats = Cat.objects.filter(
        adoption_requests__user=request.user,
        adoption_requests__status='approved',
        adoption_status='adopted'
    )

    # Get user's donations
    donations = Donation.objects.filter(donor=request.user)

    context = {
        'adoption_requests': adoption_requests,
        'adopted_cats': adopted_cats,
        'donations': donations,
    }

    return render(request, 'registration/user_profile.html', context)


# Shelter Views
class ShelterListView(ListView):
    model = Shelter
    template_name = 'shelter/shelter_list.html'
    context_object_name = 'shelters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Annotate shelters with cat count
        shelters = context['shelters']
        for shelter in shelters:
            shelter.available_cats_count = Cat.objects.filter(
                shelter=shelter,
                adoption_status='available'
            ).count()

        return context


class ShelterDetailView(DetailView):
    model = Shelter
    template_name = 'shelter/shelter_detail.html'
    context_object_name = 'shelter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get available cats in this shelter
        context['available_cats'] = Cat.objects.filter(
            shelter=self.object,
            adoption_status='available'
        )

        # Get upcoming events at this shelter
        context['upcoming_events'] = Event.objects.filter(
            shelter=self.object,
            is_active=True,
            date__gte=timezone.now()
        ).order_by('date')[:5]

        return context


# Blog/Post Views
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(is_published=True).order_by('-published_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get related posts
        context['related_posts'] = Post.objects.filter(
            is_published=True
        ).exclude(id=self.object.id).order_by('-published_date')[:3]

        return context


# Event Views
class EventListView(ListView):
    model = Event
    template_name = 'event/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
            is_active=True,
            date__gte=timezone.now()
        ).order_by('date')


class EventDetailView(DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'


# Donation Views
class DonationCreateView(LoginRequiredMixin, CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donation/donation_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Set donor if not anonymous
        if not form.cleaned_data.get('is_anonymous'):
            form.instance.donor = self.request.user

        response = super().form_valid(form)
        messages.success(self.request, _('Grazie per la tua donazione!'))
        return response


def donation_thank_you_view(request):
    return render(request, 'donation/donation_thank_you.html')


# Staff views (for shelter staff and administrators)
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is staff or admin"""

    def test_func(self):
        return self.request.user.is_authenticated and (
                self.request.user.role in ['admin', 'staff'] or
                self.request.user.is_superuser
        )


class AdoptionRequestListView(StaffRequiredMixin, ListView):
    model = AdoptionRequest
    template_name = 'cats/staff/adoption_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        # Filter by shelter for staff users
        user = self.request.user

        if user.role == 'admin' or user.is_superuser:
            # Admins can see all requests
            return AdoptionRequest.objects.all().order_by('-request_date')
        else:
            # Staff can only see requests for cats in their shelters
            return AdoptionRequest.objects.filter(
                cat__shelter__staff=user
            ).order_by('-request_date')


@login_required
def approve_adoption_request(request, request_id):
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser):
        messages.error(request, _('You do not have permission to perform this action.'))
        return redirect('home')

    adoption_request = get_object_or_404(AdoptionRequest, pk=request_id)

    # Check if user has permission to approve this request
    if request.user.role == 'staff' and request.user not in adoption_request.cat.shelter.staff.all():
        messages.error(request, _('You do not have permission to approve this request.'))
        return redirect('adoption-request-list')

    # Update request status
    adoption_request.status = 'approved'
    adoption_request.save()

    # Update cat status
    cat = adoption_request.cat
    cat.adoption_status = 'adopted'
    cat.save()

    # Create adoption record
    Adoption.objects.create(
        request=adoption_request,
        adoption_date=timezone.now().date(),
        processed_by=request.user,
        follow_up_date=timezone.now().date() + timedelta(days=30)
    )

    messages.success(request, _('Adoption request approved successfully.'))
    return redirect('adoption-request-list')


@login_required
def reject_adoption_request(request, request_id):
    if not (request.user.role in ['admin', 'staff'] or request.user.is_superuser):
        messages.error(request, _('You do not have permission to perform this action.'))
        return redirect('home')

    adoption_request = get_object_or_404(AdoptionRequest, pk=request_id)

    # Check if user has permission to reject this request
    if request.user.role == 'staff' and request.user not in adoption_request.cat.shelter.staff.all():
        messages.error(request, _('You do not have permission to reject this request.'))
        return redirect('adoption-request-list')

    # Update request status
    adoption_request.status = 'rejected'
    adoption_request.save()

    # If cat was reserved for this request, make it available again
    cat = adoption_request.cat
    if cat.adoption_status == 'reserved':
        cat.adoption_status = 'available'
        cat.save()

    messages.success(request, _('Adoption request rejected.'))
    return redirect('adoption-request-list')