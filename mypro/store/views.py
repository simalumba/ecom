from django.shortcuts import render,redirect
from .models import Product,Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from.forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
import json
from cart.cart import Cart




def search(request):
    if request.method == "POST":
        searched = request.POST.get('searched', '').strip()  # ✅ Get and strip whitespace
        
        # ✅ Check FIRST if empty
        if not searched:
            messages.warning(request, "Please enter a search term!")
            return render(request, 'search.html', {'searched': searched})
        
        # ✅ Then filter products
        products = Product.objects.filter(name__icontains=searched)
        
        # ✅ Check if no products found
        if not products.exists():
            messages.warning(request, f"No products found for '{searched}'")
            return render(request, 'search.html', {'searched': searched, 'products': []})
        
        return render(request, 'search.html', {'products': products, 'searched': searched})
    
    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:

        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Get or create shipping address
        shipping_user, created = ShippingAddress.objects.get_or_create(user=request.user)

        # Forms
        form = UserInfoForm(request.POST or None, instance=profile)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid():
            form.save()

            shipping = shipping_form.save(commit=False)
            shipping.user = request.user
            shipping.save()

            messages.success(request, "Your Info Has Been Updated!!")
            return redirect('store:home')

        return render(
            request,
            "update_info.html",
            {
                'form': form,
                'shipping_form': shipping_form
            }
        )

    else:
        messages.error(request, "You Must Be Logged In To Access That Page!!")
        return redirect('store:login')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form
        if request.method == 'POST':
             form = ChangePasswordForm(current_user,request.POST)
             # Is the form valid
             if form.is_valid():
                 form.save()
                 messages.success(request,"Your Password Has Been Updated, Please Log in Again...")
                 #login(request, current_user)
                 return redirect('store:update_user')
             else:
                  for error in list(form.errors.values()):
                      messages.error(request,error)
                      return redirect('store:update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request,'update_password.html',{'form':form})
    else:
        messages.success(request, "You Must Be Logged In To View That Page!!")
        
        return redirect('store:update_info')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form =UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
                user_form.save()

                login(request, current_user)
                messages.success(request, "User Has Been Updated!!")
                return redirect('store:home')
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "You Must Be Logged In To Access That Page!!")
        return redirect('store:home')



def category_summary(request):
    categories = Category.objects.all()
    return render(request,'category_summary.html',{'categories':categories})


# Create your views here.
def category(request, foo):
    # Replace hyphens with spaces
    foo = foo.replace('-',' ')
    try:
        # Look Up The Category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products':products, 'category':category})
    except Category.DoesNotExist:
        messages.success(request, "That Category Doesn't Exist...")
        return redirect('store:home')



def product(request,pk):
     product = Product.objects.get(id=pk)
     return render(request, 'product.html', {'product': product})


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})
def about(request):
    return render(request, 'about.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Do some shopping cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            # Get their saved cart from database
            saved_cart = current_user.old_cart
            # Convert database string to python dictionary
            if saved_cart:
                # Convert to dictionary using JSON
                converted_cart = json.loads(saved_cart)
                # Add the loaded cart dictionary to our session
                # Get the cart
                cart_obj = Cart(request)
                # Loop thru the cart and add the items from the database

                for key,value in converted_cart.items():
                    cart_obj.db_add(product=key, quantity=value)


            messages.success(request, "You Have Been Logged In!")
            return redirect('store:home')  # redirect after successful login
        else:
            messages.error(request, "There was an error, Please try again.")
            return redirect('store:login')  # redirect back to login page

    else:
        return render(request, 'login.html', {})  # show login page when method is GET


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out. Thanks for stopping by!")
    return redirect('store:login')


def register_user(request):
    forms = SignUpForm()
    if request.method == "POST":
        forms = SignUpForm(request.POST)
        if forms.is_valid():
           forms.save()
           username = forms.cleaned_data['username']
           password = forms.cleaned_data['password1']
           # log in user
           user = authenticate(username=username, password=password)
           login(request, user)
           messages.success(request, "Username Created- Pleased Fill Out Your Info Below...")
           return redirect('store:update_info')
        else:
           messages.success(request, "Whoops! There was a problem Registering, please try again...")
           return redirect('store:register') 
    else:    
        return render(request, 'register.html', {'form': forms})
        

