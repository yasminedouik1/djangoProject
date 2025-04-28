from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView,CreateView,UpdateView,DeleteView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import MenuItem, Basket, Order, OrderItem, UserProfile
from django.contrib import messages 

class DashboardView(TemplateView):
    template_name = 'resto/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['menu_items_count'] = MenuItem.objects.count()
        except Exception:
            context['menu_items_count'] = 0
        return context

class AboutView(TemplateView):
    template_name = 'resto/about.html'

class CommandesView(TemplateView):
    template_name = 'resto/commandes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            orders = Order.objects.filter(user=self.request.user).prefetch_related('orderitem_set__menu_item')
            # nehsbou fi total l kol commande
            orders_with_totals = []
            for order in orders:
                order_total = sum(item.menu_item.price * item.quantity for item in order.orderitem_set.all())
                orders_with_totals.append({
                    'order': order,
                    'total': order_total
                })
            context['orders_with_totals'] = orders_with_totals
        else:
            context['orders_with_totals'] = []
        return context

class MenuListView(ListView):
    model = MenuItem
    template_name = 'resto/menu_list.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category = self.kwargs.get('category')
        search_query = self.request.GET.get('search', '')

        if category and category != 'all':
            category_map = {
                'main': 'MAIN',
                'dessert': 'DESS',
                'drink': 'DRINK',
                'appetizer': 'APP'
            }
            queryset = queryset.filter(category=category_map.get(category))

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        address = request.POST['address']
        if User.objects.filter(username=username).exists():
            return render(request, 'resto/signup.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        user_profile = user.profile
        user_profile.phone_number = phone_number
        user_profile.address = address
        user_profile.save()
        return redirect('resto:login')
    return render(request, 'resto/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('resto:dashboard')
        else:
            return render(request, 'resto/login.html', {'error': 'Invalid credentials'})
    return render(request, 'resto/login.html')

def logout_view(request):
    logout(request)
    return redirect('resto:login')

@login_required
def add_to_basket(request, item_id):
    menu_item = MenuItem.objects.get(id=item_id)
    basket_item, created = Basket.objects.get_or_create(user=request.user, menu_item=menu_item)
    if not created:
        basket_item.quantity += 1
        basket_item.save()
    messages.success(request, "Added to basket successfully")
    return redirect('resto:menu_list')

@login_required
def basket_view(request):
    basket_items = Basket.objects.filter(user=request.user)
    # nehsbou fi total l kol haja mel menu eli fi panier
    basket_items_with_totals = []
    total_price = 0
    for item in basket_items:
        item_total = item.menu_item.price * item.quantity
        basket_items_with_totals.append({
            'item': item,
            'total': item_total
        })
        total_price += item_total

    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        
        if action == 'delete':
            Basket.objects.filter(user=request.user, id=item_id).delete()
        elif action == 'update_quantity':
            quantity = int(request.POST.get('quantity', 1))
            basket_item = Basket.objects.get(user=request.user, id=item_id)
            if quantity > 0:
                basket_item.quantity = quantity
                basket_item.save()
            else:
                basket_item.delete()
        elif action == 'confirm':
            order = Order.objects.create(user=request.user)
            for item in basket_items:
                OrderItem.objects.create(order=order, menu_item=item.menu_item, quantity=item.quantity)
            basket_items.delete()
            return redirect('resto:commandes')
        return redirect('resto:basket')

    return render(request, 'resto/basket.html', {
        'basket_items_with_totals': basket_items_with_totals,
        'total_price': total_price
    })

def update_order_status(request, order_id):
    if request.method == "POST":
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')  
        order.status = new_status
        order.save()
        return redirect('admin_orders')  

def view_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'commandes.html', {'orders': orders})
    else:
        return redirect('login')

@login_required
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status == 'PENDING':
            order.status = 'CANCELLED'
            order.save()
            messages.success(request, "Order cancelled successfully")
        else:
            messages.error(request, "Only pending orders can be cancelled")
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
    return redirect('resto:menu_list')

@login_required
def delete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status == 'CANCELLED':
            order.delete()
            messages.success(request, "Order deleted successfully")
        else:
            messages.error(request, "Only cancelled orders can be deleted")
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
    return redirect('resto:commandes')

"""

class MenuCreateView(CreateView):
    model = MenuItem
    template_name = 'resto/menu_form.html'
    fields = ['name', 'description', 'price', 'category', 'photo']
    success_url = reverse_lazy('resto:menu_list')

class MenuUpdateView(UpdateView):
    model = MenuItem
    template_name = 'resto/menu_form.html'
    fields = ['name', 'description', 'price', 'category', 'photo']
    success_url = reverse_lazy('resto:menu_list')

class MenuDeleteView(DeleteView):
    model = MenuItem
    template_name = 'resto/menu_confirm_delete.html'
    success_url = reverse_lazy('resto:menu_list')

"""