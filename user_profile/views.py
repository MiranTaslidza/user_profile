from django.shortcuts import render

# Create your views here.
def all_user(request):
    return render(request, 'user_profile/all_user.html')
