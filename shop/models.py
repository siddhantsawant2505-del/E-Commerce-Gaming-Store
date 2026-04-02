from django.db import models
from django.contrib.auth.models import User



class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)  # Optional field for product description
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    
    

class Contact(models.Model):
    name=models.CharField(max_length=122)
    rating = models.FloatField(default=0.0)
    email=models.CharField(max_length=122,default="none")
    phone=models.CharField(max_length=12,default="none")
    desc=models.TextField()
    date=models.DateField()

    def __str__(self):
        return self.name + " "+self.phone    


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    fixed_id = models.PositiveIntegerField(default=100) 

    def __str__(self):
        return f"{self.quantity}x {self.name} for {self.user.username}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user who made the order
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically sets the timestamp when the order was created

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"  # Order IDs will be unique globally


class CartItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # Links to the associated order
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1) # Added to track how many of each item is ordered

    def __str__(self):
        return f"{self.quantity}x {self.name} in Order {self.order.id}"
    

