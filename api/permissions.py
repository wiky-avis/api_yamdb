from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrModerator(BasePermission):
    pass


class IsAdminOrReadOnly(BasePermission):
    pass


class IsAdmin(BasePermission):
    pass
