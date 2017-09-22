var map_settings = spatialreport_feature_map_settings;


function build_popup(feature) {
    // var popup = L.DomUtil.create('div', settings.machine_name + '-popup');
    var popup = L.DomUtil.create('div', "machine-name-something" + '-popup');
    popup.innerHTML += '<a href="' + feature.properties.url + '">' + feature.properties.name + '</a>';
    
    if (feature.properties.distance) {
        popup.innerHTML += '<br /><strong>Distance: ' + feature.properties.distance.value +
            ' ' + feature.properties.distance.unit + '</strong>';

    }
    popup.innerHTML += '<br /><br/>' + formatProperties(feature.properties.data);
    return popup;
}


function get_data_build_map(settings, map, switcher) {
    make_drill_button(map);
    convert_leaflet_control_titles_to_tooltips();
    
    var ajax_accessable_items = {};
    
    // Loop through each item passed into the component.
    // Each item contains info about the item, the layer, and the ajax urls (point, line, and polygon)
    for (var i = 0; i < spatialreport_items.length; i++) {
        var item = spatialreport_items[i];

        // The urls dictionary always contains 'point', 'line', and 'polygon'
        // as_geojson=1 is missing by default since it's easy to add our self later.
        for (var shape_type in item.urls) {
            var ajax_url = item.urls[shape_type];

            // Spinner should go here.... Let's use the leaflet ajax spinner though.
            /* ... */

            var query_start = '?';
            if (ajax_url.split('?').length > 1) {
                query_start = '&';
            }

            map.spin(true);
            $.ajax({
                url: ajax_url + query_start + "limit=&offset=0&as_geojson=1",
                dataType: 'json',
                cache: false,
                beforeSend: function () {
                    ajax_accessable_items[item.layer.id] = {
                        'report_item': item.report_item
                    };
                },
                success: function (data) {
                    var results = data.results || data;
                    
                    if (results.features.length == 0) {
                        map.spin(false);
                        return;
                    }
                    
                    // Spatialreports don't provide any custom styles at the moment.  Let's prepare some
                    // simple ones here.
                    var style = null;
                    if (ajax_accessable_items[results.features[0].properties.layer.id].report_item) {
                        // Do nothing...
                    } else {
                        style = {
                            color: '#f00'
                        };
                    }

                    //Handle a feature collection result OR
                    // assume the result is a single feature geojson object:
                    if (results.features) {
                        for (var i in results.features) {
                            var temp_feature = results.features[i];
                            add_feature_to_map(map, results.features[i], style);
                        }
                    }
                    else {
                        add_feature_to_map(map, results, style);
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
                            cedar_layers[idx].eachLayer(function (sub_layer) {
                                sub_layer.bindPopup(build_popup(sub_layer.feature));
                            });

                            //Add layers to switcher:
                            switcher.addOverlay(cedar_layers[idx], cedar_layers[idx].cedar_properties.layer_name);
                        }
                    }

                    // Zoom to the new layers:
                    map.fitBounds(get_extent_of_layers(cedar_layers));

                    map.spin(false);
                },
                error: function (xhr, status, err) {
                    map.spin(false);
                    console.error(ajax_url, status, err.toString());
                }.bind(ajax_url),
                done: function (url, options) {
                    map.spin(false)
                }
            });
        }
    }
}


ReactDOM.render(
    <LeafletMap width="auto" height="500px" settings={map_settings} map_id={spatialreport_feature_map_attach_id} callback={get_data_build_map}/>,
    document.getElementById(spatialreport_feature_map_attach_id)
);
