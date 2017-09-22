(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

var map_settings = geoinfo_feature_map_settings;

// Monkey-patch the geoinfo_map_utils layer switchter text function:
make_layer_switcher_layer_text = function make_layer_switcher_layer_text(layer) {
    var edit_url = layer.cedar_properties.edit_url;
    var delete_url = layer.cedar_properties.delete_url;

    var s_text = '<span> ' + layer.cedar_properties.layer_name + '<a class="waves-grey lighten-5 grey-text text-darken-1 tooltipped-maps" href="' + delete_url + '" data-tooltip="Delete Layer" data-position="bottom">' + '<span class="right">' + '<i class="material-icons" style="font-size:inherit;">delete</i>' + '</span>' + '</a>' + '</span>' + '<a class="waves-grey lighten-5 grey-text text-darken-1 tooltipped-maps" href="' + edit_url + '" data-tooltip="Edit Layer" data-position="left">' + '<span class="right">' + '<i class="material-icons" style="font-size:inherit;">mode_edit</i>' + '</span>' + '</a>';
    return s_text;
};

post_build = function post_build(map) {
    console.log("POST BUILD");
    //add a "create layer" button to the map controls:
    // <a class="waves-grey lighten-5 grey-text text-darken-1 {{ user|is_disabled:'development.add_developmentproject' }}"
    //    href="{% url 'development:project-location-create' object.id %}"><i class="medium material-icons">edit_location</i>
    // </a>
    var create_url = dev_project_loc_new_base_url;

    var create_layer_button = '<a class="leaflet-control-zoom-out tooltipped-maps-create-layer" href="' + create_url + '" data-tooltip="Add New Layer" data-position="right"> ' + '<i class="material-icons" style="font-size:inherit;">add_location</i>' + '</a>';

    $('div.leaflet-control-zoom').append(create_layer_button);

    //We give it it's own class so we don't call tooltips on all map tools again.
    $('a.tooltipped-maps-create-layer').tooltip();

    /*
    SEE BELOW FOR FAILED ATTEMPTS TO ZOOM THE MAP TO FULL EXTENT WHEN ENTERING
    A PRINT PAGE.
     */

    // for printing, if we resize the map we should reset back to the full extent:
    // $(window).on('resize', function(evt){
    // console.log("window resized");
    // console.log("map resized");
    // console.log("is print page", isPrintPage(evt.target));
    // if (isPrintPage(evt.target)){
    // console.log("map resized");
    // var cedar_bounds = get_extent_of_layers(cedar_layers);
    // console.log("cedarbounds:", cedar_bounds);
    // if (cedar_bounds) {
    //     map.fitBounds(cedar_bounds);
    // }
    // }
    // })

    // map.on('resize', function(evt){
    //     console.log("map resized");
    //     var bounds = get_full_extent(map);
    //     console.log("cedarbounds", bounds.toBBoxString());
    //     if (bounds) {
    //         console.log("fit bounds to:", bounds.toBBoxString());
    //         map.fitBounds(bounds);
    //     }
    // });

    // $("#print-page-indicator").on('print-page:render', function(evt){
    //     var ppindicator = $(this);
    //     console.log("print page event fired from map area");
    //     var bounds = get_full_extent(map);
    //     console.log("cedarbounds", bounds.toBBoxString());
    //
    //     if (bounds) {
    //         console.log("fit bounds to:", bounds.toBBoxString());
    //         map.fitBounds(bounds);
    //     }
    // });
};

ReactDOM.render(React.createElement(LeafletMap, { width: 'auto', height: '500px', settings: map_settings, map_id: geoinfo_feature_map_attach_id, callback: get_data_build_map }), document.getElementById(geoinfo_feature_map_attach_id));

},{}]},{},[1]);
