from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.conf import settings
from djangotailoring.views import TailoredDocView
from djangotailoring.project import getsubjectloader
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
        return HttpResponseRedirect(reverse('mycoach:default')) 

    import os, time
    cmd_str = "source " + settings.DIR_MYDATA + "authors_checkout.sh"
    os.system(cmd_str) 
    with open(settings.DIR_PROJ + 'reboot_flag.txt', 'w') as f:
        read_data = f.write('reboot')
    return HttpResponse(time.localtime().tm_sec)

def review_view(request):
    return render(request, 'mypublisher/run_checkout.html', {
        "main_nav": main_nav(request.user, 'staff_view'),
        "tasks_nav": tasks_nav(request.user, 'publisher'),
        "steps_nav": steps_nav(request.user, 'run_checkout')
    })

def checkback_view(request):
    return HttpResponse('reboot done')

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
    students = copycat.get_table().objects.all().order_by('id').values_list('user_id')
    col_str = ', '.join([str(x) for x in headers]) 
    where_str = "user_id='" + "' or user_id='".join([str(x[0]) for x in students]) + "'"
    query = "select " + col_str + " from " + copycat.get_table()._meta.db_table
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

class Message_Viewer_View(TailoredDocView):
    #template_name='mycoach/admin.html'
    template_name='mycoach/message_viewer.html'
    m_subloader = getsubjectloader()
    #m_messages = Messages()
    @property 
    def message_document(self): 
        return self.m_messages.pathto(self.request.GET.get("messages"))

    def dispatch(self, request, *args, **kwargs):
        # psudo constructor
        configure_source_data(request.user.username)
        Log_Request(request)
        # load the nav object
        self.m_nav = StaffNav(request.path)

        return super(Message_Viewer_View, self).dispatch(request, *args, **kwargs)

    #over ride context creation for the template
    def get_context_data(self, **kwargs):
        from django.db.models import Count, Avg # import the aggregators of interest
        context = super(Message_Viewer_View, self).get_context_data(**kwargs)
        context["args"] = self.request.GET

        min_clicks = 10
        active = User.objects.annotate(clicks=Count('elog')).filter(clicks__gt=min_clicks).order_by('username')
        ids = [] 
        for aa in active:
            ids.append(aa.username) 

        message_list = self.m_messages.getlist()

        message_choice = self.request.GET.get("messages")
        if message_choice == None:
            message_choice = message_list[0]

        student_choice = self.request.GET.get("students")
        if student_choice == None:
            student_choice = ids[0]

        context["student_choices"] = ids
        context["message_choices"] = message_list
        context["student_choice"] = student_choice
        context["message_choice"] = message_choice 
        context["user"] = self.request.user
        context["nav"] = self.m_nav       
 
        return context

    def get_subject(self):
        # over ride to get someone else's subject
        try:
            sub = self.m_subloader.get_subject(self.request.GET.get("students"))[0]
        except:
            sub = self.m_subloader.empty_subject()[0]
        return sub

class Copy_Student_View(TemplateView):
    #template_name='mycoach/admin.html'
    template_name='mycoach/copy_student.html'
 
    def dispatch(self, request, *args, **kwargs):
        from django.db.models import Count, Avg # import the aggregators of interest
        # psudo constructor
        #self.m_nav = kwargs["nav"]
        Log_Request(request)
        configure_source_data(request.user.username)
        # load the nav object
        self.m_nav = StaffNav(request.path)

        self.m_copy = request.GET.get("copy_student")

        # attempt to copy the student data
        try:        
            me = Source1.objects.filter(user_id=request.user.username)[0]
            you = Source1.objects.filter(user_id=self.m_copy)[0]
            you.pk = me.pk
            #you.uid = me.uid # this is effectively to ensure the user_id attribute of the table is correct
            you.user_id = me.user_id
            you.save()
        except:
            pass

        min_clicks=1
        #self.m_students = User.objects.annotate(clicks=Count('elog', distinct=True)).filter(clicks__gt=min_clicks).order_by('username').values(
        #self.m_students = User.objects.annotate(clicks=Count('elog', distinct=True)).order_by('username').values(
        self.m_students = User.objects.values(
            'username', 
            'source1__user_id', 
            'source1__First_Survey_Complete', 
            'source1__MP_Name',
            'source1__First_Name',
            'source1__Last_Name',
            'source1__Gender',
            'source1__Course',
            'source1__Cum_GPA_Survey',
            'source1__Semesters_Completed',
            'source1__College',
            'source1__Grade_Want',
            'source1__Confidence').filter(source1__First_Survey_Complete='Yes').annotate(clicks=Count('elog', distinct=True)).order_by('username')

        return super(Copy_Student_View, self).dispatch(request, *args, **kwargs)

    #over ride context creation for the template
    def get_context_data(self, **kwargs):
        context = super(Copy_Student_View, self).get_context_data(**kwargs)
        context["args"] = self.request.GET
        context["user"] = self.request.user
        context["nav"] = self.m_nav
        context["students"] = self.m_students
        context["copy_student"] = self.m_copy
        return context


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


