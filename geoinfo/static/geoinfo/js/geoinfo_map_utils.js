/**
 * @file
 * geoinfo_map_utils.js
 * 
 * Tools to be used by maps that involve geoinfo layers and features.
 */

function build_popup(feature) {
    // var popup = L.DomUtil.create('div', settings.machine_name + '-popup');
    var popup = L.DomUtil.create('div', "machine-name-something" + '-popup');
    var innerHTML = '';
    try {
        innerHTML += '<div >';
        innerHTML += '<a href="' + feature.properties.url + '">' + feature.properties.name + '</a>';
        innerHTML += '<br /><br/>' + formatProperties(feature.properties.data);
        innerHTML += '</div>';
        popup.innerHTML = innerHTML;
    }
    catch (err) {
        popup.innerHTML = 'error generating popup';
    }
    return popup;
}

// This gets it's own function for now so when it
// comes time to do something different with drill results
// it's just a matter of re-writting this function.
function build_drill_result_html(feature) {
    return build_popup(feature);
}

function make_layer_switcher_layer_text(layer) {
    var s_text = '<span> ' + layer.cedar_properties.layer_name + '</span>';
    return s_text;
}


function make_event_layer(feature, style = null) {
    // if (style === null){
    //     new MapStyleHelper(feature).style;
    // }
    // else{
    //     var style_func = function (feature) {
    //         var return_style = {
    //             color: '#03f'
    //         };
    //         return_style = $.extend(return_style, style);    // clone the object
    //         return return_style;
    //     }
    // }

    var event_layer = L.geoJson(null, {
        pointToLayer: new MapStyleHelper().pointToLayer,
        style: style ? style : new MapStyleHelper().style,
        onEachFeature: function (feature, layer) {
            var popup = build_popup(feature);
            layer.bindPopup(popup);
        }
    });

    if (feature.properties.layer) {
        // Stuff our own properties into the layer (if it's a cedar layer):
        event_layer['cedar_properties'] = {
            layer_name: feature.properties.layer.name,
            layer_id: feature.properties.layer.id,
            edit_url: feature.properties.layer.edit_url,
            delete_url: feature.properties.layer.delete_url
        };
    }
    return event_layer
}


function make_drill_button(map) {
    var drill_button_options = {
        'text': 'Drill down',  // string
        'doToggle': true,  // bool
        'toggleStatus': false  // bool
    };

    var drill_button = new L.Control.DrillTool(drill_button_options).addTo(map);
    map.on('drill-result', function (evt) {
        // console.log("drill result:", evt.layers);
        update_drill_results(map, evt.layers);
    });

    //Listen for the drill-off so we can reset the drill pane:
    map.on('drill-off', function (evt) {
        // console.log("drill-off:");
        update_drill_results(map, []);
    });

    map.on('drill-on', function (evt) {
        console.log("drill-on");
    });
}


function update_drill_results(map, layers) {

    // Hide the the original drill container and then remove.
    $(map.getContainer())
        .find(".drill-result-card")
        .animate({width: 'toggle'}, 150)
        .remove();


    //Check if there are any layers before proceeding:
    if (layers.length === 0) {
        return;
    }

    var container_height = 'max-height:' + $(map.getContainer()).height() + 'px;';

    var drill_container = $('<div class="drill-result-container" ' +
        'style="position: absolute; right: 0; bottom: 0; ' +
        container_height +
        'max-width:35%;' +
        'z-index: 1000000; ' +
        'display:none; ' +
        'cursor:pointer;' +
        'overflow-y:auto; "></div>');
    $(map.getContainer()).append($(drill_container));

    //Disable event propagation to the map:
    $(drill_container).each(function () {
        L.DomEvent.disableClickPropagation(this)
        L.DomEvent.disableScrollPropagation(this)
    });

    var row = $('<div class="row " style="background-color:rgba(255, 255, 255, 0.65);"></div>');
    var col = $('<div class="col s12"></div>');
    $(drill_container).prepend($(row));
    $(row).append($(col));

    for (var i = 0; i < layers.length; i++) {
        $(col).append($(
            $(
                '<div class="drill-result-card">' +
                '<div class="card-panel">' +
                $(build_drill_result_html(layers[i].feature)).html() +
                '</div>' +
                '</div>'
            )
        ));
    }

    // $(drill_container).animate({width:'toggle'},200);
    $(drill_container).slideToggle();
}

// Looks for a layer that this feature belongs to,
// makes a new layer if one doesn't exist.
function add_feature_to_map(map, feature, style = null) {
    try {
        var map_layer = get_map_layer_by_cedar_layer_id(map, feature.properties.layer.id);
    }
    catch (err) {
        var map_layer = null;
    }
    try {
        map_layer.addData(feature);
    }
    catch (err) {
        // console.log("error adding feature:", feature, ". Error:", err);
        var new_event_layer = make_event_layer(feature, style);
        new_event_layer.addData(feature);
        map.addLayer(new_event_layer);
        // console.log("created new event layer:", new_event_layer.cedar_properties.layer_name);
    }
}

function convert_leaflet_control_titles_to_tooltips() {
    // This assumes that the zoom control control anchors
    // have a 'title' attribute defined and converts that
    // to the tool tip text. The title is then removed.

    // $('.leaflet-control-container').children().each(function () {
    //     $(this).attr('data-tooltip', $(this).attr('title')).attr('data-position', 'right').toggleClass('tooltipped-maps').removeAttr('title');
    // });

    $('.leaflet-control-container').find('[title]').each(function () {
        $(this).attr('data-tooltip', $(this).attr('title')).attr('data-position', 'right').toggleClass('tooltipped-maps').removeAttr('title');
    });

    //initialize map tooltips:
    $('.tooltipped-maps').tooltip();

}

// Returns a layer from the map with the supplied cedar layer id.
function get_map_layer_by_cedar_layer_id(map, cedar_layer_id) {
    lyr = null;
    map.eachLayer(function (layer) {
        try {
            if (layer.cedar_properties.layer_id == cedar_layer_id) {
                lyr = layer;
                return lyr;
            }
        }
        catch (err) {
            //Layer probably didn't have a cedar_properties object no
            // probably not a cedar layer. Keep going.
            // console.log(err);
        }

    });
    return lyr;
}


function get_cedar_layers(map) {
    var layers = [];
    map.eachLayer(function (layer) {
        //If it has a cedar_properties property then it's a cedar layer.
        if (layer.cedar_properties) {
            layers.push(layer);
        }
    });
    return layers;
}

function get_all_layers(map){
    var layers = [];
    map.eachLayer(function (layer) {
        if (layer.cedar_properties) {
            layers.push(layer);
        }
    });
    return layers;
}
function get_full_extent(map){
    var bounds = null;
    map.eachLayer(function (layer) {
        try{
            if (bounds === null){
                bounds = layer.getBounds();
            }
            else {
                bounds.extend(layer.getBounds());
            }
        }
        catch (err){
            //do nothing, probably a tile or some other layer.
        }
    });
    return bounds;
}

function get_extent_of_layers(layer_list) {
    var full_extent = null;
    for (var i = 0; i < layer_list.length; i++) {
        if (full_extent == null) {
            full_extent = layer_list[i].getBounds();
        }
        else {
            full_extent.extend(layer_list[i].getBounds());
        }
    }
    return full_extent;
}


function formatProperties(properties) {
    var i = 0;
    var output = '';

    $.each(properties, function(key, value) {
        if (++i < 5) {
            output += '<strong>' + key + ':</strong> ' + value + '<br />';
        } else {
            return false;
        }
    });

    return output;
}


function get_data_build_map(settings, map, switcher) {

    // Spinner should go here.... Let's use the leaflet ajax spinner though.
    /* ... */

    var ajax_url = geoinfo_feature_map_ajax_url;

    var query_start = '?';
    if (ajax_url.split('?').length > 1) {
        query_start = '&';
    }

    map.spin(true);
    $.ajax({
        url: ajax_url + query_start + "limit=&offset=0",
        dataType: 'json',
        cache: false,
        success: function (data) {
            var results = data.results || data;
            console.log("ajax results:", results);

            //Handle a feature collection result OR
            // assume the result is a single feature geojson object:
            if (results.features) {
                for (var i in results.features) {
                    add_feature_to_map(map, results.features[i]);
                }
            } else {
                add_feature_to_map(map, results);
            }

            //Features added, layers created. Need to do three more things:
            // 1. bind the popups - they get messed up when adding geojson features
            //      one by one to a layer.
            // 2. added cedar overlay layers to the switcher.
            // 3. zoom to combined extents of cedar layers.

            var cedar_layers = get_cedar_layers(map);

            for (var idx in cedar_layers) {
                //If it has a cedar_properties property then it's a cedar layer.
                if (cedar_layers[idx].cedar_properties) {

                    //Bind popups
                    // cedar_layers[idx].eachLayer(function (sub_layer) {
                    //     sub_layer.bindPopup(build_popup(sub_layer.feature));
                    // });

                    //Add layers to switcher:
                    switcher.addOverlay(cedar_layers[idx], make_layer_switcher_layer_text(cedar_layers[idx]));
                }
            }

            // Zoom to the new layers:
            // This can fail if no cedar features were actually returned.
            var cedar_bounds = get_extent_of_layers(cedar_layers);
            if (cedar_bounds) {
                map.fitBounds(cedar_bounds);
            }

            // make_drill_button_old(map);
            make_drill_button(map);

            map.spin(false);

            //Remove lamo leaflet tooltips and add jazzy materializecss ones instead:
            convert_leaflet_control_titles_to_tooltips();


            //call post map build for other overriding templatey things:
            post_build(map);
        },
        error: function (xhr, status, err) {
            map.spin(false);
            console.error(ajax_url, status, err.toString());
        }.bind(ajax_url)
    });
}


// Override this is another .jsx file to run additional js after map is rendered by react.
function post_build(map) {
}


