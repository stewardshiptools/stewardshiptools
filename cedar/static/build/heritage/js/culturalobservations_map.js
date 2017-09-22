(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var map_settings = culturalobservations_map_settings;
map_settings.event_name = "CulturalObservationsUpdated";
map_settings.layer_name = "Cultural Records";
map_settings.layer_id = "cultural_records";

map_settings.get_feature_data = function (feature) {
    var data = {};

    if (feature.ecological_feature) {
        data['Ecological feature'] = feature.ecological_feature;
    }
    if (feature.cultural_feature) {
        data['Cultural feature'] = feature.cultural_feature;
    }
    if (feature.industrial_feature) {
        data['Industrial feature'] = feature.industrial_feature;
    }
    if (feature.management_feature) {
        data['Management feature'] = feature.management_feature;
    }

    return data;
};

map_settings.get_feature_name = function (feature) {
    var place_names = [];

    if (feature.gazetted_place_name) {
        place_names.push(feature.gazetted_place_name);
    }
    if (feature.first_nations_place_name) {
        place_names.push(feature.first_nations_place_name);
    }
    if (feature.local_place_name) {
        place_names.push(feature.local_place_name);
    }
    var title = place_names.join(' - ');

    if (!title) {
        console.log(feature);
        if (feature.cultural_feature) {
            title = feature.cultural_feature;
        } else if (feature.ecological_feature) {
            title = feature.ecological_feature;
        } else if (feature.industrial_feature) {
            title = feature.industrial_feature;
        } else if (feature.management_feature) {
            title = feature.management_feature;
        } else if (feature.value_feature) {
            title = feature.value_feature;
        }
    }
    return title;
};

ReactDOM.render(React.createElement(LeafletMap, { width: "auto", height: "500px", settings: map_settings, map_id: culturalobservations_map_id, callback: get_data_build_map }), document.getElementById(culturalobservations_map_id));

},{}]},{},[1]);
