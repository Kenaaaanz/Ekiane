from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from ecommerce.admin import admin_site  # Import the custom admin site

from .models import GuestBuyer, Role, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = (
        'role',
        'phone_number',
        'company',
        'location',
        'marketing_opt_in',
        'interests',
        'notes',
    )
    extra = 0


class CustomUserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)
    list_display = DjangoUserAdmin.list_display + ('get_role', 'get_marketing_opt_in')
    list_select_related = ('profile',)

    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') and obj.profile else None
    get_role.short_description = 'Role'

    def get_marketing_opt_in(self, obj):
        return obj.profile.marketing_opt_in if hasattr(obj, 'profile') and obj.profile else False
    get_marketing_opt_in.boolean = True
    get_marketing_opt_in.short_description = 'Marketing Opt-In'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


# Register the custom User admin
admin_site.register(User, CustomUserAdmin)


@admin.register(GuestBuyer)
class GuestBuyerAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'source',
        'marketing_opt_in',
        'created_at',
    )
    list_filter = ('marketing_opt_in', 'source', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'notes')
    ordering = ('-created_at',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
