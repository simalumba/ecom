from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages

def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request,'cart_summary.html',{ "cart_products": cart_products, "quantities": quantities,"totals":totals })


def cart_add(request):
    cart = Cart(request)

    if request.method == "POST":
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty', 1))

        if product_qty <= 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)

        product = get_object_or_404(Product, id=product_id)

        cart.add(product=product, quantity=product_qty)

        return JsonResponse({'qty': cart.__len__()})
        messages.success(request, (" Product Added To Cart..."))

    return JsonResponse({'error': 'Invalid request'}, status=400)


def cart_update(request):
    cart = Cart(request)
    if request.method == "POST":
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product = get_object_or_404(Product, id=product_id)
        updated_qty = cart.update(product=product, quantity=product_qty)
        return JsonResponse({'qty': updated_qty})
        messages.success(request, (" Product Update To Cart..."))
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cart_delete(request):
    cart = Cart(request)
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        if product_id:
            cart.delete(product_id)
            return JsonResponse({
                'status': 'success',
                'message': 'Product Deleted From Cart...'
            })
    return JsonResponse({'status': 'error'}, status=400)