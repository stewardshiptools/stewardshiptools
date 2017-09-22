/**
 * Created by Adam_2 on 2016-05-24.
 */

L.Control.DrillTool = L.Control.extend({
    options: {
        position: 'topleft'
    },
    initialize: function (options) {
        this._button = {};
        this.setButton(options);
    },

    onAdd: function (map) {
        this._map = map;

        this._map.drillControl = {
            _set_ui_drill_process: this._set_ui_drill_process,
            button: null
        };

        var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-button');

        this._container = container;

        this._update();

        return this._container;
    },

    onRemove: function (map) {
    },

    setButton: function (options) {
        var button = {
            'text': options.text,                   //string
            'hideText': !!options.hideText,         //forced bool
            'maxWidth': options.maxWidth || 70,     //number
            'toggleStatus': options.toggleStatus,    //bool
            'toggleStatusClass': 'blue-text',
            'toggleProcessingClass': 'orange-text',
            'materialIcon': 'play_for_work'
        };

        this._button = button;
        this._update();
        // this._makeButton(this._button);
    },

    destroy: function () {
        this._button = {};
        this._update();
    },

    toggle: function (e) {
        if (typeof e === 'boolean') {
            this._button.toggleStatus = e;
        }
        else {
            this._button.toggleStatus = !this._button.toggleStatus;
        }
    },

    _update: function () {
        if (!this._map) {
            return;
        }
        // this._container.innerHTML = '';
        this._button.el = this._makeButton(this._button);
        this._map.drillControl.button = this._button

    },

    _makeButton: function (button) {
        var newButton = L.DomUtil.create('a', 'leaflet-control-zoom-out tooltiped-maps', this._container);
        // console.log("making button:", button, this._container);

        newButton.setAttribute('title', this._button.text);
        newButton.setAttribute('data-position', 'right');

        var span = L.DomUtil.create('i', 'material-icons', newButton);
        span.setAttribute('style', 'cursor:pointer; font-size:1.3rem; padding-top: 3px');   //This should go in css somewhere
        span.appendChild(document.createTextNode(this._button.materialIcon));


        if (button.toggleStatus) {
            L.DomUtil.addClass(newButton, this._button.toggleStatusClass);
        }

        // Replace default button click listener with out own:
        L.DomEvent.addListener(newButton, 'click', L.DomEvent.stopPropagation);
        L.DomEvent.addListener(newButton, 'click', L.DomEvent.preventDefault);
        L.DomEvent.addListener(newButton, 'click', this._clicked, this);

        //L.DomEvent.disableClickPropagation(newButton);                      // This was suggested by leaflet folks but it messed up the first click.
        //L.DomEvent.addListener(newButton, 'click', L.DomEvent.stop)    //This was preventing the first click on the map from registering.

        return newButton;

    },

    _clicked: function () {
        //'this' refers to button

        // This is weird.
        this.toggle();

        if (this._button.toggleStatus) {
            this._toggle_tool_on();
        }
        else {
            this._toggle_tool_off();
        }
        return;
    },

    _toggle_tool_on: function (e) {
        L.DomUtil.addClass(this._container.childNodes[0], this._button.toggleStatusClass);

        //Set cursor:
        $(this._map.getContainer()).css('cursor', 'crosshair');


        //Disable clicks on layers:
        this._map.eachLayer(
            function (layer) {
                try {
                    this._set_layer_clickable(layer, false);
                    // console.log("layer no clicks set:", layer);
                }
                catch (err) {
                    if (err instanceof TypeError) {
                        // console.log('TypeError setting clickable:', err, " for layer:", layer);
                        //Probably just a tile layer, meh.
                    }
                    else {
                        console.log('error setting clickable:', err, " for layer:", layer);
                    }
                }
            },
            this    //Give "this" context so we can access the do_drill method.
        );
        this._map.on('click', this.do_drill);

        this._map.on('drill-start', function (e) {
            this.drillControl._set_ui_drill_process(e, true);
        });
        this._map.on('drill-stop', function (e) {
            this.drillControl._set_ui_drill_process(e, false);
        });

        this._map.fire("drill-on");
    },

    _toggle_tool_off: function (e) {
        L.DomUtil.removeClass(this._container.childNodes[0], this._button.toggleStatusClass);
        this._map.off('click', this.do_drill);

        //Unset cursor:
        $(this._map.getContainer()).css('cursor', 'inherit');

        //Enable clicks on layers:
        this._map.eachLayer(
            function (layer) {
                try {
                    this._set_layer_clickable(layer, true);
                }
                catch (err) {
                    // console.log('error setting clickable:', err);
                }
            },
            this    //Give "this" context so we can access the do_drill method.
        );
        this._map.fire("drill-off");
    },

    do_drill: function (e, map) {
        var map = e.target;

        // Updating cursor has been shifted off to drill-start and drill-stop event listeners
        // in an attempt to get them to actually work. fail.

        // //Set cursor:
        // $(map.getContainer()).css('cursor', 'progress');
        //
        // console.log(" map.drillControl.button:",  map.drillControl.button);
        // console.log("map.drillControl.button.toggleProcessingClass:", map.drillControl.button.toggleProcessingClass);
        // console.log(" map.drillControl.button.toggleProcessingClass:",  map.drillControl.button.toggleProcessingClass);
        //
        // L.DomUtil.removeClass(map.drillControl.button.el, map.drillControl.button.toggleStatusClass);
        // L.DomUtil.addClass(map.drillControl.button.el, map.drillControl.button.toggleProcessingClass);

        // var turf_point = turf.point([e.latlng.lng, e.latlng.lat])
        var turf_polygon = make_turf_poly_from_click(e, 1, map);

        //Uncomment this line to add the click-polygon to the map and zoom:
        // map.fitBounds(L.geoJson(turf_polygon.geometry).addTo(map).getBounds());

        var intersecting_layers = [];

        // Notify UI a drill is running.
        map.fire('drill-start');

        map.eachLayer(function (layer) {
            if (layer.feature) {
                try {
                    // var intersection = turf.intersect(turf_point, layer.toGeoJSON());
                    var intersection = turf.intersect(turf_polygon, layer.toGeoJSON());
                    if (intersection) {
                        intersecting_layers.push(layer);
                    }
                }
                catch (err) {
                    console.log("drill error:", err);
                }
                //This worked too:
                // console.log("intersects:", buffer.intersects(layer.getBounds()));
                // if (buffer.intersects(layer.feature.geometry)) {
                //     layers.push(layer);
                // }
            }

        }, intersecting_layers);

        // Notify UI the drill has stopped.
        map.fire('drill-stop');

        map.fire('drill-result', {layers: intersecting_layers});

    },

    _set_layer_clickable: function (layer, value) {
        //http://stackoverflow.com/questions/11972816/leaflet-issue-making-layergroup-of-polylines-not-clickable

        if (!hasProp(layer, "options")) {
            return;
        }

        if (value && !layer.options.clickable) {

            layer.options.clickable = true;
            L.Path.prototype._initEvents.call(layer);
            layer._path.removeAttribute('pointer-events');

        } else if (!value && layer.options.clickable) {

            layer.options.clickable = false;

            // undoing actions done in L.Path.prototype._initEvents
            L.DomUtil.removeClass(layer._path, 'leaflet-clickable');
            L.DomEvent.off(layer._container, 'click', layer._onMouseClick);
            ['dblclick', 'mousedown', 'mouseover', 'mouseout', 'mousemove', 'contextmenu'].forEach(function (evt) {
                L.DomEvent.off(layer._container, evt, layer._fireMouseEvent);
            });

            layer._path.setAttribute('pointer-events', layer.options.pointerEvents || 'none');
        }
    },

    _set_ui_drill_process: function (e, is_running) {
        // console.log("setting drill ui. e:", e);

        var map = e.target;
        //Set cursor:
        if (is_running) {
            $(map.getContainer()).css('cursor', 'progress');

            L.DomUtil.removeClass(map.drillControl.button.el, map.drillControl.button.toggleStatusClass);
            L.DomUtil.addClass(map.drillControl.button.el, map.drillControl.button.toggleProcessingClass);
        }
        else {
            $(map.getContainer()).css('cursor', 'crosshair');

            L.DomUtil.addClass(map.drillControl.button.el, map.drillControl.button.toggleStatusClass);
            L.DomUtil.removeClass(map.drillControl.button.el, map.drillControl.button.toggleProcessingClass);
        }
    }

});

//Turns a map click into a px*px square, then into a leaflet Bounds object.
var make_latlng_bounds_from_click = function (evt, pixels, map) {
    var layer_point_min_x = (evt.layerPoint.x - pixels < 0) ? 0 : evt.layerPoint.x - pixels;
    var layer_point_max_x = evt.layerPoint.x + pixels;  //This should test for maximum map point but I don't know how right now.
    var layer_point_min_y = (evt.layerPoint.y - pixels < 0) ? 0 : evt.layerPoint.y - pixels;
    var layer_point_max_y = evt.layerPoint.y + pixels;  //This should test for maximum map point but I don't know how right now.

    var lat_lng_bounds = L.latLngBounds([
        map.layerPointToLatLng(
            L.point(layer_point_min_x, layer_point_min_y)
        ),
        map.layerPointToLatLng(
            L.point(layer_point_max_x, layer_point_max_y)
        )]
    );
    return lat_lng_bounds;

};

//Turns a map click into a px*px square, then into a turf polygon.
var make_turf_poly_from_click = function (evt, pixels, map) {
    var layer_point_min_x = (evt.layerPoint.x - pixels < 0) ? 0 : evt.layerPoint.x - pixels;
    var layer_point_max_x = evt.layerPoint.x + pixels;  //This should test for maximum map point but I don't know how right now.
    var layer_point_min_y = (evt.layerPoint.y - pixels < 0) ? 0 : evt.layerPoint.y - pixels;
    var layer_point_max_y = evt.layerPoint.y + pixels;  //This should test for maximum map point but I don't know how right now.

    var latlng_min = map.layerPointToLatLng(L.point(layer_point_min_x, layer_point_max_y));
    var latlng_max = map.layerPointToLatLng(L.point(layer_point_max_x, layer_point_min_y));

    var turf_poly = turf.polygon([[
        [latlng_min.lng, latlng_min.lat],
        [latlng_min.lng, latlng_max.lat],
        [latlng_max.lng, latlng_max.lat],
        [latlng_max.lng, latlng_min.lat],
        [latlng_min.lng, latlng_min.lat]
    ]]);

    return turf_poly;

};

var hasProp = function (obj, prop) {
    return Object.prototype.hasOwnProperty.call(obj, prop);
}