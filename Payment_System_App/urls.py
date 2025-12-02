from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
        # Player CRUD
    path('add-player/', views.add_player, name='add_player'),
    path('update-player/<int:pk>/', views.update_player_balance, name='update_player'),
    path('reset-player/<int:pk>/', views.reset_player_balance, name='reset_player'),
    path('delete-player/<int:pk>/', views.delete_player, name='delete_player'),

    # Transaction
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('reset-transactions/', views.reset_transactions, name='reset_transactions'),
    path('reset-all/', views.reset_all, name='reset_all'),
    path('match-results/', views.match_results, name='match_results'),
    path('update-match-result/', views.update_match_result, name='update_match_result'),
    path('delete-match/<int:result_id>/', views.delete_match_result, name='delete_match_result'),
    path("transaction/delete/<int:pk>/", views.delete_transaction, name="delete_transaction"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
