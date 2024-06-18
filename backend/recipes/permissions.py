from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAdminOrAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (request.user == obj.author)
            or request.user.is_staff
        )
