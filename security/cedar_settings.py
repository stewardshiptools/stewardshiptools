from cedar_settings.default_settings import default_settings

level_range = range(1, 5)
default_settings['security_level_choices'] = ('text', repr([(x, "Level {}".format(x)) for x in level_range]))
default_settings['security_level_default'] = ('int', min(level_range))
