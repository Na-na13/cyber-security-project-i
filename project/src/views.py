import html
import sqlite3
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Message
from django.views.decorators.cache import cache_control
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from axes.decorators import axes_dispatch


# @cache_control(no_cache=True, no_store=True)
def index(request):
    return render(request, 'pages/index.html')

def create(request):
    return render(request, 'pages/create.html')

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required
def logged(request):
    # Flaw 1: No automatic logout after specified idle time.
    # Fix: Session cookie age in 'settings.py'.

    # Flaw 2: After logout, user can browse back to cached pages which require login.
    # Fix: Cache control for views which require login.

    current_user = request.user
    users = ['all'] + list(User.objects.exclude(username=current_user))
    messages = list(Message.objects.filter(
        receiver=current_user)) + list(Message.objects.filter(
        receiver='all'))
    return render(request, 'pages/logged.html', {"user": current_user, "users": users,"messages": messages})


def admin_check(user):
    return user.is_staff

# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# @login_required
# @user_passes_test(admin_check)
def admin(request, messages = None):
    # Flaw: Possibility for force browsing to admin pages/elevation of priviledges for logged in user.
    # Fix: In admin pages, check if user actually has admin priviledges with @user_passes_test -decorator.
    # If user doesn't pass the check, user will be redirected to login page.

    current_user = request.user
    users = ['all'] + list(User.objects.exclude(username=current_user))
    if messages is None:
        messages = list(Message.objects.all())
    return render(request, 'pages/admin.html', {"user": current_user, "users": users,"messages": messages})

# @login_required
# @user_passes_test(admin_check)
def view_messages(request):
    if request.method == "POST":
        sender = request.POST.get('sender')
        if sender == 'all':
            messages = list(Message.objects.all())
        else:
            messages = list(Message.objects.filter(sender=sender))
        return admin(request, messages)

# @login_required
# @user_passes_test(admin_check)
def delete_messages(request):
    if request.method == "POST":
        selected_message_ids = request.POST.getlist('message_id')
        for message_id in selected_message_ids:
            Message.objects.filter(id=message_id).delete()

        return redirect('admin')


def create_account(request):
    # Flaw: No restrictions for password => password can be practically anything.
    # Fix: Django pluggable passwordvalidators (see definitions at 'settings.py').
    username = request.POST.get('username').strip()
    if len(User.objects.filter(username=username)) > 0:
        return render(request, 'pages/create.html', {"error_message": f"Username '{username}' is taken."}) 

    password = request.POST.get('password').strip()
    password_again = request.POST.get('password_again').strip()

    if password != password_again:
        return render(request, 'pages/create.html', {"error_message": "Mismatching passwords."})

    # Password validation
    # try:
    #     validate_password(password)
    # except ValidationError as e:
    #             return render(request, 'pages/create.html', {"error_message": e.messages[0]}) 

    User.objects.create_user(username=username, password=password)
    return redirect('index')

# @axes_dispatch
def login_func(request):
    # Flaw: No counter for invalid login attempts => credential stuffing.
    # Fix: Django Axes with username + IP-address combination,
    # otherwise possibility for DoS-attack.

    username = request.POST.get('username').strip()
    password = request.POST.get('password').strip()
    user = authenticate(request=request, username=username, password=password)

    if user:
        login(request, user)
        request.session['user'] = username
        if request.user.is_staff:
            return redirect('admin')

        return redirect('logged')
    
    return render(request, 'pages/index.html', {"error_message": "wrong username or password"})

def logout_func(request):
    logout(request)

    return redirect('index')

# @login_required
def send_message(request):
    # Flaw 1: SQL-injection, XSS
    # Flaw 2: CSRF-attack possibility without hidden csrf-token in the form

    # Using unsanitized data,
    # sending message "hello'); UPDATE auth_user SET is_staff=True WHERE username='alice';--"
    # will change user 'alice' priviledges to admin level,
    # sending message "hello'); DROP TABLE messages;--" 
    # causes application to fall.

    sender = request.user.username

    ##########################################
    try:
        receiver = request.GET.get('receiver')
        messagetext = request.GET.get('messagetext')
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        sql = "INSERT INTO messages (sender, receiver, messagetext) VALUES ('" + sender + "','" + receiver + "','" + messagetext + "')"
        cursor.executescript(sql)
        conn.commit()
        conn.close()
        if request.user.is_staff:
            return redirect('admin')
        return redirect('logged')
    
    except Exception as e:
        print(e)
        return render(request, 'pages/error.html')
        
    ##########################################


    # Fix: Use of POST + CSRF-token instead of GET, Django ORM instead of raw SQL
    # and sanitizing the user input data. To test the fix, replace try-except-block
    # above with commented out if-block below and from templates 'logged.html' and
    # 'admin.html', replace the tag that starts the message sending form containing GET
    #  as a method with commented out tag with POST as a method and a hidden CSRF-token.

    #if request.method == 'POST':
    #   if request.session['user'] == sender:
    #       receiver = request.POST.get('receiver')
    #       messagetext = html.escape(request.GET.get('messagetext'), quote=True)
    #       if receiver == 'all':
    #           all_users = list(User.objects.all())
    #           for user in all_users:
    #               Message.objects.create(messagetext=messagetext, receiver=user, sender=sender)
    #       else:
    #           Message.objects.create(messagetext=messagetext, receiver=receiver, sender=sender)
    #       if request.user.is_staff:
    #           return redirect('admin')
    #       return redirect('logged')
    #return render(request, 'pages/error.html')
