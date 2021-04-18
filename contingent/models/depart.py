from django.db import models


class Department(models.Model):
    name = models.CharField(u'Подразделение', max_length=200, null=True, blank=True)
    smallname = models.CharField(u'Сокр. наименование', max_length=200, null=True, blank=True)
    dep = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)
