var map_settings = speciesobservations_map_settings;
map_settings.event_name = "SpeciesObservationsUpdated";
map_settings.layer_name = "Species Records";
map_settings.layer_id = "species_records";

map_settings.get_feature_data = function(feature) {
    var data = {
        'Species theme': feature.species_theme ? feature.species_theme.name : '',
        'Harvest method': feature.harvest_method ? feature.harvest_method.name : ''
    };

    if (feature.time_frame_start || feature.time_frame_end) {
        data['Time frame'] = '';
        if (feature.time_frame_start) {
            data['Time frame'] += feature.time_frame_start.description;

            if (feature.time_frame_end) {
                data['Time frame'] += ' - ';
            }
        }
        if (feature.time_frame_end) {
            data['Time frame'] += feature.time_frame_end.description;
        }
    }

    return data;
};

map_settings.get_feature_name = function(feature) {
    return feature.species.description;
};

ReactDOM.render(
    <LeafletMap width="auto" height="500px" settings={map_settings} map_id={speciesobservations_map_id} callback={get_data_build_map} />,
    document.getElementById(speciesobservations_map_id)
);
