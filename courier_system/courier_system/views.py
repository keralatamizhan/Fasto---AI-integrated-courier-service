from django.shortcuts import render
from django.contrib import messages

def home(request):
    return render(request, 'public/home.html')

def about(request):
    return render(request, 'public/about.html')

def services(request):
    return render(request, 'public/services.html')

def contact(request):
    if request.method == 'POST':
        # Simulated contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # In a real application, you would send an email here
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return render(request, 'public/contact.html')
    
    return render(request, 'public/contact.html')
