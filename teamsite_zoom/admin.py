from django.contrib import admin

from .models import (
    AssignedNumber,
    CallingPlan,
    OauthToken,
    ZoomProfile,
)

admin.site.register(CallingPlan)
admin.site.register(AssignedNumber)
admin.site.register(OauthToken)


class InlineZoomProfile(admin.TabularInline):
    model = ZoomProfile
    fields = ["zoom_id", "dept", "phone_number", "extension_number", "pic_url"]


class InlineCallingPlan(admin.TabularInline):
    model = CallingPlan
    fields = ["type", "name"]


class InlineAssignedNumber(admin.TabularInline):
    model = AssignedNumber
    fields = ["number", "location"]


@admin.register(ZoomProfile)
class ZoomProfileAdmin(admin.ModelAdmin):
    inlines = [InlineAssignedNumber, InlineCallingPlan]
    list_display = (
        "user_name",
        "dept",
        "phone_number",
        "extension_number",
        "assigned_numbers",
        "has_pic",
    )
    search_fields = ("user__username",)
    list_filter = ("dept",)

    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_name.admin_order_field = "user__first_name"

    @staticmethod
    def assigned_numbers(obj):
        return ", ".join([n.number for n in obj.assigned_numbers.all()])

    def has_pic(self, obj):
        return obj.pic_url is not None

    has_pic.boolean = True
