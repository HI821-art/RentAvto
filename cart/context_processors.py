# myapp/context_processors.py


from cart.cart import get_count


def cart_count(request):
    return {"cart_count": get_count(request.session)}