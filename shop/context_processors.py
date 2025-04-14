def cart_count(request):
    """
    Calcule le nombre total d'articles dans le panier stocké en session.
    Le panier est supposé être un dictionnaire sous la forme {'produit_id': quantité, ...}.
    """
    count = 0
    cart = request.session.get('cart', {})
    for quantity in cart.values():
        count += quantity
    return {'cart_count': count}
