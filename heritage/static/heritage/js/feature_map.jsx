var map_settings = interview_map_settings;
map_settings.event_name = interview_list_id;

map_settings.get_feature_data = function(feature) {
    var data = {};
    var i = 0;

    for (var key in feature.data) {
        if (feature.data[key]) {
            data[key] = feature.data[key];
        }

        // We only want to show the first 10 attributes
        if (++i > 10) {
            break;
        }
    }

    return data;
};

map_settings.get_feature_name = function(feature) {
    return feature.name;
};

ReactDOM.render(
    <LeafletMap width="auto" height="500px" settings={map_settings} map_id={interview_map_id} callback={get_data_build_map} />,
    document.getElementById(interview_map_id)
);
