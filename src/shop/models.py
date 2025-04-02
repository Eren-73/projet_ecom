from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from decimal import Decimal

#
# 1. Modèle Utilisateur
#
class Utilisateur(AbstractUser):
    """
    Hérite d'AbstractUser pour bénéficier de l'authentification Django.
    Ajout d'un champ 'role' pour distinguer Admin et Client.
    Redéfinition des champs groups et user_permissions pour éviter les conflits.
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    # Redéfinition pour éviter les conflits avec auth.User
    groups = models.ManyToManyField(
        Group,
        related_name='shop_utilisateur_set',
        blank=True,
        help_text='Les groupes auxquels appartient cet utilisateur.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='shop_utilisateur_set',
        blank=True,
        help_text='Les permissions spécifiques à cet utilisateur.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_client(self):
        return self.role == 'client'


#
# 2. Modèle Categorie
#
class Categorie(models.Model):
    """
    Regroupe les produits par type (Chaussures, Vêtements, etc.).
    """
    nom_categorie = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom_categorie


#
# 3. Modèle Produit
#
class Produit(models.Model):
    """
    Représente un article à vendre dans la boutique.
    Stocke le prix en décimal (ex: 1500.00) et le stock en nombre entier.
    """
    nom_produit = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)  # Exemple: 1500.00
    stock = models.PositiveIntegerField(default=0)
    image_produit = models.ImageField(upload_to='produits/', blank=True, null=True)

    # Relation ManyToMany vers Categorie
    categories = models.ManyToManyField(Categorie, related_name='produits', blank=True)

    def __str__(self):
        return self.nom_produit

    def diminuer_stock(self, quantite):
        """
        Diminue le stock lors d'un achat.
        Retourne True si le stock est suffisant, sinon False.
        """
        if self.stock >= quantite:
            self.stock -= quantite
            self.save()
            return True
        return False


#
# 4. Modèle Panier
#
class Panier(models.Model):
    """
    Panier 'actif' d'un utilisateur avant validation.
    On suppose qu'un utilisateur n'a qu'un seul panier actif (OneToOne).
    """
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='panier'
    )
    created_at = models.DateTimeField(default=timezone.now)
    # Total du panier stocké en entier (exprimé en CFA francs)
    total = models.IntegerField(default=0)

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    def total_panier(self):
        """
        Calcule et met à jour le total du panier en additionnant le sous-total de chaque LignePanier.
        """
        total_calcule = sum(int(ligne.sous_total()) for ligne in self.lignes.all())  # type: ignore[attr-defined]
        self.total = total_calcule
        self.save()
        return self.total


#
# 5. Modèle LignePanier
#
class LignePanier(models.Model):
    """
    Table intermédiaire pour gérer les produits et quantités dans le Panier.
    """
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='lignes'  # Permet d'accéder via panier_instance.lignes.all()
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE
    )
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom_produit}"

    def sous_total(self):
        """
        Calcule le sous-total de la ligne (quantité * prix du produit).
        Retourne un Decimal qui sera converti en entier pour le panier.
        """
        return self.quantite * self.produit.prix


#
# 6. Modèle Commande
#
class Commande(models.Model):
    """
    Représente une commande validée par l'utilisateur.
    Les informations du panier au moment du paiement sont copiées dans la commande.
    """
    id = models.AutoField(primary_key=True)
    STATUT_CHOICES = (
        ('en_cours', 'En cours'),
        ('envoyee', 'Envoyée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    created_at = models.DateTimeField(default=timezone.now)
    statut_commande = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    # total_commande stocké ici en Decimal ; vous pouvez le changer en IntegerField si besoin.
    total_commande = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.username}"

    def calculer_total(self):
        """
        Recalcule le total de la commande en fonction des lignes de commande associées.
        """
        total = sum(lc.quantite * lc.prix_unitaire for lc in self.lignes.all())  # type: ignore[attr-defined]
        self.total_commande = Decimal(total)
        self.save()
        return self.total_commande


#
# 7. Modèle LigneCommande
#
class LigneCommande(models.Model):
    """
    Détail des produits commandés, qui fige le prix unitaire au moment de l'achat.
    Ce champ se remplit automatiquement et n'est pas modifiable manuellement.
    """
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.SET_NULL,
        null=True
    )
    quantite = models.PositiveIntegerField(default=1)
    # Le champ prix_unitaire est non éditable et se remplit automatiquement dans save()
    prix_unitaire = models.IntegerField(blank=True, null=True, editable=False)

    def __str__(self):
        return f"{self.quantite} x {self.produit} (Commande {self.commande.id})"

    def save(self, *args, **kwargs):
        # Si le prix unitaire n'est pas défini, le remplir automatiquement avec le prix du produit
        if self.produit is not None and self.prix_unitaire is None:
            self.prix_unitaire = int(self.produit.prix)
        super().save(*args, **kwargs)


#
# 8. Modèle Payment (Paiement)
#
class Payment(models.Model):
    """
    Gère le paiement pour une commande validée.
    Le montant est stocké en francs CFA (entier) et se calcule automatiquement
    à partir du total de la commande. Ce champ ne doit pas être modifiable manuellement.
    """
    id = models.AutoField(primary_key=True)
    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('annule', 'Annulé'),
    )
    TYPE_CHOICES = (
        ('carte', 'Carte'),
        ('paypal', 'PayPal'),
        ('autre', 'Autre'),
    )
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        related_name='paiement'
    )
    montant = models.IntegerField(blank=True, null=True, editable=False)
    type_payment = models.CharField(max_length=20, choices=TYPE_CHOICES, default='carte')
    statut_payment = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    # Champ pour s'assurer que le stock est mis à jour une seule fois.
    stock_updated = models.BooleanField(default=False, editable=False)

    def save(self, *args, **kwargs):
        # Mettre à jour le total de la commande et calculer le montant automatiquement.
        if self.commande:
            self.commande.calculer_total()  # Met à jour commande.total_commande
            if self.montant is None:
                self.montant = int(self.commande.total_commande)
        
        # Récupérer le statut précédent pour vérifier le changement.
        previous_status = None
        if self.pk:
            previous = Payment.objects.filter(pk=self.pk).first()
            if previous:
                previous_status = previous.statut_payment

        super().save(*args, **kwargs)

        # Si le paiement vient d'être validé et que le stock n'a pas encore été mis à jour...
        if self.statut_payment == 'valide' and previous_status != 'valide' and not self.stock_updated:
            for ligne in self.commande.lignes.all():  # type: ignore[attr-defined]
                ligne.produit.diminuer_stock(ligne.quantite)
            self.stock_updated = True
            # Enregistrer le changement de flag pour ne pas ré-appliquer la diminution.
            super().save(update_fields=['stock_updated'])

    def __str__(self):
        return f"Paiement #{self.id} - {self.statut_payment} - {self.montant} CFA"

