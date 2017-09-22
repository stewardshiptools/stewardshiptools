$( document ).ready(function () {
    // Think SERIOUSLY, about using redux to simplify this.
    // We could just have plugins create stores that we can access here then iterate through them to create maps.
    let leaflet_settings = window.LEAFLET_SETTINGS;

    let map_object_settings = {};

    if (!leaflet_settings.isAppPage) {
        map_object_settings.fullscreenControl = true;
        map_object_settings.fullscreenControlOptions = {
            position: 'topleft'
        };
    }

    let map = L.map("community-map", map_object_settings).setView(
        [leaflet_settings.default_center_lat, leaflet_settings.default_center_lon],
        leaflet_settings.default_initial_zoom
    );

    let base_layers = {};
    let overlay_layers = {};

    // Add overlay_layers:
    $.each(leaflet_settings.available_overlay_layers, function(key, layer_settings) {
        // make the layer, get it ready to add to layer control
        let new_layer = L.geoJson();

        // add to map if it's the in the visible layers list:
        if (leaflet_settings.visible_overlay_layers.indexOf(layer_settings.id)>=0) {
            new_layer.addTo(map);
        }
        overlay_layers[layer_settings.name] = new_layer;

        // send request to populate the layer.
        $.get(layer_settings.url, function(result){
            new_layer.addData(result);
        });
    }.bind(this));

    // Add base layers.
    let create_base_layer = function(layer_settings) {
        let layer = false;
        if (layer_settings.type === 'tile-layer') {
            let subdomains = layer_settings.sub_domains.split(',');
            if (subdomains.length === 1) {
                subdomains = subdomains[0]
            }

            let layer_leaflet_settings = {
                attribution: layer_settings.attribution,
                max_zoom: layer_settings.max_zoom,
                subdomains: subdomains
            };

            $.extend(layer_leaflet_settings, layer_settings.other_settings);

            layer = L.tileLayer(layer_settings.url_template, layer_leaflet_settings);
        }

        return layer;
    };

    $.each(leaflet_settings.base_layers, function(key, layer_settings) {
        let layer = create_base_layer(layer_settings);

        if (layer) {
            if (leaflet_settings.base_layers.length === 1 || leaflet_settings.default_base_layer.id === layer_settings.id) {
                layer.addTo(map);
            }
            base_layers[layer_settings.name] = layer;
        }
    }.bind(this));

    // Overlay layers can go here... Including Places.
    let map_styler = new MapStyleHelper();
    let placeLayer = L.geoJson(null, {
        pointToLayer: map_styler.pointToLayer,
        style: map_styler.style,
        onEachFeature: function (feature, layer) {
            let format_list = function (name, name_plural, items) {
                let output = '<dl>';
                let label = items.length === 1 ? name : name_plural;

                output += '<dt><label>' + label + '</label></dt>';

                output += items.map(function (item_name) {
                    return '<dd>' + item_name + '</dd>';
                }).join('');

                output += '</dl>';

                return output;
            };

            let popup = L.DomUtil.create('div', feature.properties.name + '-popup');

            let innerHTML = '<a href="' + feature.properties.url + '"><h7>' + feature.properties.name + '</h7></a>';

            if (feature.properties.alternate_names.length > 0) {
                innerHTML += format_list("Alternate name", "Alternate names", feature.properties.alternate_names);
            }

            if (feature.properties.common_names.length > 0) {
                innerHTML += format_list("Common name", "Common names", feature.properties.common_names);
            }

            if (feature.properties.gazetteer_names.length > 0) {
                innerHTML += format_list("Gazetteer name", "Gazetteer names", feature.properties.gazetteer_names);
            }


            popup.innerHTML = innerHTML;
            layer.bindPopup(popup);
        }
    });
    placeLayer.addTo(map);
    $.ajax({
        url: leaflet_settings.place_ajax_url,
        dataType: 'json',
        cache: false,
        success: function(data) {
            placeLayer.addData(data);
            map.flyToBounds(placeLayer.getBounds());
        },
        error: function(xhr, status, err) {
            console.error(leaflet_settings.place_ajax_url, status, err.toString());
        }.bind(leaflet_settings)
    });


    let layerSwitcher = L.control.layers(
        base_layers,
        overlay_layers,
        {'collapsed': leaflet_settings.layer_control_collapsed});
    layerSwitcher.addTo(map);

    // Additional features and controls can go here...
    let sidebar = L.control.sidebar('sidebar').addTo(map);
});
