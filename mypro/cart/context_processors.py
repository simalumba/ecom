from .cart import Cart

# Create context processor so our cart can work on all page
def cart(request):
    # return the default data from our Cart
    return {'cart': Cart(request)}
