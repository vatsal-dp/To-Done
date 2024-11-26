import datetime
import json
import pytz

from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.utils import timezone

from todo.models import List, ListItem, Template, TemplateItem, ListTags, SharedUsers, SharedList

from todo.forms import NewUserForm
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.mail import BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.db.models import Avg
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage

# Import for notifications
from webpush import send_user_notification


# Render the home page with users' to-do lists
def index(request, list_id=0):
    """Render the home page with users' to-do lists"""
    if not request.user.is_authenticated:
        return redirect("/login")

    shared_list = []

    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user

    if list_id != 0:
        # latest_lists = List.objects.filter(id=list_id, user_id_id=request.user.id)
        latest_lists = List.objects.filter(id=list_id)

    else:
        latest_lists = List.objects.filter(user_id_id=request.user.id).order_by('-updated_on')

        try:
            query_list_str = SharedList.objects.get(user_id=request.user.id).shared_list_id
        except SharedList.DoesNotExist:
            query_list_str = None

        if query_list_str is not None:
            shared_list_id = query_list_str.split(" ")
            shared_list_id.remove("")

            latest_lists = list(latest_lists)

            for list_id in shared_list_id:

                try:
                    query_list = List.objects.get(id=int(list_id))
                except List.DoesNotExist:
                    query_list = None

                if query_list:
                    shared_list.append(query_list)


    latest_list_items = ListItem.objects.order_by('-due_date')
    saved_templates = Template.objects.filter(user_id_id=request.user.id).order_by('created_on')
    list_tags = ListTags.objects.filter(user_id=request.user.id).order_by('created_on')

    # Chat GPT Assisted with some of the fields
    completed_tasks = ListItem.objects.filter(is_done=True, list__user_id=request.user)
    on_time_tasks = completed_tasks.filter(delay=0).count()
    total_completed_tasks = completed_tasks.count()
    avg_delay = completed_tasks.aggregate(Avg('delay'))['delay__avg'] or 0
    avg_completion_time = completed_tasks.aggregate(Avg('completion_time'))['completion_time__avg'] or 0

    # change color when is or over due
    cur_date = datetime.datetime.now().replace(tzinfo=pytz.UTC) + datetime.timedelta(minutes=60)
    for list_item in latest_list_items:
        list_item.color = "#FF0000" if cur_date > list_item.due_date else "#000000"

    context = {
        'latest_lists': latest_lists,
        'latest_list_items': latest_list_items,
        'templates': saved_templates,
        'list_tags': list_tags,
        'shared_list': shared_list,
        'user': user,
        'vapid_key': vapid_key,
        'on_time_rate': (on_time_tasks / total_completed_tasks * 100) if total_completed_tasks > 0 else 0,
        'avg_delay': avg_delay,
        'avg_completion_time': avg_completion_time,
    }
    return render(request, 'todo/index.html', context)

# Create a new to-do list from templates and redirect to the to-do list homepage
def todo_from_template(request):
    """Create a new to-do list from templates and redirect to the to-do list homepage"""
    if not request.user.is_authenticated:
        return redirect("/login")
    template_id = request.POST['template']
    fetched_template = get_object_or_404(Template, pk=template_id)
    todo = List.objects.create(
        title_text=fetched_template.title_text,
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=request.user.id
    )
    for template_item in fetched_template.templateitem_set.all():
        ListItem.objects.create(
            item_name=template_item.item_text,
            item_text="",
            created_on=timezone.now(),
            finished_on=timezone.now(),
            due_date=timezone.now(),
            tag_color=template_item.tag_color,
            list=todo,
            is_done=False,
        )
    return redirect("/todo")


# Create a new Template from existing to-do list and redirect to the templates list page
def template_from_todo(request):
    """Create a new Template from existing to-do list and redirect to the templates list page"""
    if not request.user.is_authenticated:
        return redirect("/login")
    todo_id = request.POST['todo']
    fetched_todo = get_object_or_404(List, pk=todo_id)
    new_template = Template.objects.create(
        title_text=fetched_todo.title_text,
        created_on=timezone.now(),
        updated_on=timezone.now(),
        user_id_id=request.user.id
    )
    for todo_item in fetched_todo.listitem_set.all():
        TemplateItem.objects.create(
            item_text=todo_item.item_name,
            created_on=timezone.now(),
            finished_on=timezone.now(),
            due_date=timezone.now(),
            tag_color = todo_item.tag_color,
            template=new_template
        )
    return redirect("/templates")


# Delete a to-do list
def delete_todo(request):
    """Delete a to-do list"""
    if not request.user.is_authenticated:
        return redirect("/login")
    todo_id = request.POST['todo']
    fetched_todo = get_object_or_404(List, pk=todo_id)
    fetched_todo.delete()
    return redirect("/todo")


# Render the template list page
def template(request, template_id=0):
    """Render the template list page"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if template_id != 0:
        saved_templates = Template.objects.filter(id=template_id)
    else:
        saved_templates = Template.objects.filter(user_id_id=request.user.id).order_by('created_on')
    context = {
        'templates': saved_templates
    }
    return render(request, 'todo/template.html', context)


# Remove a to-do list item, called by javascript function
@csrf_exempt
def removeListItem(request):
    """Remove a to-do list item, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_item_id = body['list_item_id']
        #print("list_item_id: ", list_item_id)
        try:
            with transaction.atomic():
                being_removed_item = ListItem.objects.get(id=list_item_id)
                being_removed_item.delete()
        except IntegrityError as e:
            print(str(e))
            print("unknown error occurs when trying to update todo list item text")
        return redirect("/todo")
    return redirect("/todo")

# Update a to-do list item, called by javascript function
@csrf_exempt
def updateListItem(request, item_id):
    """Update a to-do list item, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        updated_text = request.POST['note']
        # print(request.POST)
        #print(updated_text)
        #print(item_id)
        if item_id <= 0:
            return redirect("index")
        try:
            with transaction.atomic():
                todo_list_item = ListItem.objects.get(id=item_id)
                todo_list_item.item_text = updated_text
                todo_list_item.save(force_update=True)
        except IntegrityError as e:
            print(str(e))
            print("unknown error occurs when trying to update todo list item text")
        return redirect("/")
    return redirect("index")


# Add a new to-do list item, called by javascript function
@csrf_exempt
def addNewListItem(request):
    """Add a new to-do list item, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        item_name = body['list_item_name']
        create_on = body['create_on']
        eastern = pytz.timezone('US/Eastern')
        create_on_time = datetime.datetime.fromtimestamp(create_on).replace(tzinfo=eastern)
        finished_on_time = datetime.datetime.fromtimestamp(create_on).replace(tzinfo=eastern)
        due_date = body['due_date']
        tag_color = body['tag_color']
        priority = body.get('priority', 2)
        due_date_on_time = datetime.datetime.fromtimestamp(due_date).replace(tzinfo=eastern)
        # print(item_name)
        # print(create_on)
        #print(due_date)
        result_item_id = -1
        # create a new to-do list object and save it to the database
        try:
            with transaction.atomic():
                todo_list_item = ListItem(item_name=item_name, created_on=create_on_time,
                                           finished_on=finished_on_time, due_date=due_date_on_time,
                                             tag_color=tag_color, list_id=list_id, item_text="",
                                               priority = priority, is_done=False)
                todo_list_item.save()
                result_item_id = todo_list_item.id
        except IntegrityError:
            print("unknown error occurs when trying to create and save a new todo list")
            return JsonResponse({'item_id': -1})
        return JsonResponse({'item_id': result_item_id})  # Sending an success response
    else:
        return JsonResponse({'item_id': -1})


# Mark a to-do list item as done/not done, called by javascript function
@csrf_exempt
def markListItem(request):
    """Mark a to-do list item as done/not done, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        list_item_id = body['list_item_id']
        # remove the first " and last "
        list_item_is_done = True
        is_done_str = str(body['is_done'])
        finish_on = body['finish_on']
        finished_on_time = timezone.now()
        #print("is_done: " + str(body['is_done']))
        if is_done_str == "0" or is_done_str == "False" or is_done_str == "false":
            list_item_is_done = False
        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(id=list_item_id)
                query_item.is_done = list_item_is_done
                query_item.finished_on = finished_on_time

                if query_item.is_done:
                    query_item.calculate_delay()
                    query_item.calculate_completion_time()
                query_item.save()
                # Sending an success response
                return JsonResponse({'item_name': query_item.item_name,
                                      'list_name': query_list.title_text,
                                        'item_text': query_item.item_text})
        except IntegrityError:
            print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
        return HttpResponse("Success!")  # Sending an success response
    else:
        return HttpResponse("Request method is not a Post")

# Get all the list tags by user id
@csrf_exempt
def getListTagsByUserid(request):
    """Get all the list tags by user id"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_id = request.user.id
                list_tag_list = ListTags.objects.filter(user_id=user_id).values()
                return JsonResponse({'list_tag_list': list(list_tag_list)})
        except IntegrityError:
            print("query list tag by user_id = " + str(user_id) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response

# Get a to-do list item by name, called by javascript function
@csrf_exempt
def getListItemByName(request):
    """Get a to-do list item by name, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        # remove the first " and last "
        # list_item_name = list_item_name

        #print("list_id: " + list_id)
        #print("list_item_name: " + list_item_name)
        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(list_id=list_id, item_name=list_item_name)
                # Sending an success response
                return JsonResponse({'item_id': query_item.id,
                                      'item_name': query_item.item_name,
                                        'list_name': query_list.title_text,
                                          'item_text': query_item.item_text})
        except IntegrityError:
            print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response


# Get a to-do list item by id, called by javascript function
@csrf_exempt
def getListItemById(request):
    """Get a to-do list item by id, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_id = body['list_id']
        list_item_name = body['list_item_name']
        list_item_id = body['list_item_id']

        #print("list_id: " + list_id)
        #print("list_item_name: " + list_item_name)
        #print("list_item_id: " + list_item_id)

        try:
            with transaction.atomic():
                query_list = List.objects.get(id=list_id)
                query_item = ListItem.objects.get(id=list_item_id)
                #print("item_text", query_item.item_text)
                # Sending an success response
                return JsonResponse({'item_id': query_item.id,
                                      'item_name': query_item.item_name,
                                        'list_name': query_list.title_text,
                                          'item_text': query_item.item_text})
        except IntegrityError:
            #print("query list item" + str(list_item_name) + " failed!")
            JsonResponse({})
    else:
        return JsonResponse({'result': 'get'})  # Sending an success response


# Create a new to-do list, called by javascript function
@csrf_exempt
def createNewTodoList(request):
    """Create a new to-do list, called by javascript function"""

    if not request.user.is_authenticated:
        return redirect("/login")

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        list_name = body['list_name']
        create_on = body['create_on']
        tag_name = body['list_tag']
        shared_user = body['shared_user']
        user_not_found = []
        #print(shared_user)
        create_on_time = timezone.make_aware(datetime.datetime.fromtimestamp(create_on))
        # print(list_name)
        # print(create_on)
        # create a new to-do list object and save it to the database
        try:
            with transaction.atomic():
                user_id = request.user.id
                # print(user_id)
                todo_list = List(user_id_id=user_id,
                                  title_text=list_name,
                                    created_on=create_on_time,
                                      updated_on=create_on_time,
                                        list_tag=tag_name)
                if body['create_new_tag']:
                    # print('new tag')
                    new_tag = ListTags(user_id_id=user_id,
                                        tag_name=tag_name,
                                          created_on=create_on_time)
                    new_tag.save()

                todo_list.save()
                #print(todo_list.id)

                # Progress
                if body['shared_user']:
                    user_list = shared_user.split(' ')

                    k = len(user_list)-1
                    i = 0
                    while i <= k:

                        try:
                            query_user = User.objects.get(username=user_list[i])
                        except User.DoesNotExist:
                            query_user = None

                        if query_user:

                            shared_list_id = SharedList.objects.get(user=query_user).shared_list_id
                            shared_list_id = shared_list_id + str(todo_list.id) + " "
                            SharedList.objects.filter(user=query_user).update(shared_list_id=shared_list_id)
                            i += 1

                        else:
                            #print("No user named " + user_list[i] + " found!")
                            user_not_found.append(user_list[i])
                            user_list.remove(user_list[i])
                            k -= 1

                    shared_user = ' '.join(user_list)
                    new_shared_user = SharedUsers(list_id=todo_list, shared_user=shared_user)
                    new_shared_user.save()

                    #print(user_not_found)

                    if user_list:
                        List.objects.filter(id=todo_list.id).update(is_shared=True)

        except IntegrityError as e:
            print(str(e))
            print("unknown error occurs when trying to create and save a new todo list")
            return HttpResponse("Request failed when operating on database")
        # return HttpResponse("Success!")  # Sending an success response
        # context = {
        #     'user_not_found': user_not_found,
        # }
        return HttpResponse("Success!")
        # return redirect("index")
    else:
        return HttpResponse("Request method is not a Post")

# Send a push notification to a user
@require_POST
@csrf_exempt
def send_push(request):
    """Send a push notification to a user"""
    try:
        body = request.body
        data = json.loads(body)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})

# Send a push notification to a user
@require_POST
@csrf_exempt
def checkForNotifications(request):
    """Send a push notification to a user"""
    try:
        body = request.body
        data = json.loads(body)

        if 'timestamp' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        timestamp = data['timestamp']
        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)

        allItems = []

        # shared_list = SharedList.objects.filter(user=User.objects.get(request.user.id))
        eastern = pytz.timezone('US/Eastern')
        latest_lists = List.objects.filter(user_id=request.user.id).order_by('-updated_on')
        # cur_date = datetime.datetime.now(eastern).replace(tzinfo=pytz.UTC)
        cur_date = datetime.datetime.now().replace(tzinfo=pytz.UTC, second=0, microsecond=0) + datetime.timedelta(hours=1)

        for list in latest_lists:
            # print(list)
            allItems = ListItem.objects.filter(list=list).order_by('list_id')
            for item in allItems:
                # realDueDate = item.due_date
                realDueDate = item.due_date - datetime.timedelta(hours=5)
                # realDueDate_epoch = calendar.timegm(time.strptime(realDueDate, '%Y-%m-%d %H:%M:%S'))
                #(cur_date, " - ", realDueDate, ": ", realDueDate - cur_date, " ?= ", datetime.timedelta(minutes=30))
                if  realDueDate - cur_date == datetime.timedelta(minutes=30):
                    message = "{} will be due in 30 minutes".format(item.item_name)
                    payload = {'head': item.item_name, 'body': message}
                    send_user_notification(user=user, payload=payload, ttl=1000)
                    #print("TRUE")

        # for list_item in latest_list_items:
        #     print(list_item.due_date)

        # print (latest_list_items)
        # print(shared_list)
        # shared_list = SharedList(user=User.objects.get(request.user), shared_list_id="")
        # print(shared_list)

        # user = get_object_or_404(User, pk=user_id)
        # payload = {'head': data['head'], 'body': data['body']}
        # send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .models import SharedList
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Check user credentials
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # If user is authenticated, log them in
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("todo:index")  # Redirect to the appropriate page
            else:
                # If authentication fails, show custom error message
                messages.error(request, "Invalid username or password.")
        else:
            # If the form is invalid (e.g., empty fields), show custom error message
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "todo/login.html", {"login_form": form})


class NewUserForm(forms.ModelForm):
    """Form for user registration with custom validation."""
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Invalid email format.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password)  # Use Django's built-in validators
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data


from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def register_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        errors = {}

        # Check if username exists
        if User.objects.filter(username=username).exists():
            errors['username_exists'] = "Username already exists. Please try a different one."

        # Check if email exists
        if User.objects.filter(email=email).exists():
            errors['email_exists'] = "Email already exists. Please try a different one."

        # Check if passwords match
        if password1 != password2:
            errors['password_mismatch'] = "Passwords do not match. Please re-enter your passwords."

        # Validate password format
        if len(password1) < 8 or not any(char.isupper() for char in password1) or not any(char.islower() for char in password1) or not any(char.isdigit() for char in password1) or not any(char in '@$!%*?&' for char in password1):
            errors['password_invalid'] = "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character."

        if errors:
            return render(request, 'todo/register.html', {'errors': errors, 'username': username, 'email': email})

        # If no errors, create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "User successfully registered!")
        
        # Redirect to the login page with a success flag
        return render(request, 'todo/register.html', {'success': True})

    return render(request, 'todo/register.html')

# Logout a user
def logout_request(request):
    """Logout a user"""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("todo:index")


# Reset user password
def password_reset_request(request):
    """Reset user password"""
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "todo/password/password_reset_email.txt"
                    c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_email = EmailMessage(subject, email, settings.EMAIL_HOST_USER, [user.email])
                        send_email.fail_silently = False
                        send_email.send()
                    except BadHeaderError:
                        return HttpResponse('Invalid header found')
                    return redirect("/password_reset/done/")
            else:
                messages.error(request, "Not an Email from existing users!")
        else:
            messages.error(request, "Not an Email from existing users!")

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="todo/password/password_reset.html", context={"password_reset_form":password_reset_form})
