import sqlite3
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Message
from django.views.decorators.cache import cache_control
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from axes.decorators import axes_dispatch


@cache_control(no_cache=True, no_store=True)
def index(request):
    return render(request, 'pages/index.html')

def create(request):
    return render(request, 'pages/create.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def logged(request):
    # Flaw: no automatic logout after specified idle time
    # Fix: Session cookie age in settings.py

    current_user = request.user
    users = ['all'] + list(User.objects.exclude(username=current_user))
    messages = list(Message.objects.filter(
        receiver=current_user)) + list(Message.objects.filter(
        receiver='all'))
    for message in messages:
        print(message.id)
    return render(request, 'pages/logged.html', {"user": current_user, "users": users,"messages": messages})

    #try:
    #    conn = sqlite3.connect('db.sqlite3')
    #    cursor = conn.cursor()
    #    sql = "SELECT sender, messagetext FROM messages WHERE receiver=? OR receiver='all'"
    #    messages = cursor.execute(sql, (current_user.username,)).fetchall()
    #    conn.commit()
    #    conn.close()
    #    return render(request, 'pages/logged.html', {"user": current_user, "users": users,"messages": messages})
    
    #except Exception as e:
    #    print(e)
    #    return render(request, 'pages/error.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def admin(request, messages = None):
    # Flaw: no automatic logout after specified idle time
    # Fix: Session cookie age in settings.py

    current_user = request.user
    users = ['all'] + list(User.objects.exclude(username=current_user))
    if not messages:
        messages = list(Message.objects.filter(
            receiver=current_user)) + list(Message.objects.filter(
            receiver='all'))
    #for message in messages:
    #    print(message.messagetext)
    return render(request, 'pages/admin.html', {"user": current_user, "users": users,"messages": messages})

@login_required
def view_messages(request):
    if request.method == "POST":
        sender = request.POST.get('sender')
        if sender == 'all':
            messages = list(Message.objects.all())
        else:
            messages = list(Message.objects.filter(sender=sender))
        return admin(request, messages)

@login_required
def delete_messages(request):
    if request.method == "POST":
        selected_message_ids = request.POST.getlist('message_id')  # Get the list of selected message IDs

        # Process the selected message IDs as needed
        for message_id in selected_message_ids:
            Message.objects.filter(id=message_id).delete()
            # Delete the messages with the given IDs or perform other actions
            # Example: Message.objects.filter(id=message_id).delete()

        # Redirect or render a response as appropriate
        return redirect('admin')


def create_account(request):
    username = request.POST.get('username').strip()
    if len(User.objects.filter(username=username)) > 0:
        return render(request, 'pages/create.html', {"error_message": f"Username '{username}' is taken."}) 

    password = request.POST.get('password').strip()
    password_again = request.POST.get('password_again').strip()

    if password != password_again:
        return render(request, 'pages/create.html', {"error_message": "Mismatching passwords."})

    # Password validation (django default)
    try:
        validate_password(password)
    except ValidationError as e:
                return render(request, 'pages/create.html', {"error_message": e.messages[0]}) 

    User.objects.create_user(username=username, password=password)
    return redirect('index')

@axes_dispatch
def login_func(request):
    # Flaw: No counter for invalid login attempts => credential stuffing
    # Fix: Django-axes with username + IP-address combination,
    # otherwise possibility for DoS-attack

    username = request.POST.get('username').strip()
    password = request.POST.get('password').strip()

    user = authenticate(request=request, username=username, password=password)

    if user:
        login(request, user)
        # session['user'] = user
        if request.user.is_staff:
            return redirect('admin')

        return redirect('logged')
    
    return render(request, 'pages/index.html', {"error_message": "wrong username or password"})

def logout_func(request):
    logout(request)

    return redirect('index')

@login_required
def send_message(request):
    # Flaw: SQL-injection, XXS(?)
    # CSRF-attack possibility if using GET instead of POST + csrf-token

    # Using unsanitized data,
    # sending message "hello'); DROP TABLE messages;--" (what about "hello'); UPDATE auth_user SET is_staff=True WHERE username='nana1';--") <-- works!
    # causes application to fall

    # if session['user'] == sender:
    try:
        messagetext = request.GET.get('messagetext')
        receiver = request.GET.get('receiver')
        sender = request.user.username
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


    # Fix: Use of POST and Django ORM instead of raw SQL

    #if request.method == 'POST':
    #    messagetext = request.POST.get('messagetext')
    #    receiver = request.POST.get('receiver')
    #    sender = request.user

    #    if receiver == 'all':
    #        all_users = list(User.objects.all())
    #        for user in all_users:
    #            Message.objects.create(messagetext=messagetext, receiver=user, sender=sender)        
    #    else:
    #        Message.objects.create(messagetext=messagetext, receiver=receiver, sender=sender)
    #    if request.user.is_staff:
    #        return redirect('admin')
    #    return redirect('logged')

    #else:
    #    return render(request, 'pages/error.html')
