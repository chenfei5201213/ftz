from rest_framework import serializers

from .models import ExternalUser, ExternalOauth


class ExternalUserSerializer(serializers.ModelSerializer):
    """外部用户序列化"""

    class Meta:
        model = ExternalUser
        fields = '__all__'


class ExternalOauthSerializer(serializers.ModelSerializer):
    """外部授权序列化"""

    class Meta:
        model = ExternalOauth
        fields = '__all__'
