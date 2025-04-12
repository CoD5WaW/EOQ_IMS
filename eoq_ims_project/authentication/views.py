from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        username = form.cleaned_data.get('username')
        messages.success(self.request, f"Welcome, {username}!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('authentication:login')  # This ensures redirection to login page
    http_method_names = ['get', 'post']  # Allow both GET and POST methods
    
    def dispatch(self, request, *args, **kwargs):
        # Perform the logout operation
        response = super().dispatch(request, *args, **kwargs)
        
        # Add success message that will be displayed on the login page
        messages.success(request, "You have successfully logged out.")
        
        # Return the response which will redirect to the login page
        return response