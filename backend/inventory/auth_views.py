from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

class PublicUserListView(APIView):
    """Returns only usernames — used by login page dropdown. No password info exposed."""
    permission_classes = [AllowAny]

    def get(self, request):
        usernames = list(User.objects.filter(is_active=True).values_list('username', flat=True).order_by('username'))
        return Response(usernames)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'is_admin': user.is_staff
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserManagementView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all().values('id', 'username', 'is_staff')
        return Response(list(users))

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        is_admin = request.data.get('is_admin', False)
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = is_admin
        user.save()
        return Response({'message': 'User created successfully'})

    def put(self, request, user_id=None):
        if not user_id:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            if 'password' in request.data and request.data['password']:
                user.set_password(request.data['password'])
            if 'is_admin' in request.data:
                user.is_staff = request.data['is_admin']
            user.save()
            return Response({'message': 'User updated successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id=None):
        if not user_id:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.id == user_id:
            return Response({'error': 'Cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
