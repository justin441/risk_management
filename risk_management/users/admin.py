from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, BusinessUnit


class RiskManagementAdmin(AdminSite):
    site_header = _('Administration N.H Risk Register')
    site_title = _('site d\'administration de NH Risk Management')


risk_management_admin_site = RiskManagementAdmin(name='admin-nh-risk-management')


class MyUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": "This username has already been taken."}
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'civilite', 'first_name', 'last_name', 'fonction', 'telephone', 'business_unit')

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError(self.error_messages["duplicate_username"])


@admin.register(User, site=risk_management_admin_site)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = ((None, {'fields': ('email', 'password')}),
                 (_("Profil"), {"fields": ("civilite", "first_name", 'last_name', "fonction",
                                           "telephone", "business_unit")}),
                 (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                                'groups', 'user_permissions')}),
                 (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                 )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'civilite', 'first_name', 'last_name', 'business_unit', 'telephone', 'password1',
                       'password2')
        }
         ),
    )
    list_display = ("username", 'email', "first_name", "last_name", "fonction",
                    "telephone", "business_unit", "is_superuser")
    search_fields = ["first_name", 'last_name']
    list_filter = AuthUserAdmin.list_filter + ('business_unit',)


@admin.register(BusinessUnit, site=risk_management_admin_site)
class BuAdmin(admin.ModelAdmin):
    list_display = ('denomination', 'sigle', 'marche', 'ville_siege',
                    'adresse_physique', 'telephone', 'bu_manager')
    search_fields = ['denomination']
