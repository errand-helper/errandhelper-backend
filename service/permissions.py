from rest_framework.permissions import BasePermission

class IsOwnerOfBusinessProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business.user == request.user