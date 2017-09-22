from cedar_settings.default_settings import default_settings
from django.contrib.staticfiles.templatetags.staticfiles import static


default_settings['cedar__default_support_url'] = ('text', 'http://www.cedarbox.ca/support/')

default_settings['cedar__default_splash_page_background_img'] = ('text', static('css/cedar8_background.jpg'))

default_settings['cedar__default_datepicker_years'] = ('int', 300)
