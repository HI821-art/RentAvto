from django.shortcuts import redirect, render
from django.contrib import messages

from cart.cart import add_to_cart, clear_cart, get_cart
from car.models import Car


def index(request):
    items = get_cart(request.session)
    car = car.objects.filter(id__in=items.keys())
    total_price = sum(p.price for p in car)

    return render(
        request, "cart/index.html", {"car": car, "total": total_price}
    )


def add(request, id, quantity=1, return_url="/cart"):
    if Car.objects.get(id=id) is None:
        messages.error(request, "Product not found!")
        return redirect("/cart")

    add_to_cart(request.session, id, quantity)
    messages.success(request, "Product added to cart!")

    return redirect(return_url)


def clear(request):
    clear_cart(request.session)
    messages.success(request, "Cart cleared!")

    return redirect("/cart")