/**
 * Trigger a jquery event with the name of the attach_id.  This event is used to populate the map.
 * @param attach_id
 * @param results
 */
var trigger_map = function (attach_id, results) {
    $( document ).trigger(attach_id, [results]);
};

ReactDOM.render(
    <FeatureBox url={heritage_feature_list_ajax_url}
                showPager={heritage_feature_list_show_pager}
                showSearch={heritage_feature_list_show_search}
                featuresLoadedHook={trigger_map}
    />,
    document.getElementById(heritage_feature_list_attach_id)
);
