from django.contrib.auth import get_user_model

from .forms import SignUpForm

User = get_user_model()


def create_user_from_signup_form(form: SignUpForm):
    return User.objects.create_user(
        username=form.cleaned_data["username"],
        email=form.cleaned_data["email"],
        password=form.cleaned_data["password1"],
        first_name=form.cleaned_data.get("first_name", ""),
        last_name=form.cleaned_data.get("last_name", ""),
    )
