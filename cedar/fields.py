import django.db.models


class StrippedCharField(django.db.models.CharField):
    '''
    StrippedCharField will remove leading/trailing spaces and carriage returns (I think) before
    saving to the db. Used on several "Name" fields where user could mistakenly enter spaces.
    '''

    def pre_save(self, model_instance, add):
        val = super(StrippedCharField, self).pre_save(model_instance, add)
        if val is not None:
            return val.strip()
