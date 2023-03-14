from .models import Cart

def cartquantity(user):
    from django.db.models import Sum

    user_cart = Cart.objects.filter(user= user) # Replace my_user_object with the actual user object
    total_quantity = user_cart.aggregate(Sum('quantity'))['quantity__sum']
    if total_quantity == None:
        total_quantity = 0
    return(total_quantity)

    
    