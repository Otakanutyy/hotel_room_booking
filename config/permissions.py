from rest_framework.permissions import BasePermission


class IsStaffOrSuperuser(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))
        )
