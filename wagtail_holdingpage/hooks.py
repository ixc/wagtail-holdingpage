def allow_staff(request):
    """Allow access if the user doing the request can access the Wagtail admin.

    Uses Wagtail's ``wagtailadmin.access_admin`` permission rather than
    Django's ``is_staff`` flag, which Wagtail doesn't use.
    """
    user = getattr(request, "user", None)
    return bool(user and user.has_perm("wagtailadmin.access_admin"))
