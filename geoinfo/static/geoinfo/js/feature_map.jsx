var map_settings = geoinfo_feature_map_settings;

ReactDOM.render(
    <LeafletMap width="auto" height="500px" settings={map_settings} map_id={geoinfo_feature_map_attach_id} callback={get_data_build_map}/>,
    document.getElementById(geoinfo_feature_map_attach_id)
);
