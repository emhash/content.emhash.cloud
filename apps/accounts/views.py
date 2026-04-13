from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render

from .forms import LoginForm, SignUpForm
from .services import create_user_from_signup_form


def home_or_login(request):
	if request.user.is_authenticated:
		return redirect("content:dashboard")

	form = LoginForm(request, data=request.POST or None)
	if request.method == "POST":
		if form.is_valid():
			login(request, form.get_user())
			return redirect("content:dashboard")
		messages.error(request, "Invalid email or password.")

	return render(request, "accounts/login.html", {"form": form})


def signup_view(request):
	if request.user.is_authenticated:
		return redirect("content:dashboard")

	form = SignUpForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		user = create_user_from_signup_form(form)
		login(request, user)
		messages.success(request, "Your account has been created.")
		return redirect("content:dashboard")

	return render(request, "accounts/signup.html", {"form": form})


def logout_view(request):
	if request.user.is_authenticated:
		logout(request)
	return redirect("content:home")
