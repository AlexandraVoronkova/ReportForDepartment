from django.db import models


class FilterField(models.Model):
    name = models.CharField(max_length=200)
    data_name = models.CharField(max_length=200)
    model_name = models.CharField(max_length=50, null=True, blank=True)
    is_history = models.BooleanField(default=False)


class Report(models.Model):
    name = models.CharField(max_length=200)


class ReportField(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    filter_field = models.ForeignKey(FilterField, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
