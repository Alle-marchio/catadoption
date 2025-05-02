from django.urls import path
from . import views

app_name = 'purrfect_homes'  # Namespace dell'app

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),

    # Cat routes
    path('cats/', views.CatListView.as_view(), name='cat-list'),
    path('cats/<int:pk>/', views.CatDetailView.as_view(), name='cat-detail'),

    # Adoption request routes
    path('cats/<int:cat_id>/adopt/', views.AdoptionRequestCreateView.as_view(), name='adoption-request-create'),

    # User profile
    path('profile/', views.user_profile_view, name='user-profile'),

    # Shelter routes
    path('shelters/', views.ShelterListView.as_view(), name='shelter-list'),
    path('shelters/<int:pk>/', views.ShelterDetailView.as_view(), name='shelter-detail'),

    # Blog routes
    path('blog/', views.PostListView.as_view(), name='post-list'),
    path('blog/<slug:slug>/', views.PostDetailView.as_view(), name='post-detail'),

    # Event routes
    path('events/', views.EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),

    # Donation routes
    path('donate/', views.DonationCreateView.as_view(), name='donation-create'),
    path('donate/thank-you/', views.donation_thank_you_view, name='donation-thank-you'),

    # Staff routes
    path('staff/adoption-requests/', views.AdoptionRequestListView.as_view(), name='adoption-request-list'),
    path('staff/adoption-requests/<uuid:request_id>/approve/',
         views.approve_adoption_request, name='approve-adoption-request'),
    path('staff/adoption-requests/<uuid:request_id>/reject/',
         views.reject_adoption_request, name='reject-adoption-request'),
]