from cedar_settings.default_settings import default_settings

# When MH pull emails this will limit the lookback time to
# now - X hours.
default_settings['communication__mailharvest_lookback_hours'] = ('int', 3)  # integer hours.
default_settings['communication__mailharvest_get_connection_timeout'] = ('float', 15.0)  # float seconds
default_settings['communication__mailharvest_min_inline_img_size_KB'] = ('float', 10.5)  # float KiloBytes.

default_settings['communication__comm_items_panel_html_id'] = ('text', '#tab-communication')  # html id.
default_settings['communication__comm_items_panel_icon_text'] = ('text', 'contact_mail')  # html id.

default_settings['communication__disc_items_panel_html_id'] = ('text', '#tab-discussion')  # html id.
default_settings['communication__disc_items_panel_icon_text'] = ('text', 'forum')  # html id.


MH_TIMEOUT_GET_CONNECTION = 15  # time in seconds