from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from .models import Budget, BudgetItem, Transaction
from .forms import BudgetForm, BudgetItemForm
from apps.farms.models import Farm

@login_required
def budget_dashboard(request):
    """Display the budget dashboard with summary information and charts."""
    # Get active budgets (current date falls between start_date and end_date)
    today = timezone.now().date()
    active_budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=today,
        end_date__gte=today
    )
    active_budgets_count = active_budgets.count()
    
    # Get recent budgets
    recent_budgets = Budget.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Calculate total planned income and expenses
    budget_totals = Budget.objects.filter(user=request.user).aggregate(
        total_planned_income=Sum('total_planned_income'),
        total_planned_expenses=Sum('total_planned_expenses')
    )
    
    total_planned_income = budget_totals['total_planned_income'] or 0
    total_planned_expenses = budget_totals['total_planned_expenses'] or 0
    projected_profit = total_planned_income - total_planned_expenses
    
    # Get income and expense categories for charts
    income_items = BudgetItem.objects.filter(
        budget__user=request.user,
        item_type='income'
    )
    
    expense_items = BudgetItem.objects.filter(
        budget__user=request.user,
        item_type='expense'
    )
    
    # Check if we have data for charts
    has_budgets = Budget.objects.filter(user=request.user).exists()
    has_income_categories = income_items.exists()
    has_expense_categories = expense_items.exists()
    
    context = {
        'active_budgets_count': active_budgets_count,
        'recent_budgets': recent_budgets,
        'total_planned_income': total_planned_income,
        'total_planned_expenses': total_planned_expenses,
        'projected_profit': projected_profit,
        'budgets': has_budgets,
        'income_categories': has_income_categories,
        'expense_categories': has_expense_categories,
    }
    
    return render(request, 'financials/budget_dashboard.html', context)

@login_required
def budget_list(request):
    """View to display all budgets for the user"""
    # Get all budgets for the user
    budgets = Budget.objects.filter(user=request.user).select_related('farm')
    
    # Filter by farm if provided
    farm_filter = request.GET.get('farm')
    if farm_filter:
        budgets = budgets.filter(farm__id=farm_filter)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        budgets = budgets.filter(status=status_filter)
    
    # Get user's farms for filtering
    farms = Farm.objects.filter(owner=request.user)
    
    context = {
        'budgets': budgets,
        'farms': farms,
        'farm_filter': farm_filter,
        'status_filter': status_filter,
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_list.html', context)

@login_required
def budget_detail(request, budget_id):
    """View to display details of a specific budget"""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    # Get budget items
    income_items = budget.items.filter(item_type='income')
    expense_items = budget.items.filter(item_type='expense')
    budget_items = budget.items.all().order_by('item_type', 'category')
    
    # Calculate actual transactions within budget period
    actual_income = Transaction.objects.filter(
        user=request.user,
        farm=budget.farm,
        transaction_type='income',
        date__gte=budget.start_date,
        date__lte=budget.end_date
    ).select_related('income')
    
    actual_expenses = Transaction.objects.filter(
        user=request.user,
        farm=budget.farm,
        transaction_type='expense',
        date__gte=budget.start_date,
        date__lte=budget.end_date
    ).select_related('expense')
    
    # Calculate totals
    total_actual_income = actual_income.aggregate(total=Sum('amount'))['total'] or 0
    total_actual_expenses = actual_expenses.aggregate(total=Sum('amount'))['total'] or 0
    actual_profit = total_actual_income - total_actual_expenses
    
    # Calculate variance
    income_variance = total_actual_income - budget.total_planned_income
    expense_variance = total_actual_expenses - budget.total_planned_expenses
    profit_variance = actual_profit - budget.planned_profit
    
    context = {
        'budget': budget,
        'budget_items': budget_items,
        'income_items': income_items,
        'expense_items': expense_items,
        'actual_income': actual_income,
        'actual_expenses': actual_expenses,
        'total_actual_income': total_actual_income,
        'total_actual_expenses': total_actual_expenses,
        'actual_profit': actual_profit,
        'income_variance': income_variance,
        'expense_variance': expense_variance,
        'profit_variance': profit_variance,
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_detail.html', context)


@login_required
def budget_create(request):
    """View to create a new budget"""
    if request.method == 'POST':
        print("POST request received")  # Debug line
        form = BudgetForm(request.POST, user=request.user)
        print(f"Form data: {request.POST}")  # Debug line
        print(f"Form is valid: {form.is_valid()}")  # Debug line
        
        if form.is_valid():
            print("Form is valid, saving...")  # Debug line
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully!')
            return redirect('financials:budget_detail', budget_id=budget.id)
        else:
            print(f"Form errors: {form.errors}")  # Debug line
            print(f"Non-field errors: {form.non_field_errors()}")  # Debug line
    else:
        form = BudgetForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Budget',
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_form.html', context)

@login_required
def budget_update(request, budget_id):
    """View to update an existing budget"""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully!')
            return redirect('financials:budget_detail', budget_id=budget.id)
    else:
        form = BudgetForm(instance=budget, user=request.user)
    
    context = {
        'form': form,
        'budget': budget,
        'title': 'Update Budget',
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_form.html', context)

@login_required
def budget_delete(request, budget_id):
    """View to delete a budget"""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('financials:budget_list')
    
    context = {
        'budget': budget,
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_confirm_delete.html', context)

@login_required
def budget_item_create(request, budget_id):
    """View to add a new item to a budget"""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.budget = budget
            item.save()
            
            # Update budget totals
            if item.item_type == 'income':
                budget.total_planned_income += item.amount
            else:  # expense
                budget.total_planned_expenses += item.amount
            budget.save()
            
            messages.success(request, 'Budget item added successfully!')
            return redirect('financials:budget_detail', budget_id=budget.id)
    else:
        form = BudgetItemForm()
    
    context = {
        'form': form,
        'budget': budget,
        'title': 'Add Budget Item',
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_item_form.html', context)

@login_required
def budget_item_update(request, item_id):
    """View to update a budget item"""
    item = get_object_or_404(BudgetItem, id=item_id, budget__user=request.user)
    budget = item.budget
    old_amount = item.amount
    old_type = item.item_type
    
    if request.method == 'POST':
        form = BudgetItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            
            # Update budget totals
            if old_type == 'income':
                budget.total_planned_income -= old_amount
            else:  # expense
                budget.total_planned_expenses -= old_amount
                
            if updated_item.item_type == 'income':
                budget.total_planned_income += updated_item.amount
            else:  # expense
                budget.total_planned_expenses += updated_item.amount
                
            budget.save()
            
            messages.success(request, 'Budget item updated successfully!')
            return redirect('financials:budget_detail', budget_id=budget.id)
    else:
        form = BudgetItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'budget': budget,
        'title': 'Update Budget Item',
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_item_form.html', context)

@login_required
def budget_item_delete(request, item_id):
    """View to delete a budget item"""
    item = get_object_or_404(BudgetItem, id=item_id, budget__user=request.user)
    budget = item.budget
    
    if request.method == 'POST':
        # Update budget totals
        if item.item_type == 'income':
            budget.total_planned_income -= item.amount
        else:  # expense
            budget.total_planned_expenses -= item.amount
        budget.save()
        
        item.delete()
        messages.success(request, 'Budget item deleted successfully!')
        return redirect('financials:budget_detail', budget_id=budget.id)
    
    context = {
        'item': item,
        'budget': budget,
        'active_page': 'financials'
    }
    
    return render(request, 'financials/budget_item_confirm_delete.html', context)
