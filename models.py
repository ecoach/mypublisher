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

    def get_table(self):
        #if len(self.table) < 2:
        #if self.table is not None: 
        if not isinstance(self.table, unicode): 
            return Source1 
        else:
            return eval(self.table)

    def column_choices(self):
        ids = []
        for ff in self.get_table()._meta.fields:
            ids.append(ff.name)
        return zip(ids, ids)


class Copycat_Column(models.Model):
    column_name = models.CharField(max_length=100)
    copycat = models.ForeignKey(Copycat)



