from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from djangotailoring.views import TailoredDocView
from djangotailoring.project import getsubjectloader
from mytailoring.nav import all_messages_nav
from mynav.nav import main_nav, tasks_nav
from .steps import steps_nav
from .models import *
from .forms import *
# mydataX imports
from django.utils.importlib import import_module
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1
Common1 = mydata.models.Common1

# Create your views here.

def checkout_view(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('mytailoring:default')) 

    import os, time
    cmd_str = "source " + settings.DIR_MYDATA + "authors_checkout.sh"
    os.system(cmd_str) 
    with open(settings.DIR_PROJ + 'reboot_flag.txt', 'w') as f:
        read_data = f.write('reboot')
    return HttpResponse(time.localtime().tm_sec)

@staff_member_required
def run_checkout_view(request):
    return render(request, 'mypublisher/run_checkout.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'publisher'),
        "steps_nav": steps_nav(request.user, 'run_checkout')
    })

@staff_member_required
def checkback_view(request):
    return HttpResponse('reboot done')

@staff_member_required
def copycat_view(request):
    from django.db import connections, router

    copycat = copycat_object(request.user)
    copy_error = 'none'
    if request.method == 'POST':
        form = Copycat_Form(
            column_choices = copycat.column_choices(),
            data=request.POST, 
        )
        if form.is_valid():
            # Do valid form stuff here
            if form.cleaned_data["db_table"] != None and form.cleaned_data["db_table"] != copycat.table:
                copycat.table = request.POST.get("db_table")
                Copycat_Column.objects.all().filter(copycat=copycat).delete()
            elif form.cleaned_data["columns"] != None:
                # only if you didn't just swith tables
                cols = form.cleaned_data["columns"]
                Copycat_Column.objects.all().filter(copycat=copycat).delete()
                for cc in cols:
                    Copycat_Column(copycat=copycat, column_name=cc).save()
            if form.cleaned_data["copy_who"] != 'no-one':
                # attempt to copy the student data
                copied = str(request.POST.get("copy_who"))
                try:
                    # Common
                    me = Common1.objects.filter(user_id=request.user.username)[0]
                    you = Common1.objects.filter(user_id=copied)[0]
                    you.pk = me.pk
                    you.user_id = me.user_id
                    you.save()
                    copy_error = "Common sucess, "
                except:
                    copy_error = "<font color='red'>Common error</font>, "
                try:
                    # Source1
                    me = Source1.objects.filter(user_id=request.user.username)[0]
                    you = Source1.objects.filter(user_id=copied)[0]
                    you.pk = me.pk
                    you.Reg_Enrolled = me.Reg_Enrolled
                    you.user_id = me.user_id
                    you.save()
                    copy_error = copy_error + "Source1 sucess, "
                except:
                    copy_error = copy_error + "<font color='red'>Source1 error</font>, "
                copy_error = copy_error + "user: " + request.POST.get("copy_who")
            copycat.save()
    form = Copycat_Form(
        column_choices = copycat.column_choices(),
        initial={
            'columns' : [ii.column_name for ii in copycat.copycat_column_set.all()],
            'db_table' : copycat.table,
            'copy_who' : 'no-one'
        }
    )
    # make the table 
    headers = ['user_id'] + [str(ii.column_name) for ii in copycat.copycat_column_set.all()] 
    students = Source1.objects.all().order_by('id').values_list('user_id')
    col_str = ', '.join([str(x) for x in headers]) 
    where_str = " where user_id='" + "' or user_id='".join([str(x[0]) for x in students]) + "'"
    query = "select " + col_str + " from " + copycat.get_table()._meta.db_table + where_str
    db = router.db_for_read(copycat.get_table())
    cursor = connections[db].cursor()
    res = cursor.execute(query)
    student_data = cursor.fetchall() 

    return render(request, 'mypublisher/copycat.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'publisher'),
        "steps_nav": steps_nav(request.user, 'copycat'),
        "headers": headers,
        "copy_error": copy_error,
        "students": student_data,
        "active_columns": [str(ii.column_name) for ii in copycat.copycat_column_set.all()],
        "active_table": copycat.table,
        "form": form,
    })

@staff_member_required
def message_review_view(request, *args, **kwargs):

    return render(request, 'mypublisher/message_review.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'publisher'),
        "steps_nav": steps_nav(request.user, 'message_review'),
        "all_messages": all_messages_nav(request.user, kwargs['msg_id'] ),
        "selected_msg": kwargs['msg_id'],
    })

def copycat_object(user):
    profile = user.get_profile()
    prefs = profile.prefs
    # pull the users stuff
    try:
        copycat = Copycat.objects.get(pk=prefs["download_pk"])
    except:  
        copycat = Copycat(user=user)
        copycat.save()
        prefs['download_pk'] = copycat.id
        profile.prefs = prefs
        profile.save()
    return copycat


