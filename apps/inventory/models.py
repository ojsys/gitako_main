from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class InventoryItem(models.Model):
    """Base model for all inventory items"""
    
    class ItemType(models.TextChoices):
        EQUIPMENT = 'equipment', 'Equipment'
        INPUT = 'input', 'Farm Input'
        TOOL = 'tool', 'Tool'
        VEHICLE = 'vehicle', 'Vehicle'
        INFRASTRUCTURE = 'infrastructure', 'Infrastructure'
        OTHER = 'other', 'Other'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory_items')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='inventory_items', null=True, blank=True)
    
    # Item details
    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=20, choices=ItemType.choices)
    description = models.TextField(blank=True)
    
    # Quantity and unit
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=50, blank=True)  # kg, liter, piece, etc.
    
    # Status
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('depleted', 'Depleted'),
        ('disposed', 'Disposed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Location
    storage_location = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    acquisition_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Equipment(models.Model):
    """Extended details for equipment inventory items"""
    inventory_item = models.OneToOneField(InventoryItem, on_delete=models.CASCADE, primary_key=True)
    
    # Equipment details
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Technical specifications
    power_source = models.CharField(max_length=100, blank=True)  # diesel, electric, etc.
    horsepower = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capacity = models.CharField(max_length=100, blank=True)
    
    # Financial information
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval_days = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.inventory_item.name} - {self.brand} {self.model}"

class FarmInput(models.Model):
    """Extended details for farm input inventory items"""
    inventory_item = models.OneToOneField(InventoryItem, on_delete=models.CASCADE, primary_key=True)
    
    # Input details
    input_category = models.CharField(max_length=100)  # fertilizer, seed, pesticide, etc.
    brand = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    
    # Batch information
    batch_number = models.CharField(max_length=100, blank=True)
    production_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Purchase information
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=255, blank=True)
    
    # Usage information
    application_rate = models.CharField(max_length=100, blank=True)  # e.g., "2kg per hectare"
    target_crops = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"{self.inventory_item.name} - {self.input_category}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

class InventoryTransaction(models.Model):
    """Model for tracking inventory movements"""
    
    class TransactionType(models.TextChoices):
        PURCHASE = 'purchase', 'Purchase'
        USAGE = 'usage', 'Usage'
        TRANSFER = 'transfer', 'Transfer'
        ADJUSTMENT = 'adjustment', 'Adjustment'
        DISPOSAL = 'disposal', 'Disposal'
    
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    
    # Transaction details
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
    # Related information
    related_activity = models.ForeignKey('activities.Activity', on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    related_farm = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    
    # Financial information
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # User who performed the transaction
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory_transactions')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.inventory_item.name} ({self.quantity})"
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def save(self, *args, **kwargs):
        # Calculate total price if unit price is provided
        if self.unit_price is not None:
            self.total_price = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
        
        # Update inventory item quantity
        item = self.inventory_item
        if self.transaction_type == 'purchase':
            item.quantity += self.quantity
        elif self.transaction_type in ['usage', 'disposal']:
            item.quantity -= self.quantity
            # Update status if depleted
            if item.quantity <= 0:
                item.status = 'depleted'
        elif self.transaction_type == 'adjustment':
            # For adjustments, the quantity represents the new total
            item.quantity = self.quantity
        
        item.save()

class MaintenanceRecord(models.Model):
    """Model for equipment maintenance records"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    
    # Maintenance details
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(max_length=100)  # routine, repair, etc.
    description = models.TextField()
    
    # Cost information
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    parts_replaced = models.TextField(blank=True)
    
    # Service provider
    service_provider = models.CharField(max_length=255, blank=True)
    technician_name = models.CharField(max_length=255, blank=True)
    
    # Next maintenance
    next_maintenance_date = models.DateField(null=True, blank=True)
    
    # User who recorded the maintenance
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='maintenance_records')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.equipment.inventory_item.name} - {self.maintenance_type} ({self.maintenance_date})"
    
    class Meta:
        ordering = ['-maintenance_date']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update equipment's last maintenance date
        equipment = self.equipment
        equipment.last_maintenance_date = self.maintenance_date
        
        # Update next maintenance date if provided
        if self.next_maintenance_date:
            equipment.next_maintenance_date = self.next_maintenance_date
        elif equipment.maintenance_interval_days:
            from datetime import timedelta
            equipment.next_maintenance_date = self.maintenance_date + timedelta(days=equipment.maintenance_interval_days)
        
        equipment.save()
