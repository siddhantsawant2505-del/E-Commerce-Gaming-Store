from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from shop.models import  Contact,Cart, Order, CartItem,Product
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import ContactForm
from django.urls import reverse
from django.shortcuts import render
from shop.models import Order, CartItem  # Import the Order and CartItem models
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_anonymous:
          return redirect('login/')
    messages.success(request, 'Welcome!')
    reviews = Contact.objects.all()
    return render(request, 'home.html' , {'reviews': reviews})

def homeret():
     return redirect("home")

def about(request):
     if request.user.is_anonymous:
          return redirect('login')
     return render(request, 'about.html')

def search(request):
     if request.user.is_anonymous:
          return redirect('login')
     return render(request,'serach_res.html')

def products(request):
    if request.user.is_anonymous:
         return redirect('login')
    return render(request, 'products.html')


def item_detail(request):
    item_name = request.GET.get('name')  # Get the item name from query parameters
    
    context = {
        'item_name': item_name,
    }
    return render(request, 'itemdes.html',context)

def mycart(request):
    if request.user.is_anonymous:
          return redirect('login')
    return render(request, 'mycart.html')

def my_cart(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.price * item.quantity for item in cart_items)
        return render(request, 'mycart.html', {'cart_items': cart_items, 'total_price': total_price , 'id': cart_items.id})
    else:
        return redirect('login')

def add(request, product_id):
    if request.method == 'POST':
        # Ensure product exists in the database
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))  # Get quantity, default to 1
        user = request.user  # Get logged-in user
        fixed_id = f"{product.id}"
        # Create or update the cart item for the user, linking it to the correct product
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            name=product.name,
            product=product,
            fixed_id=fixed_id,  # Pass the product here
            defaults={'price': product.price, 'quantity': quantity}
        )

        # If the item already exists, just update the quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def loginUser(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
                 # A backend authenticated the credentials
                 login(request,user)
                 
                 return redirect('home')
    
        else:
                  # No backend authenticated the credentials
                  messages.error(request, 'Invalid username or password')
                  return render(request,'login.html')

    return render(request,'login.html')


def logoutUser(request):
    logout(request)
    return redirect("login") 


def contact(request):
    if request.method == "POST":
        name=request.POST.get('name')
        rating=request.POST.get('rating')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        desc=request.POST.get('desc')
        contact=Contact(name=name,rating=rating,email=email,phone=phone,desc=desc,date=datetime.today())
        contact.save()
        messages.success(request, "YOUR FEEDBACK HAS BEEN SENT.")
    return redirect(reverse('about') + '#contact')

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')  # Change this to your home page
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        cart_data = json.loads(request.body)  # Get the cart data from the request

        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=401)

        # Create a new Order for the user
        order = Order.objects.create(user=request.user)

        # Loop through each item in the cart data and create a CartItem for it
        for item in cart_data:
            CartItem.objects.create(
                order=order,
                name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Clear the user's cart after successful checkout
        Cart.objects.filter(user=request.user).delete()

        return JsonResponse({'success': True, 'message': 'Checkout completed successfully', 'order_id': order.id})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def load_user_cart(request):
    if request.user.is_authenticated:
        user_cart_items = Cart.objects.filter(user=request.user)
        print(user_cart_items) 
        # Include the 'id' in the cart items returned to the front end
        cart = [{"fixed_id": item.fixed_id, "name": item.name, "price": item.price, "quantity": item.quantity} for item in user_cart_items]
        return JsonResponse({"cart": cart})
    else:
        return JsonResponse({"cart": []})


@csrf_exempt
def remove_item(request, fixed_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                # Remove the item from the user's cart by product ID
                cart_item = Cart.objects.get(user=request.user, fixed_id=fixed_id)
                cart_item.delete()  # Delete the cart item
                return JsonResponse({'success': True, 'message': 'Item removed from cart.'})
            except Cart.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Item not found.'}, status=404)
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'}, status=401)
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)



@login_required
def view_orders(request):
    # Retrieve all orders for the logged-in user, ordered by descending ID (latest first)
    orders = Order.objects.filter(user=request.user).order_by('-id')

    # Prepare a list of orders with dynamic order numbers
    order_list = []
    total_orders = orders.count()
    grand_total = 0  # Initialize grand total

    for index, order in enumerate(orders):
        # Calculate the order number dynamically, where the latest order is number 1
        order_number = total_orders - index
        order_items = CartItem.objects.filter(order=order)  # Get items in this order

        # Calculate the total price for items in this order
        order_total = sum(item.price * item.quantity for item in order_items)

        # Add order total to grand total
        grand_total += order_total

        order_list.append({
            'order_id': order.id,           # Unique ID (incrementing value)
            'order_number': order_number,    # Dynamic order number (1, 2, 3, ...)
            'order_date': order.created_at,  # Order date
            'items': order_items,            # The items in this order
            'order_total': order_total       # Total for this order
        })

    # Pass the grand total to the template
    return render(request, 'view_orders.html', {'orders': order_list, 'grand_total': grand_total})


@csrf_exempt  # Only use if CSRF token passing doesn't work; otherwise, include CSRF protection.
def update_quantity(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Read the JSON data
            new_quantity = data.get('quantity')  # Get the new quantity

            # Ensure the product and quantity are valid
            if new_quantity is None or new_quantity <= 0:
                return JsonResponse({'success': False, 'message': 'Invalid quantity'}, status=400)

            user = request.user  # Get the logged-in user
            product = get_object_or_404(Product, id=product_id)

            # Retrieve the cart item for the user and product
            try:
                cart_item = Cart.objects.get(user=user, product=product)
                cart_item.quantity = new_quantity  # Update quantity
                cart_item.save()

                return JsonResponse({'success': True, 'message': 'Quantity updated in the database'})
            except Cart.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Item not found in cart'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
