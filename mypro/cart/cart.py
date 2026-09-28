from store.models import Product,Profile

class Cart:
    def __init__(self, request):
        self.session = request.session
        # Get request
        self.request = request
        # Get the current session key if it exists
        cart = self.session.get('session_key')
        # If the user is new,no session key! create one!
        if 'session_key' not in request.session:
            # Make sure cart is available on all pages of site
            cart = self.session['session_key'] = {}
        self.cart = cart

    def db_add(self, product, quantity):
         product_id = str(product)
         product_qty = str(quantity)
        # Logic
         if product_id in self.cart:
            self.cart[product_id] += quantity
         else:
            self.cart[product_id] = quantity
            self.session.modified = True
        # Deal with logged in user
         if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Save cart to the Profile Model
            current_user.update(old_cart=str(carty))

 

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)
        # Logic
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.session.modified = True
        # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Save cart to the Profile Model
            current_user.update(old_cart=str(carty))




    def cart_total(self):
        # Get product IDS
        product_ids = self.cart.keys()
        # Lookup those keys in our products database models
        products = Product.objects.filter(id__in=product_ids)
        # Get quantities
        quantities = self.cart
        # Start counting at 0
        total = 0
        for key, value in quantities.items():
            # Convert key string into so we can do math
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                       total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total



    def __len__(self):
        return len(self.cart)

    def get_prods(self):
       product_ids = [int(id) for id in self.cart.keys() if id.isdigit()]
       products = Product.objects.filter(id__in=product_ids)
       return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
       product_id = str(product.id)
       product_qty = int(quantity)
       ourcart = self.cart
       ourcart[product_id] = product_qty
       self.session.modified = True

    # Deal with logged in user
       if self.request.user.is_authenticated:
        current_user = Profile.objects.filter(user__id=self.request.user.id)

        carty = str(self.cart)
        carty = carty.replace("\'","\"")

        current_user.update(old_cart=str(carty))

        return product_qty

      

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
         del self.cart[product_id]
        self.session['cart'] = self.cart  # save changes
        self.session.modified = True

         # Deal with logged in user
        if self.request.user.is_authenticated:
            # Get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # Convert {'3':1, '2':4} to {"3":1, "2":4}
            carty = str(self.cart)
            carty = carty.replace("\'","\"")
            # Save cart to the Profile Model
            current_user.update(old_cart=str(carty))