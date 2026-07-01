from django.shortcuts import render , redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup_view(req):
    if req.method == 'POST':
        form = UserCreationForm(req.POST)
        if form.is_valid():
            user = form.save()
            login(req , user)
            return redirect('home')
    else :
        form = UserCreationForm()
    
    return render(req , 'registration/signup.html' , {'form' : form})



def redirect_to_home(request, exception=None):
    return redirect('home')