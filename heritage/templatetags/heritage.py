from django import template
from django.utils.safestring import mark_safe
from rest_framework.reverse import reverse_lazy

from assets.models import AssetType

from heritage.models import HeritageAsset, InterviewAsset, SessionAsset, MTKCulturalRecord, MTKSpeciesRecord

register = template.Library()


@register.inclusion_tag('heritage/heritage_map_utils.html')
def heritage_load_map_utils():
    pass


@register.inclusion_tag('heritage/record_session_links.html', takes_context=True)
def heritage_get_record_session_links(context, links):
    return {
        'links': links,
        'perms': context['perms']
    }


@register.assignment_tag()
def heritage_get_session_spatial_transcripts(session):
    return session.sessionasset_set.filter(asset_type__type_of_asset="Transcript Spatial References")


@register.filter()
def heritage_highlight_excerpt(full, excerpt):
    if not excerpt:
        if full:
            return full
        else:
            return ''

    full = full.replace(excerpt, '<span class="highlighted">%s</span>' % excerpt).strip()
    full = full.replace("\n", "<br />")

    return mark_safe("%s" % full)


@register.assignment_tag()
def get_interview_from_heritage_asset(asset_object):
    # This gets a HeritageAsset object... let's get the subclass
    asset_object = HeritageAsset.objects.get_subclass(id=asset_object.id)

    if asset_object.__class__ is InterviewAsset:
        return asset_object.interview
    elif asset_object.__class__ is SessionAsset:
        return asset_object.session.interview
    else:
        return asset_object


@register.assignment_tag()
def get_interview_record_stats(interview):
    record_count = {'total': 0, 'cultural': 0, 'species': 0}
    sessions = interview.session_set.all()

    for session in sessions:
        cultural_record_count = MTKCulturalRecord.objects.filter(published=True, session=session).count()
        species_record_count = MTKSpeciesRecord.objects.filter(published=True, session=session).count()

        record_count['total'] += cultural_record_count + species_record_count
        record_count['cultural'] += cultural_record_count
        record_count['species'] += species_record_count

    return record_count


@register.assignment_tag()
def get_interview_asset_stats(interview):
    asset_count = dict()
    total_assets = 0

    asset_types = AssetType.objects.all()

    # Initiate asset_count dictionaries
    for asset_type in asset_types:
        asset_count[asset_type] = {
            'name': asset_type.type_of_asset,
            'count': 0
        }

    # asset type is not a mandatory field anymore, account for that.
    asset_count[None] = {'name': 'Unspecified', 'count': 0}

    # We only care about interview and session assets, but we must add them both up separately.
    interview_assets = InterviewAsset.objects.filter(interview=interview)
    for asset in interview_assets:
        asset_count[asset.asset_type]['count'] += 1
        total_assets += 1

    session_assets = SessionAsset.objects.filter(session__interview=interview)
    for asset in session_assets:
        asset_count[asset.asset_type]['count'] += 1
        total_assets += 1

    asset_count_list = [x for _, x in asset_count.items()]
    asset_count_list.append({'name': 'Total files', 'count': total_assets})

    return list(filter(lambda x: x['count'] > 0, asset_count_list))


@register.inclusion_tag('heritage/gisfeature_list_include.html')
def heritage_feature_list(attach_id, ajax_url=reverse_lazy('heritage:api:sites-list'), **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('heritage/gisfeature_map_include.html')
def heritage_feature_map(attach_id, map_settings, **kwargs):
    response = {
        'attach_id': attach_id,
        'map_settings': map_settings
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response
