from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .models import CustomUser
import json


@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            profile_photo = request.FILES.get('profile_photo')

            if not all([username, email, password, password2, profile_photo]):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            if password != password2:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)

            profile_photo_path = None
            if profile_photo:
                profile_photo_path = default_storage.save(f'profile_photos/{profile_photo.name}', profile_photo)

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            if profile_photo_path:
                user.profile_photo = profile_photo_path
            user.save()

            return JsonResponse({'message': 'User registered successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                response_data = {
                    'userid': user.id,
                }
                return JsonResponse(response_data, status=200)

            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def profile_view(request):
    userid = request.GET.get('userid')
    if not userid:
        return JsonResponse({'error': 'userid is required'}, status=400)

    user = get_object_or_404(CustomUser, id=userid)

    profile_photo_url = (
        request.build_absolute_uri(user.profile_photo.url)
        if user.profile_photo
        else None
    )

    data = {
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'profile_photo': profile_photo_url,
    }
    return JsonResponse(data, status=200)