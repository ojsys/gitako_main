from django.db import models
from django.conf import settings
from apps.farms.models import Crop

class Product(models.Model):
    """Base model for products in the marketplace"""
    
    class ProductType(models.TextChoices):
        INPUT = 'input', 'Farm Input'
        PRODUCE = 'produce', 'Farm Produce'
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=10, choices=ProductType.choices)
    
    # Categorization
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class InputProduct(models.Model):
    """Model for farm inputs sold by suppliers"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    supplier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='input_products')
    
    # Product details
    brand = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50)  # kg, liter, bag, etc.
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    min_order_quantity = models.PositiveIntegerField(default=1)
    
    # Additional information
    usage_instructions = models.TextField(blank=True)
    safety_information = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.supplier.username}"
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price

class ProduceProduct(models.Model):
    """Model for farm produce listed by farmers"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='produce_products')
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='produce_products')
    crop = models.ForeignKey('farms.Crop', on_delete=models.CASCADE, related_name='produce_products')
    
    # Produce details
    variety = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    
    # Pricing and quantity
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)  # kg, ton, crate, etc.
    min_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    
    # Availability
    available_from = models.DateField()
    available_until = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold Out'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Quality information
    organic = models.BooleanField(default=False)
    certification = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.farmer.username}"
    
    @property
    def is_available(self):
        return self.status == 'available' and self.available_quantity > 0

class ProductImage(models.Model):
    """Images for products in the marketplace"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

class Order(models.Model):
    """Model for orders in the marketplace"""
    
    class OrderType(models.TextChoices):
        INPUT = 'input', 'Input Purchase'
        PRODUCE = 'produce', 'Produce Purchase'
    
    order_number = models.CharField(max_length=20, unique=True)
    order_type = models.CharField(max_length=10, choices=OrderType.choices)
    
    # Buyer and seller
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_buyer')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_as_seller')
    
    # Order details
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Shipping information
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20)
    
    # Delivery details
    estimated_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment information
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    
    # Notes
    buyer_notes = models.TextField(blank=True)
    seller_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.order_number} - {self.get_order_type_display()}"
    
    class Meta:
        ordering = ['-order_date']
    
    def save(self, *args, **kwargs):
        # Generate order number if not provided
        if not self.order_number:
            import random
            import string
            from django.utils import timezone
            
            date_str = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.digits, k=6))
            self.order_number = f"{date_str}{random_str}"
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    """Model for items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Item details
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class Review(models.Model):
    """Model for product reviews"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    order_item = models.OneToOneField(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='review')
    
    # Review content
    rating = models.PositiveSmallIntegerField()  # 1-5 stars
    title = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']
