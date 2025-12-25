from django import forms


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=300,
        label="Full Name",
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your full name", "autocomplete": "name"}
        ),
    )
    email = forms.EmailField(
        max_length=254,
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "autocomplete": "new-password",
            }
        ),
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )
    )
