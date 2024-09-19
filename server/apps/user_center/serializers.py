from rest_framework import serializers

from .models import ExternalUser, ExternalOauth, UserBehavior, UserCollect


class ExternalUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalUser  # 假设你的用户模型是 User
        fields = '__all__'  # 或者指定具体的字段列表
        read_only_fields = ('id', 'mini_openid', 'unionid', 'openid')  # 设置只读字段

    def update(self, instance, validated_data):
        # 更新实例，排除只读字段
        for attr, value in validated_data.items():
            if attr not in self.Meta.read_only_fields:
                setattr(instance, attr, value)
        instance.save()
        return instance


class ExternalUserSerializer(serializers.ModelSerializer):
    """外部用户序列化"""

    class Meta:
        model = ExternalUser
        # fields = '__all__'

        exclude = ['password']


class ExternalOauthSerializer(serializers.ModelSerializer):
    """外部授权序列化"""

    class Meta:
        model = ExternalOauth
        fields = '__all__'


class LogReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehavior
        fields = '__all__'


class UserCollectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCollect
        fields = '__all__'
