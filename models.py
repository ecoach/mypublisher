from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.conf import settings
mydata = import_module(settings.MYDATA)
Source1 = mydata.models.Source1
Common1 = mydata.models.Common1

# Create your models here.

class Copycat(models.Model):
    user = models.ForeignKey(User, to_field='username') 
    table = models.CharField(max_length=30, null=True)
    # [12m Download__Download_Column]

    def column_choices(self):
        ids = []
        for ff in eval(self.table)._meta.fields:
            ids.append(ff.name)
        return zip(ids, ids)

class Copycat_Column(models.Model):
    column_name = models.CharField(max_length=100)
    copycat = models.ForeignKey(Copycat)



