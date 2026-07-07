from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Order  
from datetime import datetime

@login_required
def dashboard_view(request):
    user = request.user
    # Database keywords ke hisab se '-date' use kiya hai
    orders = Order.objects.filter(employee=user).order_by('-date')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        orders = orders.filter(date__date__range=[start_date, end_date])

    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')