
import unicodedata
import json
from django.urls import reverse
import stripe

from django.core.mail import EmailMultiAlternatives
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
import binascii
from django.core.mail import EmailMessage
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import os
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
    # Créez une nouvelle version du panier afin d'exclure les produits non trouvés
    let_cart = {}

    for prod_id, quantity in cart.items():
        try:
            # Conversion en int pour être sûr
            produit = Produit.objects.get(id=int(prod_id))
        except Produit.DoesNotExist:
            # Vous pouvez éventuellement supprimer cet identifiant de la session si besoin
            continue  # Ignore ce produit s'il n'existe pas
        sous_total = produit.prix * quantity
        produits_in_cart.append({
            "produit": produit,
            "quantite": quantity,
            "sous_total": sous_total,
        })
        total += sous_total
        let_cart[prod_id] = quantity  # Conserve cet élément si valide

    # Option : Mettre à jour le panier dans la session pour enlever les produits supprimés
    request.session['cart'] = let_cart
    request.session.modified = True

    context = {
        "produits": produits_in_cart,
        "total": total,
    }
    return render(request, "cart.html", context)


    context = {
        "produits": produits_in_cart,
        "total": total,
    }
    return render(request, "cart.html", context)




@login_required
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Rediriger vers la connexion si non connecté

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        produits = LignePanier.objects.filter(panier=panier)
        total = sum(item.produit.prix * item.quantite for item in produits)
    except Panier.DoesNotExist:
        produits = []
        total = 0

    return render(request, 'checkout.html', {
        'produits': produits,
        'total': total
    })

def blog(request):
    return render(request,"blog.html")

def shop_deatil(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    produits_similaires = Produit.objects.filter(categories__in=produit.categories.all()).exclude(id=produit.id)[:4]
    return render(request, "shop_detail.html", {
        "produit": produit,
        "produits_similaires": produits_similaires,
    })


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
    # Accepte JSON vide
    try:
        json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Requête invalide"}, status=400)

    produit = get_object_or_404(Produit, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({"success": True, "message": "Produit ajouté au panier!"})

    


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

# views.py
from django.views.decorators.http import require_POST

@require_POST
def create_checkout_session(request):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # On récupère les données POST classiques
    product_id = request.POST.get("product_id")
    quantity = int(request.POST.get("quantity", 1))

    produit = get_object_or_404(Produit, id=product_id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": produit.nom_produit[:100],
                        "description": produit.description[:200] if produit.description else "",
                    },
                    "unit_amount": int(produit.prix * 100),
                },
                "quantity": quantity,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("checkout_success")),
            cancel_url=request.build_absolute_uri(reverse("cart")),
        )
        return redirect(session.url)  # Redirection vers Stripe
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def checkout_success(request):
    if request.method == "POST":
        email = request.POST.get("email")
        produits_raw = request.POST.getlist("produits")
        total = request.POST.get("prix_total")

        produits_detail = []
        for p in produits_raw:
            try:
                pid, quantite = map(int, p.split("-"))
                produit = Produit.objects.get(pk=pid)
                produits_detail.append((produit.nom_produit, produit.prix, quantite))
            except:
                continue

        contenu = "Merci pour votre commande !\n\nDétail :\n"
        for nom, prix, q in produits_detail:
            contenu += f"{nom} x{q} - ${prix * q:.2f}\n"
        contenu += f"\nTotal : ${total}\n"

        send_mail(
            subject="Confirmation de votre commande",
            message=contenu,
            from_email="alhousein73@gmail.com",
            recipient_list=[email],
            fail_silently=True
        )

        # Vider le panier ici si besoin
        request.session["panier_id"] = None

        return render(request, "checkout_success.html", {
            "produits": produits_detail,
            "total": total
        })

    return redirect("shop")

# ✅ Vue pour téléchargement direct
def telecharger_facture(request):
    pdf_hex = request.session.get('pdf_data')
    if not pdf_hex:
        return HttpResponse("Aucune facture disponible.")
    pdf_bytes = binascii.unhexlify(pdf_hex)
    return FileResponse(BytesIO(pdf_bytes), as_attachment=True, filename="facture_Eren'store.pdf")




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


def api_cart_items(request):
    panier = Panier.objects.filter(utilisateur=request.user).first()
    items = []
    if panier:
        for ligne in panier.lignes.all():
            items.append({
                'id': ligne.produit.id,
                'nom': ligne.produit.nom_produit,
                'prix': float(ligne.produit.prix),
                'quantite': ligne.quantite
            })
    return JsonResponse({'items': items})




@login_required
def paiement_om(request):
    if request.method == "POST":
        produits_raw = request.POST.getlist('produits')
        total = request.POST.get('prix_total')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        nom = f"{request.POST.get('first_name')} {request.POST.get('last_name')}"

        # Simulation de paiement
        print(f"💸 Paiement simulé pour {nom} ({telephone}) montant ${total}")

        # Vider le panier
        panier = Panier.objects.filter(utilisateur=request.user).first()
        if panier:
            panier.lignes.all().delete()

        # Envoi email de confirmation
        send_mail(
            "Confirmation de votre commande",
            f"Merci {nom},\n\nVotre commande de {total}$ a été prise en compte et sera traitée dans les plus brefs délais.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return redirect('checkout_success')
    return redirect('shop')

def checkout_success(request):
    return render(request, "checkout_success.html")