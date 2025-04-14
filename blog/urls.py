from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_articles, name='liste_articles'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('article/<slug:slug>/commentaire/', views.ajouter_commentaire, name='ajouter_commentaire'),
    path('article/<int:article_id>/like/', views.like_article, name='like_article'),
]
