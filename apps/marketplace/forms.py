from django import forms
from django.contrib.auth.models import User
from .models import Product, InputProduct, ProduceProduct, Order, Review
from apps.farms.models import Farm, Crop


class ProductForm(forms.ModelForm):
    """Base form for marketplace products"""
    
    class Meta:
        model = Product
        fields = ['name', 'description', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your product'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Product category'
            })
        }


class InputProductForm(forms.ModelForm):
    """Form for farm input products"""
    
    class Meta:
        model = InputProduct
        fields = [
            'brand', 'manufacturer', 'unit', 'price',
            'min_order_quantity', 'stock_quantity', 'usage_instructions'
        ]
        widgets = {
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brand name'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manufacturer'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., kg, liters, pieces'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'min_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '1'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0'
            }),
            'usage_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Usage instructions'
            })
        }


class ProduceProductForm(forms.ModelForm):
    """Form for farm produce products"""
    
    class Meta:
        model = ProduceProduct
        fields = [
            'farm', 'crop', 'variety', 'grade', 'unit', 'price_per_unit',
            'available_quantity', 'min_order_quantity', 'harvest_date',
            'available_from', 'organic'
        ]
        widgets = {
            'farm': forms.Select(attrs={'class': 'form-control'}),
            'crop': forms.Select(attrs={'class': 'form-control'}),
            'variety': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Crop variety'
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Grade (A, B, C, etc.)'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., kg, bags, tons'
            }),
            'price_per_unit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'available_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'min_order_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'harvest_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'available_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'organic': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Filter farms to user's farms
            self.fields['farm'].queryset = Farm.objects.filter(owner=self.user)
            # All crops are available
            self.fields['crop'].queryset = Crop.objects.all()


class OrderForm(forms.ModelForm):
    """Form for creating orders"""
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_country', 'shipping_phone', 'buyer_notes'
        ]
        widgets = {
            'shipping_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'shipping_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'shipping_country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Nigeria'
            }),
            'shipping_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'buyer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special instructions or notes'
            })
        }


class ReviewForm(forms.ModelForm):
    """Form for product reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product'
            })
        }


class MarketplaceSearchForm(forms.Form):
    """Form for marketplace search and filtering"""
    
    PRODUCT_TYPE_CHOICES = [
        ('', 'All Products'),
        ('input', 'Farm Inputs'),
        ('produce', 'Farm Produce')
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    
    product_type = forms.ChoiceField(
        choices=PRODUCT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Category'
        })
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01'
        })
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )