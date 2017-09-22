from cedar_settings.default_settings import default_settings

default_settings['development_project_code_prefix'] = ('text', '#DEV-PRJ-')

default_settings['development_project_primary_auth_choices'] = (
    'text',
    """New|New authorization with new activities and potential impacts
    Replace|Replacement/renewal of authorization with potential impacts
    Change|Change of activity extent/type on existing authorization & potential new impacts
    Extend|Term/timeline of extension of an existing authorization
    Admin|Administrative change (e.g. proponent name)"""
)

default_settings['development_project_misc_textareas'] = (
    'text',
    """info_package_list|Information Package List
    el_bc_rationale|EL - BC Rationale
    el_fn_rationale|EL - FN Rationale
    info_sharing_bc|Info Sharing - BC
    info_sharing_fn|Info Sharing - FN
    engagement_timeline|Engagement Timeline"""
)
