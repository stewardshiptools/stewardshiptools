import time
import logging
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.gis.measure import D
from django.contrib.gis.db.models import Union, GeometryField
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Value, F, CharField, Func, IntegerField, Q
from django.db.models.functions import Coalesce
from rest_framework import viewsets, filters, generics
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework import permissions
from django_filters import MethodFilter
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework_gis.filterset import GeoFilterSet

# Expose celery tasks to views (for webhooks)
from geoinfo import tasks  # noqa

from .serializers import GISLayerSerializer, GISLayerMasterSerializer, GISFeatureSerializer,\
    GISFeatureGeoJSONSerializer, GISFeaturePointGeoJSONSerializer, GISFeatureLineGeoJSONSerializer,\
    GISFeaturePolygonGeoJSONSerializer, GISFeatureDistanceSerializer, SpatialReportSerializer
from .models import GISLayerMaster, GISLayer, GISFeature, GISFeaturePolygon, GISFeatureLine, GISFeaturePoint, SpatialReport,\
    SpatialReportItem
from .forms import GISLayerAdminForm, SpatialReportForm, SpatialReportItemForm, GeneralSpatialReportForm
from .utils.reports import extract_ajax_urls_from_spatialreport, get_api_cache_key_from_view
from .functions import CastGeometry

from help.mixins import HelpContextMixin
from cedar.mixins import EditObjectMixin
from cedar_settings.models import GeneralSetting

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DashboardView(HelpContextMixin, TemplateView):
    template_name = 'geoinfo/dashboard.html'
    page_help_name = 'geoinfo:dashboard'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['layer_count'] = GISLayer.objects.all().count()
        context['layer_master_count'] = GISLayerMaster.objects.all().count()
        context['spatialreport_count'] = SpatialReport.objects.all().count()
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class GISLayerMasterListView(HelpContextMixin, ListView):
    model = GISLayerMaster
    page_help_name = 'geoinfo:layer-master-list'
    ajax_url_name = 'geoinfo:layer-master-list-api'

    def get_context_data(self, **kwargs):
        context = super(GISLayerMasterListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse(self.ajax_url_name)
        context['layer_type_choices'] = self.get_layer_type_choices()
        context['default_layer_type'] = self.get_default_layer_type()
        return context

    def get_default_layer_type(self):
        '''
        Set the selected layer type choice in the layer type dropdown
        :return:
        '''
        default_layer_type = getattr(self, 'default_layer_type', None)
        if default_layer_type:
            return default_layer_type
        else:
            return ''

    def get_layer_type_choices(self):
        '''
        Gathers a list of layer types for the filter drop-down in the template.
        If you want "All" option you have to provide it, value is ""
        :return: a list of dicts[<option_name>:<option_value>]
        '''
        options = [{'All':''}]
        options.extend(
            [{x['layer_type']: x['layer_type']} for x in self.model.objects.values("layer_type").distinct().order_by('layer_type')]
        )
        return options

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerMasterListView, self).dispatch(request, *args, **kwargs)


class GISLayerListView(HelpContextMixin, ListView):
    '''
    I think this is the Misc Layers List view?
    If so, it is deprecated but left here in case
    someone objects.
    '''
    model = GISLayer
    page_help_name = 'geoinfo:gislayer-list'
    ajax_url_name = 'geoinfo:api:layer-list'

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GISLayerListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse(self.ajax_url_name)
        return context


class GISLayerCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = GISLayer
    form_class = GISLayerAdminForm
    page_help_name = 'geoinfo:gislayer-create'
    edit_object_cancel_url = reverse_lazy('geoinfo:layer-list')

    # if we specify the template here then we don't have to re-specify it in any subclasses (if we don't want to).
    template_name = 'geoinfo/gislayer_form.html'

    def get_form_kwargs(self):
        kwargs = super(GISLayerCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @method_decorator(permission_required('geoinfo.add_gislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        # TODO Find a way to reliably get information about features created for new as well as updated layers.
        # counts = "{polygon_count} polygons, {line_count} lines, and {point_count} points.".format(
        #     **form.instance.get_stats
        # )
        # messages.add_message(self.request, messages.INFO,
        #                      "Successfully created {} with {}".format(form.instance.name, counts))

        return super().form_valid(form)


class GISLayerUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = GISLayer
    form_class = GISLayerAdminForm
    page_help_name = 'geoinfo:gislayer-update'
    edit_object_delete_perm = 'geoinfo:delete_gislayer'

    # if we specify the template here then we don't have to re-specify it in any subclasses (if we don't want to).
    template_name = 'geoinfo/gislayer_form.html'

    def get_edit_object_cancel_url(self):
        return self.object.get_absolute_url()

    def get_edit_object_delete_url(self):
        return reverse("geoinfo:layer-delete", args=[self.object.id])

    def get_form_kwargs(self):
        kwargs = super(GISLayerUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @method_decorator(permission_required('geoinfo.change_gislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerUpdateView, self).dispatch(request, *args, **kwargs)


class GISLayerDeleteView(HelpContextMixin, DeleteView):
    model = GISLayer
    success_url = reverse_lazy('geoinfo:layer-list')
    page_help_name = 'geoinfo:gislayer-delete'
    template_name = 'geoinfo/gislayer_confirm_delete.html'

    @method_decorator(permission_required('geoinfo.delete_gislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerDeleteView, self).dispatch(request, *args, **kwargs)


class GISLayerDetailView(HelpContextMixin, DetailView):
    model = GISLayer
    page_help_name = 'geoinfo:gislayer-detail'
    template_name = 'geoinfo/gislayer_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GISLayerDetailView, self).get_context_data(**kwargs)
        # Put in the extra "&" in case filtering is done in the page and exta queries are added automatically.
        context['feature_ajax_url'] = "{}?{}={}".format(reverse('geoinfo:api:feature-list'), 'layer', self.object.id)
        context['feature_ajax_geojson_url'] = "{}?{}={}&as_geojson=1".format(reverse('geoinfo:api:feature-list'),
                                                                             'layer', self.object.id)
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(GISLayerDetailView, self).dispatch(request, *args, **kwargs)


class GISFeatureDetailView(HelpContextMixin, DetailView):
    model = GISFeature
    page_help_name = 'geoinfo:gisfeature-detail'

    def get_context_data(self, **kwargs):
        context = super(GISFeatureDetailView, self).get_context_data(**kwargs)
        context['feature_ajax_geojson_url'] = feature_ajax_url = "%s?as_geojson=1" %\
                                                                 reverse('geoinfo:api:feature-detail',
                                                                         args=[self.object.id], request=self.request)
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(GISFeatureDetailView, self).dispatch(request, *args, **kwargs)


class SpatialReportListView(HelpContextMixin, ListView):
    model = SpatialReport
    page_help_name = 'geoinfo:spatialreport-list'

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportListView, self).dispatch(request, *args, **kwargs)


class SpatialReportCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = SpatialReport
    form_class = SpatialReportForm
    page_help_name = 'geoinfo:spatialreport-create'
    edit_object_cancel_url = reverse_lazy('geoinfo:spatialreport-list')

    @method_decorator(permission_required('geoinfo.add_spatialreport', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportCreateView, self).dispatch(request, *args, **kwargs)


class SpatialReportUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = SpatialReport
    form_class = SpatialReportForm
    page_help_name = 'geoinfo:spatialreport-update'
    edit_object_delete_perm = 'geoinfo:delete_spatialreport'

    def get_edit_object_cancel_url(self):
        return reverse('geoinfo:spatialreport-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('geoinfo:spatialreport-delete', args=[self.object.id])

    @method_decorator(permission_required('geoinfo.change_spatialreport', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportUpdateView, self).dispatch(request, *args, **kwargs)


class SpatialReportDeleteView(HelpContextMixin, DeleteView):
    model = SpatialReport
    success_url = reverse_lazy('geoinfo:spatialreport-list')
    page_help_name = 'geoinfo:spatialreport-delete'

    @method_decorator(permission_required('geoinfo.delete_spatialreport', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportDeleteView, self).dispatch(request, *args, **kwargs)


class SpatialReportDetailView(HelpContextMixin, DetailView):
    model = SpatialReport
    page_help_name = 'geoinfo:spatialreport-detail'

    def get_context_data(self, **kwargs):
        context = super(SpatialReportDetailView, self).get_context_data(**kwargs)

        report_ajax_urls = extract_ajax_urls_from_spatialreport(self.object)
        context['report_ajax_urls'] = report_ajax_urls

        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportDetailView, self).dispatch(request, *args, **kwargs)


class SpatialReportItemCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = SpatialReportItem
    form_class = SpatialReportItemForm
    page_help_name = 'geoinfo:spatialreportitem-create'

    def get_edit_object_cancel_url(self):
        return reverse('geoinfo:spatialreport-detail', args=[self.kwargs.get('report_pk')])

    def get_form_kwargs(self):
        kwargs = super(SpatialReportItemCreateView, self).get_form_kwargs()
        kwargs['report_id'] = self.kwargs.get('report_pk', None)
        return kwargs

    @method_decorator(permission_required('geoinfo.add_spatialreport', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportItemCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('geoinfo:spatialreport-detail', kwargs={'pk': self.object.report.pk})

    def report(self):
        report_pk = self.kwargs.get('report_pk', None)
        if report_pk:
            return SpatialReport.objects.get(id=report_pk)
        return None


class SpatialReportItemUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = SpatialReportItem
    form_class = SpatialReportItemForm
    page_help_name = 'geoinfo:spatialreportitem-update'
    edit_object_delete_perm = 'geoinfo:delete_spatialreportitem'

    def get_edit_object_cancel_url(self):
        return reverse('geoinfo:spatialreport-detail', args=[self.kwargs.get('report_pk')])

    def get_edit_object_delete_url(self):
        return reverse('geoinfo:spatialreportitem-delete', args=[self.kwargs.get('report_pk')])

    def get_form_kwargs(self):
        kwargs = super(SpatialReportItemUpdateView, self).get_form_kwargs()
        kwargs['report_id'] = self.kwargs.get('report_pk', None)
        return kwargs

    @method_decorator(permission_required('geoinfo.add_spatialreport', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportItemUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('geoinfo:spatialreport-detail', kwargs={'pk': self.object.report.pk})

    def report(self):
        report_pk = self.kwargs.get('report_pk', None)
        if report_pk:
            return SpatialReport.objects.get(id=report_pk)
        return None


class SpatialReportItemDeleteView(HelpContextMixin, DeleteView):
    model = SpatialReportItem
    page_help_name = 'geoinfo:spatialreportitem-delete'

    @method_decorator(permission_required('geoinfo.delete_spatialreportitem', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(SpatialReportItemDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('geoinfo:spatialreport-detail', kwargs={'pk': self.object.report.pk})


class GenericSpatialReportFormView(EditObjectMixin, FormView):
    template_name = 'geoinfo/spatialreport_generic_form.html'
    form_class = GeneralSpatialReportForm
    edit_object_delete_perm = 'geoinfo:delete_spatialreport'

    def get_success_url(self):
        if self.report:
            return reverse('geoinfo:spatialreport-detail', kwargs={'pk': self.report.pk})
        else:
            return reverse('geoinfo:spatialreport-list')  # TODO: Replace this with the url of the created spatialreport.

    def get_initial(self):
        initial = super(GenericSpatialReportFormView, self).get_initial()
        initial['distance_cap'] = "5km"
        return initial

    def form_valid(self, form):
        return super(GenericSpatialReportFormView, self).form_valid(form)

    def create_new_report(self, name, distance_cap, report_on, item_layer_set, report=None):
        if report is None:
            report = SpatialReport.objects.create(name=name, distance_cap=distance_cap)

        for layer in report_on:
            report.report_on.add(layer)

        report.save()

        for layer in item_layer_set:
            SpatialReportItem.objects.create(report=report, distance_cap=distance_cap, layer=layer)

        return report


# Rest API viewsets
class GISLayerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = GISLayer.objects.all()
    serializer_class = GISLayerSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('input_type',)
    search_fields = ('name', 'input_type', 'notes', 'author__username', 'author__first_name', 'author__last_name')
    ordering_fields = '__all__'
    ordering = ('name', '-created')


class GISLayerMasterListAPIView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = GISLayerMaster.objects.all()
    serializer_class = GISLayerMasterSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('input_type', 'layer_type')
    search_fields = ('name', 'input_type', 'notes', 'author__username', 'author__first_name', 'author__last_name',
                     'layer_type')
    ordering_fields = '__all__'
    ordering = ('name', '-created')


class GISFeatureViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = GISFeature.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'layer')
    search_fields = ('name', 'data')
    ordering_fields = '__all__'
    ordering = ('name',)
    geojson_serializer_class = GISFeatureGeoJSONSerializer
    default_serializer_class = GISFeatureSerializer

    def get_serializer_class(self):
        include_geoms = int(self.request.query_params.get('as_geojson', 0))

        if include_geoms:
            return self.geojson_serializer_class

        return self.default_serializer_class

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response

        t = time.time()
        queryset = self.filter_queryset(self.get_queryset())
        logger.debug("GISFeatureViewSet-list:filter-queryset; layer: {}. response time= {} sec.".format(
            self.request.query_params.get('layer', None), time.time() - t))

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

        else:
            # I'm not convinced running select_related is doing anything, but leaving here in hope.
            # t = time.time()
            # queryset = queryset.select_related()
            # logger.debug("GISFeatureViewSet-list:select_related_fields; layer: {}. response time= {} sec.".format(
            #     self.request.query_params.get('layer', None), time.time() - t))


            t = time.time()
            serializer = self.get_serializer(queryset, many=True)
            logger.debug("GISFeatureViewSet-list:get-serializer; layer: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), time.time() - t))

            t = time.time()
            data = serializer.data
            logger.debug("GISFeatureViewSet-list:serializer-data; layer: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), time.time() - t))

            t = time.time()
            response = Response(data)
            logger.debug("GISFeatureViewSet-list:build-response; layer: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), time.time() - t))

        return response

    def get_queryset(self):
        queryset = self.queryset

        simplify_tolerance = GeneralSetting.objects.get('geoinfo__default_feature_simplify_tolerance')

        '''
        # Simple Coalesce query to get the separate geoms up into the GISFeature query.
        queryset = queryset.annotate(geom_co=Coalesce(
            F('gisfeaturepolygon__geometry'), F('gisfeatureline__geometry'), F('gisfeaturepoint__geometry'), output_field=GeometryField()
            ))
        '''

        '''
        This query runs a coalesce (as described above), then Casts the geography to geometry,
        then projects to web merc, then projects BACK to geography (4326).
        '''

        queryset = queryset.annotate(
            geom_simple=Func(
                            Func(
                                Func(CastGeometry(
                                    Coalesce(
                                        F('gisfeaturepolygon__geometry'), F('gisfeatureline__geometry'), F('gisfeaturepoint__geometry'), output_field=GeometryField()
                                        ),
                                        GeometryField()
                                    ),
                                    Value(3785),
                                    function='ST_Transform'
                                ),
                                Value(float(simplify_tolerance)),
                                Value(True),                # Preserve collapsed. Requires PostGIS 2.2+
                                function='ST_Simplify'),
                            Value(4326),
                            function='ST_Transform'
                        )
            )

        return queryset


class GISFeatureShapeViewSet(generics.ListAPIView):
    '''
    This api should be subclassed and only called by its children, not directly.
    Used by the reporting tools to filter the queryset by distance to a layer. Other
    uses?
    '''
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ['name', 'layer']
    search_fields = ('name', 'layer__name', 'data')
    ordering_fields = '__all__'
    ordering = ('distance',)

    model = GISFeature  # Override me!
    default_serializer = GISFeatureDistanceSerializer  # do not override.
    geojson_serializer = GISFeatureDistanceSerializer  # Override me!  This default is so that as_geojson does nothing.

    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def list(self, request, *args, **kwargs):
        outer_time = time.time()
        cache_key = get_api_cache_key_from_view(self, request)
        response = cache.get(cache_key, None) # Grab the cache, default to None

        if response is None:
            t = time.time()
            response = super(GISFeatureShapeViewSet, self).list(request, *args, **kwargs)
            logger.debug("GISFeatureShapeViewSet-list; layer: {}. geomclass: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), str(self.model), time.time() - t))

            t = time.time()
            response = self.finalize_response(request, response, *args, **kwargs)
            logger.debug("GISFeatureShapeViewSet-finalize; layer: {}. geomclass: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), str(self.model), time.time() - t))

            t = time.time()
            response.render()
            logger.debug("GISFeatureShapeViewSet-render; layer: {}. geomclass: {}. response time= {} sec.".format(
                self.request.query_params.get('layer', None), str(self.model), time.time() - t))

            cache.set(cache_key, response, None)  # Set timeout to none so it never expires.

        # Not really sure if this is needed.  Adding it since it's in the drf-util package's
        # version of response caching.
        if not hasattr(response, '_closable_objects'):
            response._closable_objects = []

        return response

    def get_queryset(self):
        '''
            distance_layer_id_string is analogous to REPORT ON LAYERs. It is derived from the 'distance_from'
            request parameter (csv value).
            distance_layer_id_list - yeah I know it doesn't need to be called that here, but it makes
            this method so much more readable.
            NOTE:
                layer_id is analogous to REPORT AGAINST LAYER
                distance_layer_id_string and distance_layer_id_list are analogous to REPORT ON LAYERS
            NOTE:
                API list filters are applied after get_queryset, so they can't be relied on in the get_queryset method.
        :return:
        '''
        outer_time = time.time()

        # layer_id is analogous to REPORT AGAINST LAYER
        # TODO Investigate if it's worth using self.filter_queryset() here instead.
        layer_id = self.request.query_params.get('layer', None)
        if layer_id:
            queryset = self.model.objects.filter(layer=layer_id)
        else:
            queryset = self.model.objects.all()

        # Something is needed to give an empty meaningless distance when a distance query isn't being run in order
        # to keep the serializer happy.
        queryset = queryset.annotate(distance=Value(None, CharField()))

        distance_layer_id_string = self.request.query_params.get('distance_from', None)
        if distance_layer_id_string is None:
            return queryset

        distance_layer_id_list = distance_layer_id_string.split(',')

        distance_cap = self.request.query_params.get('distance_cap', None)  # A measurement in meters

        '''
        # create a coalesce query to gather the geoms of the report_on_layer features and collect into one geometry feature:
        '''
        queryset_collector = GISFeature.objects.filter(layer__id__in=distance_layer_id_list)\
            .annotate(geom_collected=
                Func(
                    CastGeometry(
                        Coalesce(
                            F('gisfeaturepolygon__geometry'),
                            F('gisfeatureline__geometry'),
                            F('gisfeaturepoint__geometry'),
                            output_field=GeometryField()
                        ),
                        GeometryField()
                    ),
                    function='ST_COLLECT'
                )
        ).values('geom_collected')

        # if we simplify the geometry that we'll use to do the distance query we get a big performance boost.
        # We don't care about topology.
        # geom = GEOSGeometry(queryset_collector[0]['geom_collected']).simplify(tolerance=2, preserve_topology=False)
        geom = GEOSGeometry(queryset_collector[0]['geom_collected'])

        if distance_cap:
            queryset = queryset.filter(geometry__dwithin=(geom, D(m=distance_cap)))

        queryset_distance = queryset.distance(geom)
        # distance_time = time.time()
        # logger.debug("distance_time: {} sec. # features: {}".format(time.time() - distance_time, queryset_distance.count()))

        logger.debug("dis_layer_id_string: {}. d_cap {}. model_type {}. outertime= {} sec.".format(
            distance_layer_id_string, distance_cap, str(self.model), time.time() - outer_time))

        return queryset_distance

    def get_serializer_class(self):
        include_geoms = int(self.request.query_params.get('as_geojson', 0))

        if include_geoms:
            return self.geojson_serializer

        return self.default_serializer


class GISFeaturePointViewSet(GISFeatureShapeViewSet):
    '''
    By default, falls back to GISFeatureDistanceSerializer if as_geojson url parameter is not supplied
    '''
    permission_classes = (permissions.IsAuthenticated,)
    model = GISFeaturePoint
    geojson_serializer = GISFeaturePointGeoJSONSerializer

    def get_queryset(self):
        qs = super(GISFeaturePointViewSet, self).get_queryset()

        # simplify it:
        simplify_tolerance = GeneralSetting.objects.get('geoinfo__default_feature_simplify_tolerance')

        # Maybe there's not point to simplifying a point set. Postgis will figure it out.
        qs = qs.annotate(
            geom_simple=Func(
                Func(
                    Func(CastGeometry(
                        F('geometry'),
                        GeometryField()), Value(3785), function='ST_Transform'),
                    Value(float(simplify_tolerance)),
                    Value(True),  # Preserve collapsed. Requires PostGIS 2.2+
                    function='ST_Simplify'),
                Value(4326),
                function='ST_Transform')
        )
        return qs


class GISFeatureLineViewSet(GISFeatureShapeViewSet):
    '''
    By default, falls back to GISFeatureDistanceSerializer if as_geojson url parameter is not supplied
    '''
    permission_classes = (permissions.IsAuthenticated,)
    model = GISFeatureLine
    geojson_serializer = GISFeatureLineGeoJSONSerializer

    def get_queryset(self):
        qs = super(GISFeatureLineViewSet, self).get_queryset()

        # simplify it:
        simplify_tolerance = GeneralSetting.objects.get('geoinfo__default_feature_simplify_tolerance')
        qs = qs.annotate(
            geom_simple=Func(
                            Func(
                                Func(CastGeometry(
                                    F('geometry'),
                                    GeometryField()), Value(3785), function='ST_Transform'),
                                Value(float(simplify_tolerance)),
                                Value(True),  # Preserve collapsed. Requires PostGIS 2.2+
                                function='ST_Simplify'),
                            Value(4326),
                            function='ST_Transform')
            )
        return qs


class GISFeaturePolygonViewSet(GISFeatureShapeViewSet):
    '''
    By default, falls back to GISFeatureDistanceSerializer if as_geojson url parameter is not supplied
    '''
    permission_classes = (permissions.IsAuthenticated,)
    model = GISFeaturePolygon
    geojson_serializer = GISFeaturePolygonGeoJSONSerializer

    def get_queryset(self):
        qs = super(GISFeaturePolygonViewSet, self).get_queryset()
        # return qs

        # simplify it:
        simplify_tolerance = GeneralSetting.objects.get('geoinfo__default_feature_simplify_tolerance')
        qs = qs.annotate(
            geom_simple=Func(
                            Func(
                                Func(CastGeometry(
                                    F('geometry'),
                                    GeometryField()), Value(3785), function='ST_Transform'),
                                Value(float(simplify_tolerance)),
                                Value(True),  # Preserve collapsed. Requires PostGIS 2.2+
                                function='ST_Simplify'),
                            Value(4326),
                            function='ST_Transform')
            )
        return qs


class SpatialReportViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SpatialReport.objects.all()
    serializer_class = SpatialReportSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('report_on',)
    search_fields = ('name', 'distance_cap', 'report_on__name')
    ordering_fields = '__all__'
    ordering = ('name',)
