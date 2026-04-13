from django.shortcuts import render
from .models import CustomUser
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
# Create your views here.


@csrf_exempt
def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('data', data)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phone_number')
            role = data.get('role')
            if not username or not email or not password:
                return JsonResponse({'error': 'missing fields'}, status=400)
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                role=role
            )
            return JsonResponse({'message': 'user created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return JsonResponse({'error': 'Missing credentials'}, status=400)
              # authenticate user
            user = authenticate(request, username=email, password=password)
            print("see the logged in user userDetail", user)
            print(user.id)
            print(user.email)
            print(user.username)
            if user is None:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            login(request, user)
            return JsonResponse({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            })
            # return JsonResponse({'message': "Logged in successfully"}, status=200)

            # if not user:
            #     return JsonResponse({'error': "AN authorized"}, status=403)
            # else:
            #     return JsonResponse({'message': "logged in successfully"}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
