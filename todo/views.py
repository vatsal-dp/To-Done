import datetime
import json
import pytz

from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.utils import timezone

from django.core.mail import send_mail

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

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from http.server import HTTPServer, BaseHTTPRequestHandler


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def cal_service():
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        #   "/home/devyash/Downloads/NCSU/SE/last project/To-Done/todo/cred.json", SCOPES
          "/Users/vatsaldp/Desktop/To-Done/todo/cred.json", SCOPES
      )
      creds = flow.run_local_server(port=8002)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    return build("calendar", "v3", credentials=creds)

  except HttpError as error:
    print(f"An error occurred: {error}")

# Render the home page with users' to-do lists
def index(request, list_id=0):
    """Render the home page with users' to-do lists"""
    if not request.user.is_authenticated:
        return redirect("/login")



    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    user = request.user

    if list_id != 0:
        # latest_lists = List.objects.filter(id=list_id, user_id_id=request.user.id)
        latest_lists = List.objects.filter(id=list_id)

    else:
        latest_lists = List.objects.filter(user_id_id=request.user.id).order_by('-updated_on')

        


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

# # Add a new to-do list item, called by javascript function
# @csrf_exempt
# def addNewListItem(request):
#     """Add a new to-do list item, called by javascript function"""
#     if not request.user.is_authenticated:
#         return redirect("/login")
#     if request.method == 'POST':
#         body_unicode = request.body.decode('utf-8')
#         body = json.loads(body_unicode)
#         list_id = body['list_id']
#         item_name = body['list_item_name']
#         create_on = body['create_on']
#         eastern = pytz.timezone('US/Eastern')
#         create_on_time = datetime.datetime.fromtimestamp(create_on).replace(tzinfo=eastern)
#         finished_on_time = datetime.datetime.fromtimestamp(create_on).replace(tzinfo=eastern)
#         due_date = body['due_date']
#         tag_color = body['tag_color']
#         priority = body.get('priority', 2)
#         due_date_on_time = datetime.datetime.fromtimestamp(due_date).replace(tzinfo=eastern)
#         # print(item_name)
#         # print(create_on)
#         #print(due_date)
#         result_item_id = -1
#         # create a new to-do list object and save it to the database
#         try:
#             with transaction.atomic():
#                 todo_list_item = ListItem(item_name=item_name, created_on=create_on_time,
#                                            finished_on=finished_on_time, due_date=due_date_on_time,
#                                              tag_color=tag_color, list_id=list_id, item_text="",
#                                                priority = priority, is_done=False)
#                 todo_list_item.save()
#                 result_item_id = todo_list_item.id
#         except IntegrityError:
#             print("unknown error occurs when trying to create and save a new todo list")
#             return JsonResponse({'item_id': -1})
#         return JsonResponse({'item_id': result_item_id})  # Sending an success response
#     else:
#         return JsonResponse({'item_id': -1})

@csrf_exempt
def addNewListItem(request):
    """Add a new to-do list item, called by javascript function"""
    if not request.user.is_authenticated:
        return redirect("/login")
    
    if request.method == 'POST':
        try:
            # Parse request body
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            
            list_id = body['list_id']
            item_name = body['list_item_name']
            create_on = body['create_on']
            due_date = body['due_date']
            tag_color = body['tag_color']
            priority = body.get('priority', 2)

            # Convert timestamps to aware datetime objects
            # Use fromtimestamp with timezone.utc first, then convert to Eastern
            eastern = pytz.timezone('US/Eastern')
            
            create_on_time = (
                datetime.datetime.fromtimestamp(create_on, tz=pytz.UTC)
                .astimezone(eastern)
            )
            
            finished_on_time = (
                datetime.datetime.fromtimestamp(create_on, tz=pytz.UTC)
                .astimezone(eastern)
            )
            
            due_date_on_time = (
                datetime.datetime.fromtimestamp(due_date, tz=pytz.UTC)
                .astimezone(eastern)
            )

            cot_cal = create_on_time - datetime.timedelta(hours=5)
            ddot_cal = due_date_on_time - datetime.timedelta(hours=5)


            event = {
                'summary': item_name,
                # 'location': '800 Howard St., San Francisco, CA 94103',
                # 'description': 'A chance to hear more about Google\'s developer products.',
                'start': {
                    'dateTime': cot_cal.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': ddot_cal.isoformat(),
                    'timeZone': 'America/New_York',
                },
                # 'recurrence': [
                #     'RRULE:FREQ=DAILY;COUNT=2'
                # ],
                # 'attendees': [
                #     {'email': 'lpage@example.com'},
                #     {'email': 'sbrin@example.com'},
                # ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                    ],
                },
                }
            

            # Create and save the new todo list item
            with transaction.atomic():
                todo_list_item = ListItem(
                    item_name=item_name,
                    created_on=create_on_time,
                    finished_on=finished_on_time,
                    due_date=due_date_on_time,
                    tag_color=tag_color,
                    list_id=list_id,
                    item_text="",
                    priority=priority,
                    is_done=False
                )
                todo_list_item.save()
                result_item_id = todo_list_item.id
                
            service = cal_service()
            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

            return JsonResponse({'item_id': result_item_id})

        except json.JSONDecodeError:
            print("Error decoding JSON data")
            return JsonResponse({'item_id': -1})
        except IntegrityError:
            print("Database integrity error when creating new todo list")
            return JsonResponse({'item_id': -1})
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({'item_id': -1})
            
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
# @require_POST
# @csrf_exempt
# def checkForNotifications(request):
#     """Send a push notification to a user"""
#     try:
#         body = request.body
#         data = json.loads(body)

#         if 'timestamp' not in data or 'id' not in data:
#             return JsonResponse(status=400, data={"message": "Invalid data format"})

#         timestamp = data['timestamp']
#         user_id = data['id']
#         user = get_object_or_404(User, pk=user_id)

#         allItems = []

#         # shared_list = SharedList.objects.filter(user=User.objects.get(request.user.id))
#         eastern = pytz.timezone('US/Eastern')
#         latest_lists = List.objects.filter(user_id=request.user.id).order_by('-updated_on')
#         # cur_date = datetime.datetime.now(eastern).replace(tzinfo=pytz.UTC)
#         cur_date = datetime.datetime.now().replace(tzinfo=pytz.UTC, second=0, microsecond=0) + datetime.timedelta(hours=1)

#         for list in latest_lists:
#             # print(list)
#             allItems = ListItem.objects.filter(list=list).order_by('list_id')
#             for item in allItems:
#                 # realDueDate = item.due_date
#                 realDueDate = item.due_date - datetime.timedelta(hours=5)
#                 # realDueDate_epoch = calendar.timegm(time.strptime(realDueDate, '%Y-%m-%d %H:%M:%S'))
#                 #(cur_date, " - ", realDueDate, ": ", realDueDate - cur_date, " ?= ", datetime.timedelta(minutes=30))
#                 if  realDueDate - cur_date == datetime.timedelta(minutes=30):
#                     message = "{} will be due in 30 minutes".format(item.item_name)
#                     payload = {'head': item.item_name, 'body': message}
#                     send_user_notification(user=user, payload=payload, ttl=1000)
#                     #print("TRUE")

#         # for list_item in latest_list_items:
#         #     print(list_item.due_date)

#         # print (latest_list_items)
#         # print(shared_list)
#         # shared_list = SharedList(user=User.objects.get(request.user), shared_list_id="")
#         # print(shared_list)

#         # user = get_object_or_404(User, pk=user_id)
#         # payload = {'head': data['head'], 'body': data['body']}
#         # send_user_notification(user=user, payload=payload, ttl=1000)

#         return JsonResponse(status=200, data={"message": "Web push successful"})
#     except TypeError:
#         return JsonResponse(status=500, data={"message": "An error occurred"})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json
import pytz
import datetime

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
        # print("user email id: ",user.email)
        allItems = []

        # shared_list = SharedList.objects.filter(user=User.objects.get(request.user.id))
        eastern = pytz.timezone('US/Eastern')
        latest_lists = List.objects.filter(user_id=request.user.id).order_by('-updated_on')
        # cur_date = datetime.datetime.now(eastern).replace(tzinfo=pytz.UTC)
        cur_date = datetime.datetime.now().replace(tzinfo=pytz.UTC, second=0, microsecond=0)
        print("current date variable = ",cur_date)
        for list in latest_lists:
            # print(list)
            allItems = ListItem.objects.filter(list=list).order_by('list_id')
            for item in allItems:
                # realDueDate = item.due_date
                realDueDate = item.due_date - datetime.timedelta(hours=5)
                print("real due date var = ",realDueDate)
                # realDueDate_epoch = calendar.timegm(time.strptime(realDueDate, '%Y-%m-%d %H:%M:%S'))
                #(cur_date, " - ", realDueDate, ": ", realDueDate - cur_date, " ?= ", datetime.timedelta(minutes=30))
                print("difference = ",realDueDate-cur_date)
                print("delta = ",datetime.timedelta(minutes=30))
                if  realDueDate - cur_date == datetime.timedelta(minutes=30):
                    print("inside if condition!")
                    message = "{} will be due in 30 minutes".format(item.item_name)
                    payload = {'head': item.item_name, 'body': message}
                    send_user_notification(user=user, payload=payload, ttl=1000)
                    #print("TRUE")
                    send_mail(
                        subject="Reminder: {} due in 30 minutes".format(item.item_name),
                        message=message,
                        # from_email=settings.DEFAULT_FROM_EMAIL,
                        # recipient_list=[user.email],
                        from_email="clemsonbetter@gmail.com",
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print("mail sent!")

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

# Register a new user account
def register_request(request):
    """Register a new user account"""
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            #print(user)

            # Add a empty list to SharedList table
           

            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("todo:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="todo/register.html",
                  context={"register_form":form})


# Login a user
def login_request(request):
    if request.method == "POST":
        """Login a user"""
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("todo:index")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="todo/login.html", context={"login_form":form})


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
