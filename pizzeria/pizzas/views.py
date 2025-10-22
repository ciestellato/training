from django.shortcuts import render

from .models import Pizza

# Create your views here.
def index(request):
    """ピザのホームページ"""
    return render(request, 'pizzas/index.html')

def pizzas(request):
    """ピザの一覧"""
    pizzas = Pizza.objects.order_by('date_added')
    context = {'pizzas': pizzas}
    return render(request, 'pizzas/pizzas.html', context)

def pizza(request, pizza_id):
    """ピザのトッピング"""
    pizza = Pizza.objects.get(id=pizza_id)
    toppings = pizza.topping_set.order_by('-date_added')
    context = {'pizza': pizza, 'toppings': toppings}
    return render(request, 'pizzas/pizza.html', context)