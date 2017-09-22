from django.conf import settings

def is_haida(request):
    return {'IS_HAIDA': getattr(settings, 'IS_HAIDA', False)}
