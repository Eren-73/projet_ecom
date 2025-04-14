from django.contrib import admin
from .models import Utilisateur, Categorie, Produit, Panier, LignePanier, Commande, LigneCommande, Payment

# Affichage inline pour les lignes du panier
class LignePanierInline(admin.TabularInline):
    model = LignePanier
    fields = ('produit', 'quantite', 'detail_prix')
    readonly_fields = ('detail_prix',)
    extra = 0

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'created_at', 'total')
    readonly_fields = ('total',)
    inlines = [LignePanierInline]


# Affichage inline pour les lignes de commande
class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'created_at', 'statut_commande', 'total_commande')
    inlines = [LigneCommandeInline]

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'prix', 'stock')

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom_categorie',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'montant', 'statut_payment', 'created_at')
    readonly_fields = ('montant',)  # Le champ montant est en lecture seule

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')

