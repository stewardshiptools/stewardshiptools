"""
Module for processing shared engagement record data

Fields preceded "-->" have been skipped for now.

SER Field Reference (also see development.forms.py):
    govt_rep_name_first = forms.CharField(required=True)
    govt_rep_name_last = forms.CharField(required=True)
    govt_rep_position = forms.CharField(required=False)
    govt_rep_email = forms.EmailField(required=True)
    govt_rep_phone_number = PhoneNumberField(required=True)
    govt_rep_mailing_address = forms.CharField(widget=forms.Textarea, required=True)
    proposal_short_summary = forms.CharField(widget=forms.Textarea, required=True)
    applicant_company_name = forms.CharField(required=True)
    applicant_rep_first_name = forms.CharField(required=True)
    applicant_rep_last_name = forms.CharField(required=True)
    applicant_rep_email = forms.EmailField(required=True)
    applicant_rep_phone_number = PhoneNumberField(required=False)
    applicant_rep_mailing_address = forms.CharField(widget=forms.Textarea, required=True)
    bc_filing_code_n = forms.CharField(required=False)
    applicant_filing_code_n = forms.CharField(required=False)
    location_general_desc = forms.CharField(widget=forms.Textarea, required=False)
    location_n_legal_desc = forms.CharField(widget=forms.Textarea, required=False)
    location_n_geomark = forms.URLField(required = False)
    location_n_geomark_comment = forms.CharField(required=False)
    location_n_size = forms.CharField(required=False)
    primary_authorization_type = forms.ChoiceField(required=False)
    authorization_n_name = forms.CharField(required=False)
    authorization_n_description = forms.CharField(widget=forms.Textarea, required=False)
    engagement_lvl_bc_proposed = forms.CharField(required=False)
    engagement_lvl_bc_rationale = forms.CharField(widget=forms.Textarea, required=False)
    bc_info_sharing = forms.CharField(required=False)
    bc_initial_recommendations = forms.CharField(widget=forms.Textarea, required=False)

"""
from datetime import datetime
from django.utils import timezone
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

import crm.models
import development.models


def get_kwargs_govt_rep(data):
    """
    Ignores 'govt_rep_position'.
    Update: added "position" for govt_rep_position
    :param data: ser data dict
    :return: kwargs for govt_rep crm.Person
    """
    kwargs = {
        'name_first': data.get('govt_rep_name_first', None),
        'name_last': data.get('govt_rep_name_last', None),
        'position': data.get('govt_rep_position', None),
        'email': data.get('govt_rep_email', None),
        'phone': data.get('govt_rep_phone_number', None),
        'address': data.get('govt_rep_mailing_address', None)
    }
    return pop_kwarg_nones(kwargs)


def get_kwargs_app_rep(data):
    """
    :param data: ser data dict
    :return: kwargs for applicant_rep crm.Person
    """
    kwargs = {
        'name_first': data.get('applicant_rep_first_name', None),
        'name_last': data.get('applicant_rep_last_name', None),
        'email': data.get('applicant_rep_email', None),
        'phone': data.get('applicant_rep_phone_number', None),
        'address': data.get('applicant_rep_mailing_address', None),
        'company': data.get('applicant_company_name', None)
    }
    return pop_kwarg_nones(kwargs)


def get_kwargs_bc_file_code(data):
    """
    :param data: ser data dict
    :return: kwargs for bc filing code development.FileNo
    """

    file_number = data.get('bc_filing_code_n', None)

    # quick check to make sure a file no was actually submitted:
    if file_number is None:
        return None
    else:
        kwargs = []
        for f_num in str(file_number).split(','):
            kwargs.append(
                pop_kwarg_nones(
                    {
                        'file_number': f_num.strip(),
                        # 'project': data.get('project', None),
                        'org_type': 'government',
                        'organization': None
                    }
                )
            )
    return kwargs


def get_kwargs_app_file_codes(data):
    """
    :param data: ser data dict
    :return: kwargs for applicant filing code development.FileNo
    """

    file_number = data.get('applicant_filing_code_n', None)

    # quick check to make sure a file no was actually submitted:
    if file_number is None:
        return None
    else:
        kwargs = []

        for f_num in str(file_number).split(','):
            kwargs.append(
                pop_kwarg_nones({
                    'file_number': f_num.strip(),
                    # 'project': data.get('project', None),
                    'org_type': 'proponent',
                    'organization': None
                })
            )

    return kwargs


def get_kwargs_development_project(data):
    """
    :param data: ser data dict
    :return: kwargs for development.DevelopmentProject
    """

    misc_textareas = {
        'el_bc_rationale': data.get('engagement_lvl_bc_rationale', None),
        'info_sharing_bc': data.get('info_sharing_bc', None),
    }

    extra_info = {
        'authorization_name': data.get('authorization_n_name', None),
        'authorization_description': data.get('authorization_n_description', None),
        'el_bc_proposed': data.get('engagement_lvl_bc_proposed', None),
        'initial_recommendations': data.get('bc_initial_recommendations', None),
    }

    due_date = data.get('due_date', None)
    if due_date:
        due_date = timezone.make_aware(
            datetime.strptime(due_date, '%Y-%m-%d'),
            timezone.get_default_timezone()
        )

    # suggest project title and
    # add extra_info data into the description field
    kwargs = {
        'cedar_project_name': data.get('title', None),
        'description': data.get('proposal_short_summary', None),
        'rationale': data.get('project_rationale', None),
        'location_description': data.get('location_general_desc', ' \n\n') + data.get('location_n_legal_desc', ''),
        'primary_authorization': data.get('primary_authorization_type', None),
        'due_date': due_date,
        'misc_textareas': pop_kwarg_nones(misc_textareas),
        'extra_info': pop_kwarg_nones(extra_info)

    }
    return pop_kwarg_nones(kwargs)


def get_kwargs_geomark(data):
    """
    :param data: ser data dict
    :return: kwargs for development.DevelopmentGISLayer.geomark
    """
    kwargs = {
        # 'project': data.get('project', None),
        'layer_type': 'geomark',
        'geomark': data.get('location_n_geomark', None),
        'notes': data.get('location_n_geomark_comment', '\n\n') + data.get('location_n_size', '')
    }
    return pop_kwarg_nones(kwargs)


def pop_kwarg_nones(kwargs):
    """
    Pops off any kwargs that are none.
    Yeah I know this is verbose as hell.
    Also, I used a separate list (pop keys)
    cause it's scary manipulating a list while going over it.
    :param kwargs:
    :return:
    """
    pop_keys = []
    for k in kwargs.keys():
        if kwargs[k] is None:
            pop_keys.append(k)

    for k in pop_keys:
        kwargs.pop(k)

    # if it has any keys left, return them, otherwise return None
    if kwargs.keys():
        return kwargs
    else:
        return None


def get_or_new(model, kwargs):
    """
    A twist on get or create - it doesn't create, only
    returns an instantiated object but doesn't save. If
    "new" is True then the object doesn't already exist and
    could be saved.
    BIG FAT WARNING: This is actually pretty useless at the moment because
    we don't know enough yet about how to handle multiple objects returned.
    So it just returns a NEW instances anyways. da, da, daaaa.
    :param model:
    :param kwargs:
    :return: obj, new (bool)
    """
    try:
        obj = model.objects.get(**kwargs)
        new = False
    except model.DoesNotExist:
        obj = model(**dict((k, v) for (k, v) in kwargs.items() if '__' not in k))
        new = True
    except model.MultipleObjectsReturned:
        obj = model(**dict((k, v) for (k, v) in kwargs.items() if '__' not in k))
        new = True

    return obj, new


def process_ser(data):
    """
    Report on objects that will either be created or linked by the ser data
    Note that for each model in the "result" object there is an instance and
    a set of kwargs. Only the kwargs are used by the SER Form to create objects.
    For now, the instance is ignored.
    :param data: a dict of de-serialized xml ser data.
    :return:
    """
    result = {}

    # create a new (unsaved) dev prj instance and stuff in "data" so it can be passed around
    kw = get_kwargs_development_project(data)
    project = development.models.DevelopmentProject(**kw)
    data.update({'project': project})
    result.update({'project':
        {
            'object': project,
            'kwargs': get_kwargs_development_project(data)
        },
    })

    # govt_rep = government_contact (crm.Person)
    kw = get_kwargs_govt_rep(data)
    result.update({'government_contact':
        {
            # 'object': govt_rep,
            'kwargs': kw
        }
    })

    # applicant_rep = company_contact (crm.Person)
    kw = get_kwargs_app_rep(data)
    result.update({'company_contact':
        {
            'kwargs': kw
        }
    })

    # bc_filing_code_n = (FileNo) FK
    kw = get_kwargs_bc_file_code(data)
    if kw:
        result.update({'bc_filenos': kw})

    # applicant_filing_code_n = (FileNo) FK
    if kw:
        kw = get_kwargs_app_file_codes(data)
        result.update({'app_filenos': kw})

    # geomark
    kw = get_kwargs_geomark(data)
    geomark = development.models.DevelopmentGISLayer(**kw)
    result.update({'geomark':
        {
            'object': geomark,
            'kwargs': kw
        }
    })

    results = add_unmapped_fields_to_description(result)
    return results


def add_unmapped_fields_to_description(result_dict):
    """
    Jumps through some hoops on the other resulting kwargs to build
    DEV PRJ Description text:
        - company contact,
        - govt contact,
        - extra_info,
        - geomark
    :param result_dict: 
    :return: 
    """
    description = result_dict['project']['kwargs'].get('description', '')

    horz_bar = '\n----------------------------------------------------------------\n'

    # using this fields list so we can have some control over the sorting of the text when it's output.
    # perhaps going with a "blah {}" instead of loops this would be better. Hoping this is just a stopgap.
    contact_fields = ['name_first',
                      'name_last',
                      'position',
                      'company',
                      'email',
                      'phone',
                      'address']

    company_contact_text = ''
    for field in contact_fields:
        if field in result_dict['company_contact']['kwargs'].keys():
            company_contact_text += '{}: {}\n'.format(
                field.replace("_", " ").capitalize(),
                result_dict['company_contact']['kwargs'][field]
            )
    if company_contact_text:
        description += horz_bar + 'Company Contact\n' + company_contact_text

    govt_contact_text = ''
    for field in contact_fields:
        if field in result_dict['government_contact']['kwargs'].keys():
            govt_contact_text += '{}: {}\n'.format(
                field.replace("_", " ").capitalize(),
                result_dict['government_contact']['kwargs'][field]
            )
    if govt_contact_text:
        description += horz_bar + 'Government Contact\n' + govt_contact_text

    extra_info = result_dict['project']['kwargs'].get('extra_info', None)
    if extra_info:
        extra_info_text = ''
        for k in extra_info.keys():
            extra_info_text += '{}: {}\n'.format(
                k.replace("_", " ").capitalize(),
                extra_info[k]
            )
        if extra_info_text:
            description += horz_bar + 'Additional Info\n' + extra_info_text

    geomark = result_dict['geomark']['kwargs'].get('geomark', None)
    if geomark:
        geomark_text = horz_bar + 'Geomark\nURL: ' + geomark
        geommark_notes = result_dict['geomark']['kwargs'].get('notes', None)
        if geommark_notes:
            geomark_text += '\nNotes: ' + geommark_notes
        description += geomark_text

    result_dict['project']['kwargs'].update({
        'description': description
    })
    return result_dict


def serialize_ser(ser_dict):
    """
    :param ser_dict:
    :return: ser_xml_string
    """
    return XMLRenderer().render(ser_dict)


def deserialize_ser(ser_xml_string):
    """
    :param ser_xml_string:
    :return: dict
    """
    return XMLParser().parse(ser_xml_string)


