from rest_framework import permissions, generics
from rest_framework.response import Response
from account import serializers


class ProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user
