from django.db import models
from django.conf import settings
from apps.farms.models import Farm, CropCycle

class Transaction(models.Model):
    """Base model for all financial transactions"""
    
    class TransactionType(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
        TRANSFER = 'transfer', 'Transfer'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField()
    
    # Payment information
    payment_method = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} ({self.date})"
    
    class Meta:
        ordering = ['-date', '-created_at']

class Income(models.Model):
    """Model for tracking income"""
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, primary_key=True)
    
    class IncomeSource(models.TextChoices):
        CROP_SALE = 'crop_sale', 'Crop Sale'
        LIVESTOCK_SALE = 'livestock_sale', 'Livestock Sale'
        RENTAL = 'rental', 'Equipment/Land Rental'
        SUBSIDY = 'subsidy', 'Government Subsidy'
        OTHER = 'other', 'Other'
    
    source = models.CharField(max_length=20, choices=IncomeSource.choices)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='income_records')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)  # kg, tons, etc.
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buyer_name = models.CharField(max_length=255, blank=True)
    buyer_contact = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.get_source_display()} - {self.transaction.amount}"

class Expense(models.Model):
    """Model for tracking expenses"""
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, primary_key=True)
    
    class ExpenseCategory(models.TextChoices):
        SEEDS = 'seeds', 'Seeds'
        FERTILIZER = 'fertilizer', 'Fertilizer'
        PESTICIDE = 'pesticide', 'Pesticide'
        EQUIPMENT = 'equipment', 'Equipment'
        LABOR = 'labor', 'Labor'
        FUEL = 'fuel', 'Fuel'
        RENT = 'rent', 'Land Rent'
        UTILITIES = 'utilities', 'Utilities'
        MAINTENANCE = 'maintenance', 'Maintenance'
        TRANSPORTATION = 'transportation', 'Transportation'
        INSURANCE = 'insurance', 'Insurance'
        LOAN_PAYMENT = 'loan_payment', 'Loan Payment'
        OTHER = 'other', 'Other'
    
    category = models.CharField(max_length=20, choices=ExpenseCategory.choices)
    crop_cycle = models.ForeignKey(CropCycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='expense_records')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)  # kg, hours, liters, etc.
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_contact = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.transaction.amount}"

class Budget(models.Model):
    """Model for farm budgets and financial planning"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Budget period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Budget amounts
    total_planned_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_planned_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def planned_profit(self):
        return self.total_planned_income - self.total_planned_expenses
    
    @property
    def actual_income(self):
        # Calculate actual income within the budget period
        return Transaction.objects.filter(
            user=self.user,
            farm=self.farm,
            transaction_type='income',
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    @property
    def actual_expenses(self):
        # Calculate actual expenses within the budget period
        return Transaction.objects.filter(
            user=self.user,
            farm=self.farm,
            transaction_type='expense',
            date__gte=self.start_date,
            date__lte=self.end_date
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    
    @property
    def actual_profit(self):
        return self.actual_income - self.actual_expenses

class BudgetItem(models.Model):
    """Model for individual budget items"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    
    class ItemType(models.TextChoices):
        SELECT = '', 'Select Type'
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
    
    item_type = models.CharField(max_length=10, choices=ItemType.choices, default=ItemType.SELECT)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    variance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Optional fields
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - {self.amount}"

class FinancialReport(models.Model):
    """Model for generated financial reports"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_reports')
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='financial_reports', null=True, blank=True)
    title = models.CharField(max_length=255)
    
    # Report period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report type
    REPORT_TYPE_CHOICES = [
        ('income_statement', 'Income Statement'),
        ('expense_report', 'Expense Report'),
        ('profit_loss', 'Profit & Loss'),
        ('budget_comparison', 'Budget Comparison'),
        ('crop_profitability', 'Crop Profitability'),
    ]
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    
    # Report data
    report_data = models.JSONField(default=dict)
    
    # Report file
    report_file = models.FileField(upload_to='financial_reports/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"
