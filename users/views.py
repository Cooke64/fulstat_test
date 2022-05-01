from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .permissions import IsAdmin, IsUser
from .serializers import (
    SignUpSerializer, ConformationCodeSerializer, UserSerializer,
    JustUserSerializer)
from .models import User
from .services import send_code_to_email, get_tokens_for_user

OK_STATUS = status.HTTP_200_OK
BAD_STATUS = status.HTTP_400_BAD_REQUEST


class UserCreate(APIView):
    """Вью для отображения регистрации пользователя и
    отправки сообщения на указанный mail кода подтверждения.
    """
    queryset = get_user_model()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            serializer.save()
            send_code_to_email(username, email)
            return JsonResponse({'email': email, 'username': username},
                                status=OK_STATUS)


class TokenAPIView(APIView):
    """Вью для подтверждения полного доступа к
    сайту зарегистрированного пользователя.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = ConformationCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                username = serializer.validated_data['username']
                code = serializer.data['confirmation_code']
            except ValueError as e:
                raise e
            user = get_object_or_404(User, username=username)
            if code == user.confirmation_code:
                token = get_tokens_for_user(user)
                user.is_active = True
                user.save()
                return JsonResponse({'token': token}, status=OK_STATUS)
            return JsonResponse(
                {'Статус': 'Неверный код подтверждения'}, status=BAD_STATUS)


class UserAPIView(ModelViewSet):
    """Вью для отображения всех пользователей сайта."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = ([IsAdmin, ])
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    def get_object(self):
        return get_object_or_404(
            self.queryset, username=self.kwargs["username"])

    @action(
        methods=('get', 'patch',), detail=False,
        url_path='me', permission_classes=([IsUser, ]),
        serializer_class=JustUserSerializer
    )
    def get_me(self, request):
        try:
            user = User.objects.get(username=request.user.username)
        except ObjectDoesNotExist as e:
            raise e
        if request.method == 'get':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=OK_STATUS)
        try:
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=OK_STATUS)
        except ValidationError as e:
            raise e
