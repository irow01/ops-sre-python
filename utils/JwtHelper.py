from user import serializer, models
from rest_framework_jwt.utils import jwt_encode_handler


def generate_token(username):
    user_obj = models.User.objects.filter(username=username).first()
    user_data = serializer.UserSerializer(instance=user_obj, many=False)
    token = jwt_encode_handler(user_data.data)
    return token
