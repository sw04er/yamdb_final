import uuid

from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import viewsets, status, filters, permissions, generics
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .paginators import StandardPagination
from .models import Category, Genre, Title, Review, User, UserToRegister
from .permissions import (IsAdminOrReadOnly, IsAdmin,
                          IsAuthorOrAdminOrModerator, IsAbleToChangeRoles)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSafeMethodSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer, UserSerializer)

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class UserViewSet(viewsets.ModelViewSet):
    """Retrieve, editing, creating and deleting all users's data"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    pagination_class = StandardPagination
    # Search for users/{username}/
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated, IsAbleToChangeRoles]
    )
    def user_personal_info(self, request):
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def send_email(request):
    to_email = request.data.get('email')
    if to_email is None:
        return Response({'message': 'There must be an email adress'})
    subject = 'Confirmation code'
    confirmation_code = uuid.uuid4()
    try:
        send_mail(
            subject=subject,
            message=str(confirmation_code),
            recipient_list=[to_email],
            fail_silently=False
        )
        UserToRegister.objects.update_or_create(
            email=to_email,
            defaults={'confirmation_code': confirmation_code}
        )
    except BadHeaderError:
        return Response({'message': 'Invalid header found'})
    return Response({'message': 'The email has been sent'})


@api_view(['POST'])
def send_token(request):
    email = request.data.get('email')
    confirmation_code = request.data.get('confirmation_code')
    # Check if a code and an email are valid
    try:
        user_to_register = UserToRegister.objects.get(email=email)
        if str(user_to_register.confirmation_code) != confirmation_code:
            return Response({'message': 'Invalid code'})
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email, 'password': confirmation_code}
        )
        # Delete this user from register query
        user_to_register.delete()
        # Create a token for him
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token)
        })
    except UserToRegister.DoesNotExist:
        return Response(
            {'message': 'You must recieve confirmation code firstly'}
        )


class MethodNotAllowed(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(viewsets.ModelViewSet, MethodNotAllowed):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class GenreViewSet(viewsets.ModelViewSet, MethodNotAllowed):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', 'slug')
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-id')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleSafeMethodSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrAdminOrModerator)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrAdminOrModerator,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(Review,
                                   title__pk=self.kwargs['title_id'],
                                   pk=self.kwargs['review_id'])
        return review.comments.all()
