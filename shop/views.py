
import unicodedata
import json
from django.urls import reverse
import stripe

from django.core.mail import EmailMultiAlternatives


from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from datetime import datetime 
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from shop.models import Produit, Panier, LignePanier,Categorie
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings



# Create your views here.
def index(request):
  return render(request,"index.html")

def about(request):
  return render(request,"about.html")

def services(request):
  return render(request,"services.html")

def shop(request):
    categorie_id = request.GET.get('categorie')
    search_query = request.GET.get('q', '')

    produits = Produit.objects.all()
    categories = Categorie.objects.all()

    if categorie_id:
        produits = produits.filter(categories__id=categorie_id)

    if search_query:
        produits = produits.filter(
            Q(nom_produit__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'produits': produits,
        'categories': categories,
        'selected_categorie': int(categorie_id) if categorie_id else None,
    }
    return render(request, 'shop.html', context)


def contact(request):
  return render(request,"contact.html")


# shop/views.py
from decimal import Decimal

def cart(request):
    cart = request.session.get('cart', {})  # Format : {'produit_id': quantite, ...}
    produits_in_cart = []
    total = Decimal("0.00")
    for prod_id, quantity in cart.items():
        produit = get_object_or_404(Produit, id=prod_id)
        sous_total = produit.prix * quantity
        produits_in_cart.append({
            "produit": produit,
            "quantite": quantity,
            "sous_total": sous_total,
        })
        total += sous_total

    context = {
        "produits": produits_in_cart,
        "total": total,
    }
    return render(request, "cart.html", context)




def checkout(request):
    return render(request,"checkout.html")

def blog(request):
    return render(request,"blog.html")

def shop_deatil(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    return render(request, 'shop_detail.html', {'produit': produit})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})  # panier au format {'produit_id': quantite, ...}
    product_key = str(product_id)
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')





@require_POST
def add_to_cart(request, product_id):
    # Récupère le produit ou renvoie 404 s'il n'existe pas
    produit = get_object_or_404(Produit, id=product_id)
    
    # Récupère le panier depuis la session (sous forme de dictionnaire)
    cart = request.session.get('cart', {})

    # Ajoute le produit au panier en incrémentant la quantité
    # On stocke l'ID du produit en tant que chaîne, car les clés de session sont des chaînes.
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    # Sauvegarde le panier dans la session
    request.session['cart'] = cart
    request.session.modified = True  # Assure que la session est sauvegardée

    # Retourne un JSON indiquant le succès
    return JsonResponse({"success": True, "message": "Produit ajouté dans le panier!"})
    


@require_POST
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Quantity invalide'}, status=400)

    cart = request.session.get('cart', {})
    product_key = str(product_id)
    if product_key in cart:
        cart[product_key] = quantity
        request.session['cart'] = cart
        request.session.modified = True

    # Recalculez total et sous-total
    produit = get_object_or_404(Produit, id=product_id)
    sous_total = produit.prix * quantity

    total = Decimal("0.00")
    for prod_id, qty in cart.items():
        prod = get_object_or_404(Produit, id=prod_id)
        total += prod.prix * qty

    return JsonResponse({
        'line_total': float(sous_total),
        'cart_total': float(total)
    })
    

def remove_from_cart_session(request, product_id):
    # Récupère le panier depuis la session (format: {'produit_id': quantité, ...})
    cart = request.session.get('cart', {})
    product_key = str(product_id)
    if product_key in cart:
        del cart[product_key]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cart')

# Formulaire personnalisé pour l'inscription
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")






# ✅ CONNEXION
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ Envoi de l'e-mail de confirmation de connexion
            send_mail(
                'Connexion réussie',
                f'Bonjour {user.username}, vous vous êtes connecté avec succès à Eren\'store.',
                'noreply@erenstore.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('index')  # à adapter selon la page d'accueil
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, "login.html")


# ✅ DECONNEXION
def logout_view(request):
    logout(request)
    return redirect('login')



def context_processor(request):
    return {
        'year': datetime.now().year
    }

def politique_confidentialite(request):
    return render(request, 'politique_confidentialite.html')

@login_required

def api_cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    return JsonResponse({'count': count})

def api_search_products(request):
    search_query = request.GET.get('q', '')
    produits = Produit.objects.all()

    if search_query:
        produits = produits.filter(
            Q(nom_produit__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    html = render_to_string("partials/_produits_list.html", {'produits': produits})
    return JsonResponse({'html': html})


def produit_detail(request, id):
    produit = get_object_or_404(Produit, id=id)
    produits_similaires = Produit.objects.filter(categories__in=produit.categories.all()).exclude(id=produit.id)[:4]
    context = {
        "produit": produit,
        "produits_similaires": produits_similaires,
    }
    return render(request, "produit_detail.html", context)


def success(request):
    return render(request, 'success.html')



stripe.api_key = settings.STRIPE_SECRET_KEY


stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    if request.method == "POST":
        data = json.loads(request.body)
        produit = get_object_or_404(Produit, id=data["product_id"])
        quantity = data.get("quantity", 1)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": produit.nom_produit[:100],  # sécurité max
                            "description": produit.description[:200] if produit.description else "",
                        },
                        "unit_amount": int(produit.prix * 100),
                    },
                    "quantity": quantity,
                }],
                mode="payment",
                success_url=f"http://127.0.0.1:8000/checkout/success/",
                cancel_url=f"http://127.0.0.1:8000/produit/{produit.id}/",

            )
            return JsonResponse({"id": session.id})
        except Exception as e:
            print("Erreur Stripe:", e)
            return JsonResponse({"error": str(e)}, status=500)

def checkout_success(request):
    return render(request, "checkout_success.html")



def to_ascii(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")




User = get_user_model()
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse email est déjà utilisée.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_url = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )

        subject = "Activation de votre compte"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email
        email_html = render_to_string('activation_email.html', {
            'activation_url': activation_url
        })

        msg = EmailMultiAlternatives(subject, "", from_email, [to_email])
        msg.attach_alternative(email_html, "text/html")
        msg.send()

        return render(request, 'register.html', {'activation_pending': True})
    return render(request, 'register.html')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Votre compte a été activé. Vous pouvez maintenant vous connecter.")
        return redirect('login')
    else:
        messages.error(request, "Lien invalide ou expiré.")
        return redirect('register')
