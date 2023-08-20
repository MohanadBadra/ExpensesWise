from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from validate_email import validate_email
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import json

import threading

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)

# Create your views here.
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email'] 
        if not validate_email(email):
            return JsonResponse({'email_error': 'email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'email is already exists, enter an other email pleas'}, status=409)

        return JsonResponse({'email_valid': True})

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'username is already exists, enter an other username pleas'}, status=409)

        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        # GET USER DATA
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        # VALIDATE
        if not User.objects.filter(username=username).exists():
            if len(password) < 6:
                messages.error(request, 'Password is too short')
                return render(request, 'authentication/register.html', context)
            
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = False
            user.save()
            

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link = reverse('activate', kwargs={'uidb64': uidb64, 'token':token_generator.make_token(user)})
            
            activate_url = 'http://'+domain+link

            email_body = f'Welcome {user.username} Pleas use this link below to verify your account and active it:\n {activate_url}'
            email = EmailMessage(
                "Activate you account",
                email_body,
                "noreply@expensewise.com",
                [email],
            )

            EmailThread(email).start()
            messages.success(request, 'Account successfully created')
            return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')
        

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message'+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')
    
        except Exception as ex:
            pass

        return redirect('login')
    
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f"Welcome {user.username}, You have Logged In")
                    return redirect('transactions')

                messages.error(request, 'Account have not activated yet, check your Email to activate it')
                return render(request, 'authentication/login.html')
            
            messages.error(request, "Incorrect username or password.")
            return render(request, 'authentication/login.html')
        messages.error(request, "Pleas fill all fields")
        return render(request, 'authentication/login.html')
    
class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been Logged Out")
        return redirect('login')
    
class RequestPassword(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']
        context = {'values': request.POST}
        if not validate_email(email):
            messages.error(request, 'Pleas supply a valid email')
            return render(request, 'authentication/reset-password.html', context)

        domain = get_current_site(request).domain
        user = User.objects.filter(email=email)
        
        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            link = reverse('reset-password', kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user[0])})
            
            reset_url = 'http://'+domain+link

            email_body = f'Welcome {user[0].username} Pleas use this link below to Reset your Password:\n {reset_url}'
            email = EmailMessage(
                "Reset your Password",
                email_body,
                "noreply@expensewise.com",
                [email],
            )

            EmailThread(email).start()
        
            messages.success(request, 'We have sent you an email to Reset your Password')
            
            return redirect('login')

        else:
            messages.error(request, 'There is no user by that email')


        return render(request, 'authentication/reset-password.html')
    
class ResetPassword(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, Pleas request a new link')
                return render(request, 'authentication/reset-password.html')

            return render(request, 'authentication/set-new-password.html', context)
        
        except Exception as identifier:
            messages.info(request, 'Something went wrong')

        return render(request, 'authentication/set-new-password.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Two Passwords don\'t match')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password is too Short')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password Rested Successfully')
            return redirect('login')
        
        except Exception as identifier:

            messages.info(request, 'Something went wrong')
            return render(request, 'authentication/login.html', context)
