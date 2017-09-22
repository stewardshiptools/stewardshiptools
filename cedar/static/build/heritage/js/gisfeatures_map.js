(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var map_settings = speciesobservations_map_settings;
map_settings.event_name = "SpeciesObservationsUpdated";
map_settings.layer_name = "Species Records";
map_settings.layer_id = "species_records";

map_settings.get_feature_data = function (feature) {
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

map_settings.get_feature_name = function (feature) {
    return feature.species.description;
};

ReactDOM.render(React.createElement(LeafletMap, { width: "auto", height: "500px", settings: map_settings, map_id: speciesobservations_map_id, callback: get_data_build_map }), document.getElementById(speciesobservations_map_id));

},{}]},{},[1]);
