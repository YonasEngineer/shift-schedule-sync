from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
# Create your views here.


# @ensure_csrf_cookie
def create_shift(request):
    if request.method == "GET":
        csrf_token = request.COOKIES.get("csrftoken")
        print("CSRF TOKEN:", csrf_token)
        return HttpResponse("Success")
    # print(request)


@csrf_exempt
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print("user", user)
    if user is not None:
        login(request, user)  # creates session
        return HttpResponse("Logged in",)
    else:
        return HttpResponse("Invalid credentials")


def logout_view(request):
    logout(request)
    return HttpResponse("Logged out")


def dashboard(request):
    if request.user.is_authenticated:
        return HttpResponse("Welcome")
    else:
        return HttpResponse("Not logged in")
