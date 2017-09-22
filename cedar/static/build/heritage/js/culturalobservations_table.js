(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var customFilterComponent = React.createClass({
    displayName: "customFilterComponent",

    getDefaultProps: function getDefaultProps() {
        return {
            "query": ""
        };
    },

    searchChange: function searchChange(value) {
        value = encodeURIComponent(value);
        this.props.query = value;
        this.props.changeFilter(value);
    },

    render: function render() {
        return React.createElement("div", { className: "filter-container" }, React.createElement("input", { type: "text",
            name: "search",
            placeholder: "Filter..." }));
    },
    componentDidMount: function componentDidMount() {
        var search_box = $(ReactDOM.findDOMNode(this)).find('input');
        var search_handle_proxy = $.proxy(this.searchChange, this); //holds on to react component's "this" context.
        $(search_box).typeWatch({
            wait: 550,
            callback: function callback(value) {
                search_handle_proxy(value);
            },
            captureLength: 1,
            allowSubmit: true
        });
    }
});

var customCulturalObservationPager = React.createClass({
    displayName: "customCulturalObservationPager",

    getDefaultProps: function getDefaultProps() {
        return {
            "maxPage": 0,
            "nextText": "",
            "previousText": "",
            "currentPage": 0
        };
    },
    pageChange: function pageChange(event) {
        this.props.setPage(parseInt(event.target.value));
    },
    render: function render() {
        var prev = "";
        var next = "";
        var page;

        if (this.props.currentPage > 0) {
            prev = React.createElement("button", { type: "button", className: "waves-effect waves-dark btn-flat white", onClick: this.props.previous }, "Previous");
        }

        if (this.props.currentPage + 1 < this.props.maxPage) {
            next = React.createElement("button", { type: "button", className: "waves-effect waves-dark btn-flat white", onClick: this.props.next }, "Next");
        }

        var options = [];
        for (var i = 0; i < this.props.maxPage; i++) {
            options.push(React.createElement("option", { key: i, value: i }, i + 1));
        }

        return React.createElement("div", null, React.createElement("div", { className: "griddle-previous" }, prev), React.createElement("div", { className: "griddle-page" }, React.createElement("select", { className: "browser-default", value: this.props.currentPage, onChange: this.pageChange }, options), " / ", this.props.maxPage), React.createElement("div", { className: "griddle-next" }, next));
    }
});

var CulturalObservationLink = React.createClass({
    displayName: "CulturalObservationLink",

    render: function render() {
        return React.createElement("a", { href: this.props.rowData.url }, "VIEW");
    }
});

var CulturalObservationsComponent = React.createClass({
    displayName: "CulturalObservationsComponent",

    getInitialState: function getInitialState() {
        var initial = {
            "results": [],
            "currentPage": 0,
            "maxPages": 0,
            "search": '',
            "externalResultsPerPage": 10,
            "externalSortColumn": '',
            "externalSortAscending": true
        };

        return initial;
    },
    //general lifecycle methods
    componentWillMount: function componentWillMount() {},
    componentDidMount: function componentDidMount() {
        this.loadUpdatesFromServer();
        $(ReactDOM.findDOMNode(this)).find('div.results-on-page-selector select').material_select();

        $(ReactDOM.findDOMNode(this)).find('div.results-on-page-selector select').on('change', function (e) {
            this.setPageSize(e.target.value);
        }.bind(this));

        //Attach click listener to settings, that then looks for the settings dialog:
        $(ReactDOM.findDOMNode(this)).find(".griddle-settings-toggle > button").on('click', function (evt) {
            var settings_button = evt.currentTarget;

            // need to get checkbox values, but we have to give it time to render before trying to attach click listeners.
            setTimeout($.proxy(function () {
                var columnboxes = $(settings_button).parent().parent().next().find("div.griddle-column-selection > label > input[type='checkbox']");
                $(columnboxes).on('change', function (evt) {
                    var col_name = $(this).attr('data-name');
                    var columns = localStorage.getItem('culturalcolumns').split(",");
                    var idx = columns.indexOf(col_name);
                    if (evt.target.checked) {
                        //Make sure it's in the columns list:
                        if (idx === -1) {
                            columns.push(col_name);
                        }
                    } else {
                        if (idx > -1) {
                            columns.splice(idx, 1);
                        }
                    }
                    localStorage.setItem('culturalcolumns', columns);
                });
            }), 300);
        });
    },
    loadUpdatesFromServer: function loadUpdatesFromServer() {
        var spinner = $('.progress');
        spinner.css('visibility', 'visible');

        var sort = this.state.externalSortColumn;

        if (sort && !this.state.externalSortAscending) {
            sort = "-" + sort;
        }

        $.ajax({
            url: cultural_ajax_url + "?" + extra_query + "&limit=" + this.state.externalResultsPerPage + "&offset=" + this.state.currentPage * this.state.externalResultsPerPage + "&ordering=" + sort + "&search=" + this.state.search,
            dataType: 'json',
            cache: false,
            success: function (data) {
                // Craft a custom results array to avoid conflicts between DRF and Griddle
                var results = [];
                // Would be nice if the results came flat so we don't have to do this...
                $.each(data.results, function (key, r) {
                    // console.log("r:", r);

                    // The key still matches the keys of the results, but the list here is flat for now, because
                    // Griddle doesn't like it when multiple columns share child keys.
                    results.push({
                        "url": r.url,
                        "id": r.id,
                        "gazetted_place_name": r.gazetted_place_name,
                        "first_nations_place_name": r.first_nations_place_name,
                        "local_place_name": r.local_place_name,
                        "cultural_feature": r.cultural_feature,
                        "ecological_feature": r.ecological_feature,
                        "industrial_feature": r.industrial_feature,
                        "management_feature": r.management_feature,
                        "value_feature": r.value_feature || '', // Nearly always empty...
                        "travel_mode": r.travel_mode || '',
                        "target_species": r.target_species || '',
                        "secondary_species": r.secondary_species || '',
                        "seasons": r.seasons ? r.seasons.join(', ') : '',
                        "use": r.use ? r.use.description : '',
                        "time_frame_start": r.time_frame_start ? r.time_frame_start.description : '',
                        "time_frame_end": r.time_frame_end ? r.time_frame_end.description : '',
                        "participant_community": r.participant_community || ''
                    });
                });

                var counter;
                if ($("#cultural-records-result-count").length) {
                    counter = $("#cultural-records-result-count");
                } else {
                    counter = $(ReactDOM.findDOMNode(this)).find('div#cultural-inline-results-count');
                    $(ReactDOM.findDOMNode(this)).find('div#cultural-inline-results-count-prefix').text("# Results: ");
                }

                counter.text(data.count);

                $(document).trigger('CulturalObservationsUpdated', [data.results]);

                this.setState({
                    results: results,
                    maxPages: Math.ceil(data.count / this.state.externalResultsPerPage)
                });
                spinner.css('visibility', 'hidden');
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(cultural_ajax_url, status, err.toString());
            }.bind(this)
        });
    },
    //what page is currently viewed
    setPage: function setPage(index) {
        //This should interact with the data source to get the page at the given index
        index = index > this.state.maxPages ? this.state.maxPages : index < 1 ? 0 : index;
        this.setState({
            currentPage: index
        }, this.loadUpdatesFromServer);
    },
    //this changes whether data is sorted in ascending or descending order
    changeSort: function changeSort(sort, sortAscending) {
        this.setState({
            "currentPage": 0,
            "externalSortColumn": sort,
            "externalSortAscending": sortAscending
        }, this.loadUpdatesFromServer);
    },
    //this method handles the filtering of the data
    setFilter: function setFilter(filter) {
        this.setState({
            "currentPage": 0,
            "search": filter
        }, this.loadUpdatesFromServer);
    },
    //this method handles determining the page size
    setPageSize: function setPageSize(size) {
        this.setState({
            "currentPage": 0,
            "externalResultsPerPage": size
        }, this.loadUpdatesFromServer);
    },
    render: function render() {
        var default_columns = ["id", "cultural_feature", "gazetted_place_name", "first_nations_place_name", "ecological_feature", "industrial_feature", "management_feature", "value_feature", "travel_mode"];

        var columns_are_good = false;

        //Read column names from local storage if present:
        if (localStorage.getItem('culturalcolumns')) {
            var columns_local_storage = localStorage.getItem('culturalcolumns').split(",");

            // make sure there is at least one column that is a default, otherwise, weirdness:
            for (var i in columns_local_storage) {
                var idx = default_columns.indexOf(columns_local_storage[i]);
                if (idx > -1) {
                    columns_are_good = true;
                    break;
                }
            }
        }

        if (columns_are_good) {
            var columns = columns_local_storage;
        } else {
            console.log("huh, something happened to the columns, fall back to default:", columns_local_storage);
            var columns = default_columns;
        }
        localStorage.setItem('culturalcolumns', columns);

        var columnMetadata = [{
            "columnName": "id",
            "locked": true,
            "visible": true,
            "displayName": "",
            "customComponent": CulturalObservationLink // A custom component to render this field as a link.
        }, {
            "columnName": "cultural_feature",
            "displayName": "Cultural Feature"
        }, {
            "columnName": "gazetted_place_name",
            "displayName": "Gazetted Place Name"
        }, {
            "columnName": "first_nations_place_name",
            "displayName": "Haida Place Name*"
        }, {
            "columnName": "local_place_name",
            "displayName": "Local Place Name"
        }, {
            "columnName": "ecological_feature",
            "displayName": "Ecological Feature"
        }, {
            "columnName": "industrial_feature",
            "displayName": "Industrial Feature"
        }, {
            "columnName": "management_feature",
            "displayName": "Management Feature"
        }, {
            "columnName": "value_feature",
            "displayName": "Value Feature"
        }, {
            "columnName": "travel_mode",
            "displayName": "Travel Mode"
        }, {
            "columnName": "target_species",
            "displayName": "Target Species"
        }, {
            "columnName": "secondary_species",
            "displayName": "Secondary Species"
        }, {
            "columnName": "seasons",
            "displayName": "Seasons"
        }, {
            "columnName": "use",
            "displayName": "Use"
        }, {
            "columnName": "time_frame_start",
            "displayName": "Time frame start"
        }, {
            "columnName": "time_frame_end",
            "displayName": "Time frame end"
        }, {
            "columnName": "participant_community",
            "displayName": "Participant community"
        }];

        var results_on_page_options = [5, 10, 25, 50, 100, 500, 1000];
        var options = [];

        for (var i = 0; i < results_on_page_options.length; i++) {
            options.push(React.createElement("option", { key: i, value: results_on_page_options[i] }, results_on_page_options[i]));
        }

        var results_on_page_selector = React.createElement("div", { key: "results_on_page_selector", className: "input-field col results-on-page-selector" }, React.createElement("select", { value: this.state.externalResultsPerPage, onChange: this.setPageSize }, options), React.createElement("label", null, "Results per page"));

        return React.createElement("div", null, React.createElement("div", { className: "extra-tight-table-row teal-text text-darken-2 col s12" }, "Note: The Cultural Records table and map are linked. Filter the table and the map will update correspondingly."), React.createElement("div", { className: "extra-tight-table-row teal-text text-darken-2 col s12" }, React.createElement("em", null, "*The Haida Place Names column may contain errors.")), React.createElement("div", { className: "extra-tight-table-row grey-text text-darken-2 col s12", style: { fontWeight: "bold" } }, React.createElement("div", { id: "cultural-inline-results-count-prefix", style: { display: "inline" } }), React.createElement("div", { id: "cultural-inline-results-count", style: { display: "inline" } })), React.createElement("div", { className: "row" }, results_on_page_selector, React.createElement("div", { className: "col s12" }, React.createElement(Griddle, { useExternal: true, externalSetPage: this.setPage,
            columns: columns, columnMetadata: columnMetadata,
            externalChangeSort: this.changeSort, externalSetFilter: this.setFilter,
            externalSetPageSize: this.setPageSize, externalMaxPage: this.state.maxPages,
            externalCurrentPage: this.state.currentPage, results: this.state.results,
            resultsPerPage: this.state.externalResultsPerPage,
            externalSortColumn: this.state.externalSortColumn,
            externalSortAscending: this.state.externalSortAscending,
            showFilter: true, showSettings: true, useGriddleStyles: false,
            useCustomPagerComponent: true, customPagerComponent: customCulturalObservationPager,
            useCustomFilterComponent: true, customFilterComponent: customFilterComponent,
            settingsToggleClassName: "waves-effect waves-dark btn-flat white"
        }))));
    }
});

ReactDOM.render(React.createElement(CulturalObservationsComponent, null), document.getElementById(table_id));

},{}]},{},[1]);
