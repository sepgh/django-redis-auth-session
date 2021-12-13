from django.apps import apps
from django.conf import settings
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class SessionTokenAuthentication(TokenAuthentication):
    """
      Normal behavior of TokenAuthentication is that it takes token from our header,
    Then it will query "Token" model with related token and will return the user of that model/row

      We are overriding that behavior. Using token from authorization header, we are storing loading the user_id
    from session, and then select the user using its primary key
    """

    def __init__(self):
        super(SessionTokenAuthentication, self).__init__()
        self.request = None

    def authenticate(self, request):
        self.request = request
        super(SessionTokenAuthentication, self).authenticate(request)

    def authenticate_credentials(self, key):
        user_id = self.request.session.get("user_id")
        if user_id is not None:
            user_model: Model = apps.get_model(settings.AUTH_USER_MODEL)
            try:
                user = user_model.objects.get(id=user_id)
            except Model.DoesNotExist:
                raise exceptions.AuthenticationFailed(_('Invalid token.'))
            if hasattr(user, "is_active") and not user.is_active:
                raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
            return (user, key)
        else:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
