import jwt
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication, jwt_decode_handler
from rest_framework import exceptions
from user import models


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):

    def authenticate(self, request):
        jwt_value = request.META.get('HTTP_X_TOKEN')
        if jwt_value is None:
            # return None
            raise exceptions.AuthenticationFailed()
        try:
            payload = jwt_decode_handler(jwt_value)
            username = payload['username']
            uuid = payload['uuid']
            user = models.User.objects.filter(username=username, uuid=uuid)
            if not user:
                raise jwt.ExpiredSignature
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed()
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        pass
