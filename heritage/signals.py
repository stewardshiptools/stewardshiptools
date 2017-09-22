from django.db.models.signals import post_save

from heritage.models import Interview
from heritage.utils.sanitizer import interview_populate_sensitive_phrases
from cedar_settings.models import GeneralSetting


# Catch the heritage.Interview save signal in order to update
# RelatedSensitivePhrase objects for the saved interview.
def interview_post_save_populate_sensitive_phrases(sender, instance, created, **kwargs):
    if GeneralSetting.objects.get('heritage__interview__auto_populate_sensitive_phrases_on_save'):
        interview_populate_sensitive_phrases(instance)


post_save.connect(interview_post_save_populate_sensitive_phrases, sender=Interview)
