var LeafletMap = React.createClass({
    getInitialState: function() {
        return {
            map: null
        };
    },
    componentDidMount: function () {
        // Think SERIOUSLY, about using redux to simplify this.
        // We could just have plugins create stores that we can access here then iterate through them to create maps.
        var map_node = this.props.map_id || ReactDOM.findDOMNode(this);
        var map = L.map(map_node, {
            fullscreenControl: true,
            fullscreenControlOptions: {
                position: 'topleft'
            }
        }).setView([54, -128], 4);

        var base_layers = {};
        var overlay_layers = {};

        // Add overlay_layers:
        console.log("PROPS.SETTINGS:", this.props.settings);
        $.each(this.props.settings.available_overlay_layers, function(key, layer_settings) {
            // make the layer, get it ready to add to layer control
            var new_layer = L.geoJson();

            // add to map if it's the in the visible layers list:
            if (this.props.settings.visible_overlay_layers.indexOf(layer_settings.id)>=0) {
                new_layer.addTo(map);
            }
            overlay_layers[layer_settings.name] = new_layer;

            // send request to populate the layer.
            $.get(layer_settings.url, function(result){
                new_layer.addData(result);
            });
        }.bind(this));

        // Add base layers.
        var create_base_layer = function(layer_settings) {
            var layer = false;
            if (layer_settings.type == 'tile-layer') {
                var subdomains = layer_settings.sub_domains.split(',');
                if (subdomains.length == 1) {
                    subdomains = subdomains[0]
                }

                var layer_leaflet_settings = {
                    attribution: layer_settings.attribution,
                    max_zoom: layer_settings.max_zoom,
                    subdomains: subdomains
                };

                $.extend(layer_leaflet_settings, layer_settings.other_settings);

                layer = L.tileLayer(layer_settings.url_template, layer_leaflet_settings);
            }

            return layer;
        };

        $.each(this.props.settings.base_layers, function(key, layer_settings) {
            var layer = create_base_layer(layer_settings);

            if (layer) {
                if (this.props.settings.base_layers.length == 1 || this.props.settings.default_base_layer.id == layer_settings.id) {
                    layer.addTo(map);
                }
                base_layers[layer_settings.name] = layer;
            }
        }.bind(this));

        var layerSwitcher = L.control.layers(
            base_layers,
            overlay_layers,
            {'collapsed': this.props.settings.layer_control_collapsed});
        
        // Allow custom callbacks to add custom code to maps on top of anything loaded from models.
        if (this.props.callback) {
            this.props.callback(this.props.settings, map, layerSwitcher);
        }

        layerSwitcher.addTo(map);

        this.setState({
            map: map
        });
    },
    //shouldComponentUpdate: function(nextProps, nextState) {
        //return false;
    //},
    render: function() {
        return (
            <div id={this.props.map_id} style={{width: this.props.width, height: this.props.height}}></div>
        );
    }
});

// Expose this component to the global scope so other scripts can use it.
window.LeafletMap = LeafletMap;

// Iterate over any maps on the page and mount LeafletMaps on them.
var leaflet_settings = Window.Leaflet;

if (leaflet_settings) {
    $.each(leaflet_settings, function (machine_name, map_url) {
        // Fetching the settings with AJAX to avoid issues with injecting javascript lists/code into python.
        $.ajax({
            url: map_url,
            dataType: 'json',
            cache: false,
            success: function (map_settings) {
                ReactDOM.render(
                    <LeafletMap width="auto" height="500px" settings={map_settings}/>,
                    document.getElementById(machine_name)
                );
            },
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }
        });
    });
}
