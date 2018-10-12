import logging
from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User, BusinessUnit, Position
from .forms import BusinessUnitAdminForm

logger = logging.getLogger('django')


class RiskManagementAdmin(AdminSite):
    site_header = _('Administration N.H Risk Register')
    site_title = _('site d\'administration de NH Risk Management')


risk_management_admin_site = RiskManagementAdmin(name='admin-nh-risk-management')


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update(
        {"duplicate_username": _('Ce nom d\'utilisateur est déjà pris')}
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'civilite', 'first_name', 'last_name', 'telephone')

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError(self.error_messages["duplicate_username"])


class PositionInline(admin.TabularInline):
    model = Position


@admin.register(User, site=risk_management_admin_site)
class MyUserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = ((None, {'fields': ('email', 'password')}),
                 (_("Profil"), {"fields": ("civilite", "first_name", 'last_name',
                                           "telephone")}),
                 (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                                'groups', 'user_permissions')}),
                 (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                 )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'civilite', 'first_name', 'last_name', 'telephone', 'password1',
                       'password2')
        }
         ),
    )
    list_display = ("username", 'email', "first_name", "last_name",
                    "telephone", "is_superuser")
    search_fields = ["first_name", 'last_name']


@admin.register(BusinessUnit, site=risk_management_admin_site)
class BuAdmin(admin.ModelAdmin):
    form = BusinessUnitAdminForm
    list_display = ('denomination', 'sigle', 'marche', 'ville_siege',
                    'adresse_physique', 'telephone', 'site_web', 'bu_manager')
    search_fields = ['denomination']
    fieldsets = [
        (_('Infos'),
         {'fields': ['denomination', 'raison_sociale', 'sigle', 'marche', 'ville_siege', 'bu_manager', 'projet']}),
        (_('Contact'), {'fields': ['adresse_physique', 'adresse_postale', 'telephone', 'site_web']}),
    ]
    inlines = [PositionInline, ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            logger.info('New {} created.'.format(obj.get_bu_type()))
            obj.issue_notification('created', actor=request.user, target=obj)
            logger.info('Notification sent.')

    def delete_model(self, request, obj):
        super().save_model(request, obj)
        logger.info('Business unit {} was sucesffuly deleted.'.format(obj.denomination))
        obj.issue_notification('delete', actor=request.user, target=obj)
        logger.info('Notification sent.')
