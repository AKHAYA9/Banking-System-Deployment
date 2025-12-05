from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ---------------------------
    # Public / Auth
    # ---------------------------
    path('', views.index, name='index'),
    path('please_login/', views.please_login, name='please_login'),
    path('login/', views.UserLogin, name='UserLogin'),
    path('login/check/', views.UserLoginCheck, name='UserLoginCheck'),
    path('register/', views.UserRegister, name='UserRegister'),
    path('register/action/', views.UserRegisterActions, name='UserRegisterActions'),
    path('logout/', views.user_logout, name='user_logout'),

    # ---------------------------
    # Normal User
    # ---------------------------
    path('user/home/', views.UserHome, name='user_home'),
    path('user/dashboard/', views.UserHome, name='user_dashboard'),  # Alias
    path('profile/edit/', views.UserProfileUpdateView, name='profile_edit'),
    path('profile/change-password/', views.UserChangePasswordView, name='change_password'),
    # ---------------------------
    # Custom Admin Dashboard
    # ---------------------------
    path('dashboard/home/', views.admin_home, name='admin_home'),
    path('dashboard/manage-users/', views.manage_users, name='manage_users'),
    path('dashboard/activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('dashboard/deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('dashboard/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    # Players CRUD
    path('dashboard/player/add/', views.add_player, name='add_player'),
    path('dashboard/player/update/<int:pk>/', views.update_player_balance, name='update_player'),
    path('dashboard/player/delete/<int:pk>/', views.delete_player, name='delete_player'),
    path('dashboard/player/reset/<int:pk>/', views.reset_player_balance, name='reset_player_balance'),

    # Transactions CRUD
    path('dashboard/transaction/add/', views.add_transaction, name='add_transaction'),
    path('dashboard/transaction/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('dashboard/transaction/reset/', views.reset_transactions, name='reset_transactions'),
    path('dashboard/reset-all/', views.reset_all, name='reset_all'),

    # Match Results
    path('dashboard/match-results/', views.match_results, name='match_results'),
    path('dashboard/match-results/delete/<int:result_id>/', views.delete_match_result, name='delete_match_result'),

    # Public Pages
    path('service/', views.service, name='service'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("contact-submit/", views.contact_submit, name="contact_submit"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)