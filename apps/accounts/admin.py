from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class UserCreationForm(forms.ModelForm):
	"""A form for creating new users. Includes all the required
	fields, plus a repeated password."""
	password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
	password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ("email", "name")

	def clean_password2(self):
		p1 = self.cleaned_data.get("password1")
		p2 = self.cleaned_data.get("password2")
		if p1 and p2 and p1 != p2:
			raise forms.ValidationError("Passwords don't match")
		return p2

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class UserChangeForm(forms.ModelForm):
	"""A form for updating users. Replaces the password field with
	a read-only hash display."""
	password = ReadOnlyPasswordHashField()

	class Meta:
		model = User
		fields = ("email", "name", "password", "is_active", "is_staff", "is_superuser")

	def clean_password(self):
		return self.initial.get("password")


class UserAdmin(BaseUserAdmin):
	form = UserChangeForm
	add_form = UserCreationForm

	list_display = ("email", "name", "is_staff", "is_superuser")
	list_filter = ("is_staff", "is_superuser", "is_active")
	fieldsets = (
		(None, {"fields": ("email", "password")}),
		("Personal info", {"fields": ("name",)}),
		("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
		("Important dates", {"fields": ("last_login",)}),
	)
	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "name", "password1", "password2"),
		}),
	)
	search_fields = ("email", "name")
	ordering = ("email",)
	filter_horizontal = ("groups", "user_permissions")


admin.site.register(User, UserAdmin)
