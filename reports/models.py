from django.contrib.gis.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ReportItem(models.Model):
    report_content_type = models.ForeignKey(ContentType)
    report_object_id = models.PositiveIntegerField()
    report_object = GenericForeignKey('report_content_type', 'report_object_id')

    # The following three fields create a generic foreign key.
    report_item_content_type = models.ForeignKey(ContentType)
    report_item_object_id = models.PositiveIntegerField()
    report_item = GenericForeignKey('report_item_content_type', 'report_item_object_id')

    def __str__(self):
        return self.report_item

    class Meta:
        abstract = True


class Report(models.Model):
    """
    """
    report_type_choices = (  # Override this!
        ('this', 'This'),
        ('should', 'should'),
        ('be', 'be'),
        ('overridden', 'overridden!')
    )

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=200, choices=report_type_choices)
    report_on = models.ManyToManyField(ReportItem, related_name='items_reported_on')
    report_against = models.ManyToManyField(ReportItem, related_name='items_reported_against')

    class Meta:
        abstract = True
