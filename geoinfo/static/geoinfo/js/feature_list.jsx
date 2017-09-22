ReactDOM.render(
    <FeatureBox url={geoinfo_feature_list_ajax_url}
               showPager={geoinfo_feature_list_show_pager}
               showSearch={geoinfo_feature_list_show_search} />,
    document.getElementById(geoinfo_feature_list_attach_id)
);
