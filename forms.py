from django import forms
from django.conf import settings
from .models import *
from datetime import datetime
from django.utils.importlib import import_module
#mydata = import_module(settings.MYDATA)
#Source1 = mydata.models.Source1

class Copycat_Form(forms.Form):
    db_table = forms.ChoiceField(required=False)
    columns = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    copy_who = forms.CharField(required=False, max_length=10, widget=forms.HiddenInput())

    def __init__(self, column_choices, *args, **kwargs):
        super(Copycat_Form, self).__init__(*args, **kwargs)
        self.fields['db_table'].choices = self.table_choices()
        self.fields['columns'].choices = column_choices

    def table_choices(self):
        available = [
            ('Source1', 'Source1'),
            ('Common1', 'Common1')
        ]
        return available


