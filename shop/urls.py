from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Pages principales
    path('', views.index, name='index'),
    path('blog/', views.index, name='blog'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # Boutique et panier
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),  # Peut-être à remplacer par views.checkout plus tard

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart_session, name='remove_from_cart'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),

    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('shop/<int:pk>/', views.shop_deatil, name='shop_deatils'),
    # Réinitialisation de mot de passe
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
        success_url='/password_reset_done/'
    ), name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

    # Politique de confidentialité
    path('confidentialite/', views.politique_confidentialite, name='confidentialite'),

    # API pour le panier
    path("api/cart/count/", views.api_cart_count, name="api_cart_count"),

    path('api/search-products/', views.api_search_products, name='api_search_products'),
    path('produit/<int:id>/', views.produit_detail, name='produit_detail'),
    path('success/', views.success, name='success'),  # ✅ cette ligne
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'), # type: ignore
    path("checkout-success/", views.checkout_success, name="checkout_success"),



    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('api/cart-items/', views.api_cart_items, name='api_cart_items'),
    path('paiement/', views.paiement_om, name='paiement_om'),
    path('merci/', views.checkout_success, name='checkout_success'),




]

# Fichiers médias en développement
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
