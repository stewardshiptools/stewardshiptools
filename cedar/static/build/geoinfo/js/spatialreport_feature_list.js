(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

// This is where you'd setup an item, or a row.

var Feature = React.createClass({
    displayName: 'Feature',

    render: function render() {
        var columnNodes = [];
        var distance = $.isNumeric(this.props.data.distance.value) ? this.props.data.distance.value + " " + this.props.data.distance.unit : this.props.data.distance.value;

        var modal_id = this.props.data.id + this.props.data.layer.url.replace(/\/$/, '').replace(/\//g, '-');
        var modal_content = [];
        $.each(this.props.data.data, function (key, value) {
            modal_content.push(React.createElement('span', { key: modal_id + '-' + key }, React.createElement('strong', null, key, ':'), ' ', value, React.createElement('br', null)));
        });

        columnNodes.push(React.createElement('td', { className: 'extra-tight-table-row', key: this.props.data.name + "-data" }, React.createElement('a', { className: 'tight-button waves-effect waves-light btn-flat modal-trigger', href: '#' + modal_id }, 'Detail'), React.createElement('div', { key: modal_id, id: modal_id, className: 'modal' }, React.createElement('div', { className: 'modal-content' }, modal_content), React.createElement('div', { className: 'modal-footer' }, React.createElement('a', { href: '#!', className: 'modal-action modal-close waves-effect waves-green btn-flat' }, 'Close')))));
        columnNodes.push(React.createElement('td', { className: 'extra-tight-table-row', key: this.props.data.name }, React.createElement('a', { href: this.props.data.url }, this.props.data.name)));
        columnNodes.push(React.createElement('td', { className: 'extra-tight-table-row', key: this.props.data.layer.id }, React.createElement('a', {
            href: this.props.data.layer.url }, this.props.data.layer.name)));
        columnNodes.push(React.createElement('td', { className: 'extra-tight-table-row', key: this.props.data.name + "-distance" }, distance));

        return React.createElement('tr', { className: this.props.stripe_classes, style: this.props.style }, columnNodes);
    }
});

// This is where to setup any list wrappers, like tables.
var FeatureList = React.createClass({
    displayName: 'FeatureList',

    render: function render() {
        var headerNodes = [];
        if (this.props.data[0]) {
            headerNodes.push(React.createElement('th', { key: 'data', 'data-field': 'data' }, '\xA0'));
            headerNodes.push(React.createElement('th', { key: 'name', 'data-field': 'name' }, 'Name'));
            headerNodes.push(React.createElement('th', { key: 'layer', 'data-field': 'layer' }, 'Layer'));
            headerNodes.push(React.createElement('th', { key: 'distance', 'data-field': 'distance' }, 'Distance'));
        }

        var data = this.props.data;

        // Sort the results by group then by distance
        data.sort(function (a, b) {
            var a_group = a.sort_group.toLowerCase();
            var b_group = b.sort_group.toLowerCase();
            var group_compare = a_group.localeCompare(b_group);

            if (group_compare !== 0) {
                return group_compare;
            }

            var a_distance = 0;
            if (a.distance.unit !== '') {
                if (a.distance.unit === 'm') {
                    a_distance = a.distance.value;
                } else if (a.distance.unit === 'km') {
                    a_distance = a.distance.value * 1000;
                }
            }

            var b_distance = 0;
            if (b.distance.unit !== '') {
                if (b.distance.unit === 'm') {
                    b_distance = b.distance.value;
                } else if (b.distance.unit === 'km') {
                    b_distance = b.distance.value * 1000;
                }
            }

            return a_distance - b_distance;
        });

        var map_bindings = {
            stripe_classes: '',
            top_border: {}
        };
        var featureNodes = data.map(function (feature, idx, nodes) {
            if (idx !== 0 && feature.sort_group !== nodes[idx - 1].sort_group) {
                map_bindings.top_border = {
                    borderTop: '#666666 1px solid' // When changing groups throw in a grey separator
                };

                if (!map_bindings.stripe_classes) {
                    map_bindings.stripe_classes = 'grey lighten-5';
                } else {
                    map_bindings.stripe_classes = '';
                }
            } else {
                map_bindings.top_border = {};
            }

            return React.createElement(Feature, { key: feature.url, data: feature, stripe_classes: map_bindings.stripe_classes, style: map_bindings.top_border });
        }.bind(map_bindings));

        return React.createElement('div', { className: 'featureList' }, React.createElement('table', { className: '' }, React.createElement('thead', null, React.createElement('tr', null, headerNodes)), React.createElement('tbody', null, featureNodes)));
    }
});

var FeaturePager = React.createClass({
    displayName: 'FeaturePager',

    handlePagingEvent: function handlePagingEvent(e) {
        this.handlePaging(e.target.value);
    },
    handlePaging: function handlePaging(page) {
        if (page.target) {
            //this.props.setPage(page.target.value - 1);
            //return;

            page = page.target.value;
        }

        //if ((page < 0) || (page + 1 > this.props.maxPages) || (!$.isNumeric(page))) {
        //    this.componentWillUpdate(false);
        //    return;
        //}
        this.props.setPage(page);
    },
    render: function render() {
        var pages = [];

        if (this.props.currentPage <= 0) {
            pages.push(React.createElement('li', { key: 'first', className: 'disabled' }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'skip_previous'))));
            pages.push(React.createElement('li', { key: 'prev', className: 'disabled' }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'chevron_left'))));
        } else {
            pages.push(React.createElement('li', { key: 'first', onClick: this.handlePaging.bind(this, 0) }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'skip_previous'))));
            pages.push(React.createElement('li', { key: 'prev', onClick: this.handlePaging.bind(this, this.props.currentPage - 1) }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'chevron_left'))));
        }

        var options = [];
        for (var i = 0; i <= this.props.count; i += this.props.pageSize) {
            var page = i / this.props.pageSize + 1;

            options.push(React.createElement('option', { key: i, value: page - 1 }, page));
        }
        pages.push(React.createElement('li', { key: 'pager_select_li', className: 'intput-field' }, React.createElement('select', { key: 'pager_select', className: 'browser-default', value: this.props.currentPage, onChange: this.handlePagingEvent, style: { width: 'auto', display: 'inline' } }, options)));
        pages.push(React.createElement('li', { key: 'pager-text', className: 'input-field' }, 'out of ', this.props.maxPages));

        if (this.props.currentPage >= this.props.maxPages - 1) {
            pages.push(React.createElement('li', { key: 'next', className: 'disabled' }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'chevron_right'))));
            pages.push(React.createElement('li', { key: 'last', className: 'disabled' }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'skip_next'))));
        } else {
            pages.push(React.createElement('li', { key: 'next', onClick: this.handlePaging.bind(this, this.props.currentPage + 1) }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'chevron_right'))));
            pages.push(React.createElement('li', { key: 'last', onClick: this.handlePaging.bind(this, this.props.maxPages - 1) }, React.createElement('a', { href: '#!' }, React.createElement('i', { className: 'material-icons' }, 'skip_next'))));
        }

        return React.createElement('div', { className: 'row' }, React.createElement('div', { className: 'center' }, React.createElement('ul', { className: 'pagination' }, pages)));
    }
});

var FeatureSearch = React.createClass({
    displayName: 'FeatureSearch',

    handleSearch: function handleSearch(e) {
        this.props.handleSearch(e.target.value);
    },
    render: function render() {
        return React.createElement('div', { className: 'row' }, React.createElement('div', { className: 'input-field col s12 m8 l4' }, React.createElement('i', { className: 'material-icons prefix' }, 'search'), React.createElement('input', { type: 'text', id: 'search_box', onChange: this.handleSearch }), React.createElement('label', { htmlFor: 'search_box' }, 'Filter')));
    }
});

var FeatureBox = React.createClass({
    displayName: 'FeatureBox',

    getInitialState: function getInitialState() {
        return {
            pageSize: 20,
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            data: []
        };
    },
    loadFeatureData: function loadFeatureData() {

        var results_list = [];
        var results_count = 0;
        var num_report_on_layers = 0;

        var urls_processed = 0;

        // Loop through each item passed into the component.
        // Each item contains info about the item, the layer, and the ajax urls (point, line, and polygon)
        for (var i = 0; i < this.props.items.length; i++) {
            console.log("report this?:", this);
            var item = this.props.items[i];

            if (!item.report_item) {
                num_report_on_layers++;
                continue;
            }

            // The urls dictionary always contains 'point', 'line', and 'polygon'
            // as_geojson=1 is missing by default since it's easy to add our self later.
            for (var shape_type in item.urls) {
                var url = item.urls[shape_type];

                var query_start = '?';
                if (url.split('?').length > 1) {
                    query_start = '&';
                }

                // I'm somewhat worried about the idea of several ajax calls altering the results_list array at the same
                // time, but so far it seems to be working just fine...
                $.ajax({
                    url: url + query_start + 'search=' + this.state.search,
                    dataType: 'json',
                    cache: false,
                    beforeSend: function (xhr, settings) {
                        show_report_running(true); // keep showing, that's cool.
                    }.bind(this),
                    success: function (data) {
                        var results = data.results || data;
                        results_count += results.length;

                        // If there's no results, just directly set the data to the current ajax result.
                        if (results_list.length == 0) {
                            results_list = results;
                        } else {
                            $.merge(results_list, results);
                        }

                        // Set the results count on the detail page...
                        $('#spatialreport-result-count').text(results_count);

                        this.setState({
                            data: results_list,
                            count: results_count,
                            maxPages: 1
                        });
                    }.bind(this),
                    error: function (xhr, status, err) {
                        console.error(this.props.url, status, err.toString());
                    }.bind(this),
                    complete: function (xhr, status) {
                        console.log("layer reporting complete for url:", url, $.active, " remaining ajax calls.");

                        // if ($.active == 0) {
                        //     show_report_running(false);
                        // }
                        // $('.modal-trigger').leanModal();


                        // Check if we're done with the spinner... (this should be deprecated
                        if (++urls_processed == (this.props.items.length - num_report_on_layers) * 3) {
                            // Subtract one because one of the items is the report_on layer which we don't care about.
                            $('.modal-trigger').leanModal(); // Also a good time to initialize modals...
                        }
                    }.bind(this)
                });
            }
        }
    },
    componentDidMount: function componentDidMount() {
        this.loadFeatureData();
        //$('.modal-trigger').leanModal();
    },
    handleSearch: function handleSearch(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadFeatureData);
    },
    setPage: function setPage(page) {
        this.setState({
            currentPage: page
        }, this.loadFeatureData);
    },
    render: function render() {
        var pager = "";
        if (this.props.showPager) {
            pager = React.createElement(FeaturePager, {
                currentPage: this.state.currentPage,
                maxPages: this.state.maxPages,
                pageSize: this.state.pageSize,
                count: this.state.count,
                setPage: this.setPage
            });
        }

        var search = "";
        if (this.props.showSearch) {
            search = React.createElement(FeatureSearch, { handleSearch: this.handleSearch });
        }

        return React.createElement('div', { className: 'featureBox' }, React.createElement(FeatureList, { data: this.state.data }));
    }
});

ReactDOM.render(React.createElement(FeatureBox, { items: spatialreports_items,
    showPager: spatialreports_feature_list_show_pager,
    showSearch: spatialreports_feature_list_show_search }), document.getElementById(spatialreports_feature_list_attach_id));

function show_report_running(toggle) {
    var spinner = $('.progress');
    var little_spinner = $("#little-spinner");
    var reporting_complete_check = $("#reporting_complete");

    if (toggle === true) {
        spinner.css('visibility', 'visible');
        little_spinner.show();
        reporting_complete_check.hide();
    } else {
        spinner.css('visibility', 'hidden');
        little_spinner.hide();
        reporting_complete_check.show();
    }
}

// Whenever an Ajax request completes, jQuery checks whether there are any other
// outstanding Ajax requests. If none remain, jQuery triggers the ajaxStop event.
$(document).ajaxStop(function () {
    show_report_running(false);
});

},{}]},{},[1]);
