from rest_framework import serializers
from django.contrib.auth.models import User
from tracker.models import Account 

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Auto-create Account for this user
        Account.objects.create(user=user)

        return user