/**
 * @file
 * heritage_map_utils.js
 * 
 * Extends and overrides parts of geoinfo_map_utils.js
 */

function get_data_build_map(settings, map, switcher) {
    make_drill_button(map);
    convert_leaflet_control_titles_to_tooltips();

    var event_name = settings.event_name || '';
    if (!event_name) {
        return;
    }

    var style = {};

    // Listen for the table to update its contents.
    $( document ).on(event_name, function(e, results) {
        map.spin(true);

        var cedar_layers = get_cedar_layers(map);
        for (var idx in cedar_layers) {
            cedar_layers[idx].clearLayers();
        }
        if (results.length > 0) {
            $.each(results, function (i, result) {
                var layer_name = settings.layer_name;
                var layer_id = settings.layer_id;
                if (result.layer && result.layer.name && result.layer.id) {
                    layer_name = result.layer.name;
                    layer_id = result.layer.id;
                }

                if (!layer_id) {
                    return true; // Continue
                }

                // Shove some useful properties inside the geoJSON.
                var geom = result.geom;

                var data = settings.get_feature_data(result);

                var feature = {
                    id: result.id,
                    type: 'Feature',
                    geometry: geom,
                    properties: {
                        name: settings.get_feature_name(result),
                        url: result.url,  // Link to the record (not the species)
                        data: data,
                        layer: {
                            name: layer_name,
                            id: layer_id
                        }
                    }
                };
                
                add_feature_to_map(map, feature, style);
            });

            //Features added, layers created. Need to do three more things:
            // 1. bind the popups - they get messed up when adding geojson features
            //      one by one to a layer.
            // 2. added cedar overlay layers to the switcher.
            // 3. zoom to combined extents of cedar layers.
            cedar_layers = get_cedar_layers(map);

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
        }

        map.spin(false);
    });
}
