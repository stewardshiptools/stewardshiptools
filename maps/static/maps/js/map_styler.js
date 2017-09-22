function MapStyleHelper() {
    this.pointToLayer = function (feature, latlng) {
        try {
            var helper = new MapStyleHelper();
            var map_style = null;

            // check if we are in hacked geometry collection object:
            if (helper.is_hacked(feature)) {
                // the remover gets called out of context, just make a new object to call it:
                map_style = feature.geometry.properties.map_style;
            }
            else {
                map_style = feature.properties.map_style;
            }

            var style = null;
            if (map_style.composite) {
                style = helper.get_point_style_from_composite(map_style);
            }
            else {
                style = map_style;
            }

            // save the layer type for the switch otherwise removing invalid props would kill it.
            var leaflet_layer_type = style.leaflet_layer_type;
            style = helper.remove_invalid_properties(style);


            switch (leaflet_layer_type) {
                case 'circle':
                    // this only worked with the old style of circle option syntax. hm.
                    return L.circle(latlng, style.radius, style);
                    // return L.circle(latlng, style);
                    break;
                case 'circleMarker':
                    return L.circleMarker(latlng, style);
                    break;
                case 'fa-marker':
                    return L.marker(latlng, {
                        icon: L.AwesomeMarkers.icon(style)
                    });
                    // return L.marker(latlng, {
                    //     icon: L.AwesomeMarkers.icon({
                    //         prefix: 'fa',
                    //         icon: 'fa-address-book',
                    //         markerColor: 'red',
                    //         iconColor: 'blue'
                    //     })
                    // });
                    break;
                default:
                    return L.marker(latlng);
            }
        }
        catch (err) {
            // something bad happened, return a plain jane (sorry mom) marker:
            return L.marker(latlng);
        }
    };
    this.onEachFeature = function (feature, layer) {
        // console.log("on each feature. feature:", feature, "layer:", layer);
    };
    this.style = function (feature) {
        // We can't depend on the map_style making into the feature properties
        // due to silliness with the serializer. Use the class-level data.
        try {
            var helper = new MapStyleHelper();
            var map_style = {};

            // check if we are in hacked geometry collection object:
            if (helper.is_hacked(feature)) {
                // the remover gets called out of context, just make a new object to call it:
                map_style = feature.geometry.properties.map_style;
            }
            else {
                map_style = feature.properties.map_style;
            }
            if (map_style.composite) {
                return helper.remove_invalid_properties(
                    helper.get_path_style_from_composite(map_style)
                );
            }
            else {
                return helper.remove_invalid_properties(map_style);
            }
        }
        catch (err) {
            // console.warn("map styler did not find a map style. err msg:", err);
            return {};
        }
    };
    this.options = {
        // shortcut to supply the three methods to a leaflet layer options parameter
        pointToLayer: this.pointToLayer,
        onEachFeature: this.onEachFeature,
        style: this.style

    };
    this.remove_invalid_properties = function (style) {
        //clone it
        style = jQuery.extend({}, style);
        delete style.leaflet_layer_type;
        return style;
    };
    this.has = function (object, key) {
        return object ? hasOwnProperty.call(object, key) : false;
    };
    this.is_hacked = function (feature) {
        var hack = false;
        if (feature.hasOwnProperty('geometry')) {
            if (feature.geometry.hasOwnProperty('properties')) {
                hack = true;
            }
        }
        return hack;
    };
    this.get_path_style_from_composite = function (map_style) {
        if (map_style.polyline_style) {
            return map_style.polyline_style;
        }
        else {
            return map_style.polygon_style;
        }
    };
    this.get_point_style_from_composite = function (map_style) {
        if (map_style.marker_style) {
            return map_style.marker_style;
        }
        else {
            return map_style.circle_style;
        }
    }
}
