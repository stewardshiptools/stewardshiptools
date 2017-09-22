(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var map_settings = interview_map_settings;
map_settings.event_name = interview_list_id;

map_settings.get_feature_data = function (feature) {
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

map_settings.get_feature_name = function (feature) {
    return feature.name;
};

ReactDOM.render(React.createElement(LeafletMap, { width: "auto", height: "500px", settings: map_settings, map_id: interview_map_id, callback: get_data_build_map }), document.getElementById(interview_map_id));

},{}]},{},[1]);
