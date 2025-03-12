from django import forms
from .models import CustomUser, Course, Enrollment


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "profile_photo"]

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        password_confirm = self.cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return password_confirm


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "tags", "content"]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["course"]
