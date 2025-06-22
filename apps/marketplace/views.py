from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json

from .models import (
    Product, InputProduct, ProduceProduct, ProductImage, Order, OrderItem, Review
)
from .forms import (
    ProductForm, InputProductForm, ProduceProductForm, OrderForm, ReviewForm
)
from apps.farms.models import Farm, Crop

@login_required
def marketplace_dashboard(request):
    """Marketplace dashboard for farmers"""
    # User's products
    user_input_products = InputProduct.objects.filter(supplier=request.user)
    user_produce_products = ProduceProduct.objects.filter(farmer=request.user)
    
    # Orders as buyer and seller
    orders_as_buyer = Order.objects.filter(buyer=request.user).count()
    orders_as_seller = Order.objects.filter(seller=request.user).count()
    
    # Recent orders
    recent_orders = Order.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('buyer', 'seller').order_by('-order_date')[:10]
    
    # Sales analytics
    total_sales = Order.objects.filter(
        seller=request.user,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Purchase analytics
    total_purchases = Order.objects.filter(
        buyer=request.user,
        payment_status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Product performance
    top_selling_products = OrderItem.objects.filter(
        order__seller=request.user,
        order__payment_status='paid'
    ).values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_revenue')[:5]
    
    # Market insights
    popular_products = Product.objects.filter(
        is_active=True
    ).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    context = {
        'user_input_products': user_input_products.count(),
        'user_produce_products': user_produce_products.count(),
        'orders_as_buyer': orders_as_buyer,
        'orders_as_seller': orders_as_seller,
        'recent_orders': recent_orders,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'top_selling_products': top_selling_products,
        'popular_products': popular_products,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/marketplace_dashboard.html', context)

@login_required
def marketplace_browse(request):
    """Browse all marketplace products"""
    products = Product.objects.filter(is_active=True).select_related(
        'inputproduct', 'produceproduct'
    ).prefetch_related('images')
    
    # Apply filters
    product_type = request.GET.get('type')
    category = request.GET.get('category')
    search = request.GET.get('search')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    location = request.GET.get('location')
    
    if product_type:
        products = products.filter(product_type=product_type)
    
    if category:
        products = products.filter(category__icontains=category)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )
    
    if min_price:
        products = products.filter(
            Q(inputproduct__price__gte=min_price) |
            Q(produceproduct__price_per_unit__gte=min_price)
        )
    
    if max_price:
        products = products.filter(
            Q(inputproduct__price__lte=max_price) |
            Q(produceproduct__price_per_unit__lte=max_price)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Product.objects.filter(
        is_active=True
    ).values_list('category', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_filters': {
            'type': product_type,
            'category': category,
            'search': search,
            'min_price': min_price,
            'max_price': max_price,
            'location': location
        },
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/marketplace_browse.html', context)

@login_required
def product_detail(request, product_id):
    """Detailed view of a marketplace product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get product-specific details
    input_detail = None
    produce_detail = None
    
    if product.product_type == 'input':
        try:
            input_detail = InputProduct.objects.get(product=product)
        except InputProduct.DoesNotExist:
            pass
    
    elif product.product_type == 'produce':
        try:
            produce_detail = ProduceProduct.objects.get(product=product)
        except ProduceProduct.DoesNotExist:
            pass
    
    # Get reviews
    reviews = Review.objects.filter(product=product).select_related('user').order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # Check if user can review (has purchased this product)
    can_review = False
    if product.product_type == 'input' and input_detail:
        can_review = Order.objects.filter(
            buyer=request.user,
            items__product=product,
            payment_status='paid'
        ).exists()
    elif product.product_type == 'produce' and produce_detail:
        can_review = Order.objects.filter(
            buyer=request.user,
            items__product=product,
            payment_status='paid'
        ).exists()
    
    # Check if user already reviewed
    user_review = None
    if can_review:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
        except Review.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'input_detail': input_detail,
        'produce_detail': produce_detail,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
        'can_review': can_review and not user_review,
        'user_review': user_review,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/product_detail.html', context)

@login_required
def my_products(request):
    """User's products (both selling and buying)"""
    input_products = InputProduct.objects.filter(
        supplier=request.user
    ).select_related('product').order_by('-product__created_at')
    
    produce_products = ProduceProduct.objects.filter(
        farmer=request.user
    ).select_related('product', 'crop').order_by('-product__created_at')
    
    context = {
        'input_products': input_products,
        'produce_products': produce_products,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/my_products.html', context)

@login_required
def create_input_product(request):
    """Create a new input product for sale"""
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        input_form = InputProductForm(request.POST)
        
        if product_form.is_valid() and input_form.is_valid():
            # Create product
            product = product_form.save(commit=False)
            product.product_type = 'input'
            product.save()
            
            # Create input product
            input_product = input_form.save(commit=False)
            input_product.product = product
            input_product.supplier = request.user
            input_product.save()
            
            messages.success(request, f'Input product "{product.name}" created successfully.')
            return redirect('marketplace:product_detail', product_id=product.id)
    else:
        product_form = ProductForm()
        input_form = InputProductForm()
    
    context = {
        'product_form': product_form,
        'input_form': input_form,
        'title': 'List Farm Input for Sale',
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/create_input_product.html', context)

@login_required
def create_produce_product(request):
    """Create a new produce product for sale"""
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        produce_form = ProduceProductForm(request.POST, user=request.user)
        
        if product_form.is_valid() and produce_form.is_valid():
            # Create product
            product = product_form.save(commit=False)
            product.product_type = 'produce'
            product.save()
            
            # Create produce product
            produce_product = produce_form.save(commit=False)
            produce_product.product = product
            produce_product.farmer = request.user
            produce_product.save()
            
            messages.success(request, f'Produce "{product.name}" listed successfully.')
            return redirect('marketplace:product_detail', product_id=product.id)
    else:
        product_form = ProductForm()
        produce_form = ProduceProductForm(user=request.user)
    
    context = {
        'product_form': product_form,
        'produce_form': produce_form,
        'title': 'List Farm Produce for Sale',
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/create_produce_product.html', context)

@login_required
def my_orders(request):
    """User's orders (as buyer and seller)"""
    orders_as_buyer = Order.objects.filter(
        buyer=request.user
    ).select_related('seller').order_by('-order_date')
    
    orders_as_seller = Order.objects.filter(
        seller=request.user
    ).select_related('buyer').order_by('-order_date')
    
    context = {
        'orders_as_buyer': orders_as_buyer,
        'orders_as_seller': orders_as_seller,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/my_orders.html', context)

@login_required
def order_detail(request, order_id):
    """Detailed view of an order"""
    order = get_object_or_404(
        Order.objects.filter(
            Q(buyer=request.user) | Q(seller=request.user)
        ), 
        id=order_id
    )
    
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    context = {
        'order': order,
        'order_items': order_items,
        'is_buyer': order.buyer == request.user,
        'is_seller': order.seller == request.user,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/order_detail.html', context)

@login_required
def create_order(request, product_id):
    """Create a new order for a product"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get product details
    input_detail = None
    produce_detail = None
    seller = None
    
    if product.product_type == 'input':
        input_detail = get_object_or_404(InputProduct, product=product)
        seller = input_detail.supplier
    elif product.product_type == 'produce':
        produce_detail = get_object_or_404(ProduceProduct, product=product)
        seller = produce_detail.farmer
    
    # Prevent self-ordering
    if seller == request.user:
        messages.error(request, 'You cannot order your own products.')
        return redirect('marketplace:product_detail', product_id=product.id)
    
    if request.method == 'POST':
        quantity = float(request.POST.get('quantity', 1))
        
        # Calculate pricing
        if input_detail:
            unit_price = input_detail.current_price
            if quantity < input_detail.min_order_quantity:
                messages.error(request, f'Minimum order quantity is {input_detail.min_order_quantity}.')
                return redirect('marketplace:product_detail', product_id=product.id)
        else:
            unit_price = produce_detail.price_per_unit
            if quantity < produce_detail.min_order_quantity:
                messages.error(request, f'Minimum order quantity is {produce_detail.min_order_quantity}.')
                return redirect('marketplace:product_detail', product_id=product.id)
        
        total_amount = quantity * unit_price
        
        # Create order
        order = Order.objects.create(
            order_type=product.product_type,
            buyer=request.user,
            seller=seller,
            total_amount=total_amount,
            shipping_address=request.POST.get('shipping_address'),
            shipping_city=request.POST.get('shipping_city'),
            shipping_state=request.POST.get('shipping_state'),
            shipping_country=request.POST.get('shipping_country', 'Nigeria'),
            shipping_phone=request.POST.get('shipping_phone'),
            buyer_notes=request.POST.get('buyer_notes', '')
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_amount
        )
        
        messages.success(request, f'Order #{order.order_number} created successfully!')
        return redirect('marketplace:order_detail', order_id=order.id)
    
    context = {
        'product': product,
        'input_detail': input_detail,
        'produce_detail': produce_detail,
        'seller': seller,
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/create_order.html', context)

@login_required
def marketplace_analytics(request):
    """Marketplace analytics for farmers"""
    # Sales analytics
    user_sales = Order.objects.filter(seller=request.user)
    monthly_sales = user_sales.filter(
        order_date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # Purchase analytics
    user_purchases = Order.objects.filter(buyer=request.user)
    monthly_purchases = user_purchases.filter(
        order_date__gte=timezone.now().date() - timedelta(days=30)
    ).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    # Product performance
    product_performance = OrderItem.objects.filter(
        order__seller=request.user
    ).values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_revenue')
    
    # Sales trends (last 6 months)
    sales_trends = user_sales.filter(
        order_date__gte=timezone.now().date() - timedelta(days=180)
    ).extra(
        select={'month': "date_trunc('month', order_date)"}
    ).values('month').annotate(
        sales=Sum('total_amount'),
        orders=Count('id')
    ).order_by('month')
    
    context = {
        'monthly_sales': monthly_sales,
        'monthly_purchases': monthly_purchases,
        'product_performance': product_performance,
        'sales_trends': json.dumps(list(sales_trends), default=str),
        'total_products': InputProduct.objects.filter(supplier=request.user).count() + 
                         ProduceProduct.objects.filter(farmer=request.user).count(),
        'active_page': 'marketplace'
    }
    
    return render(request, 'marketplace/marketplace_analytics.html', context)

# AJAX Views
@login_required
def add_to_cart(request, product_id):
    """AJAX view to add product to cart (simplified)"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = float(request.POST.get('quantity', 1))
        
        # In a full implementation, you'd use a cart session or model
        # For now, return success
        return JsonResponse({
            'success': True,
            'message': f'Added {quantity} units to cart',
            'product_name': product.name
        })
    
    return JsonResponse({'success': False})

@login_required
def update_order_status(request, order_id):
    """AJAX view to update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, seller=request.user)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Order status updated to {order.get_status_display()}'
            })
    
    return JsonResponse({'success': False})

@login_required
def product_search(request):
    """AJAX product search"""
    query = request.GET.get('q', '')
    if len(query) >= 2:
        products = Product.objects.filter(
            is_active=True,
            name__icontains=query
        ).values('id', 'name', 'category', 'product_type')[:10]
        
        return JsonResponse({
            'success': True,
            'products': list(products)
        })
    
    return JsonResponse({'success': False, 'products': []})
