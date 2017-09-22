(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
GridSettings = React.createClass({
    displayName: "GridSettings",

    getDefaultProps: function () {
        return {
            "columns": [],
            "columnMetadata": [],
            "selectedColumns": [],
            "settingsText": "",
            "maxRowsText": "",
            "resultsPerPage": 0,
            "enableToggleCustom": false,
            "useCustomComponent": false,
            "useGriddleStyles": true,
            "toggleCustomComponent": function () {}
        };
    },
    setPageSize: function (event) {
        var value = parseInt(event.target.value, 10);
        this.props.setPageSize(value);
    },
    handleChange: function (event) {
        console.log("change:", event);
        var columnName = event.target.dataset ? event.target.dataset.name : event.target.getAttribute('data-name');
        if (event.target.checked === true && includes(this.props.selectedColumns, columnName) === false) {
            this.props.selectedColumns.push(columnName);
            this.props.setColumns(this.props.selectedColumns);
        } else {
            /* redraw with the selected columns minus the one just unchecked */
            this.props.setColumns(without(this.props.selectedColumns, columnName));
        }
    },
    render: function () {
        var that = this;

        var nodes = [];
        //don't show column selector if we're on a custom component
        if (that.props.useCustomComponent === false) {
            nodes = this.props.columns.map(function (col, index) {
                var checked = includes(that.props.selectedColumns, col);
                //check column metadata -- if this one is locked make it disabled and don't put an onChange event
                var meta = find(that.props.columnMetadata, { columnName: col });
                var displayName = col;

                if (typeof meta !== "undefined" && typeof meta.displayName !== "undefined" && meta.displayName != null) {
                    displayName = meta.displayName;
                }

                if (typeof meta !== "undefined" && meta != null && meta.locked) {
                    return React.createElement(
                        "div",
                        { className: "column checkbox" },
                        React.createElement(
                            "label",
                            null,
                            React.createElement("input", { type: "checkbox", disabled: true, name: "check", checked: checked,
                                "data-name": col }),
                            displayName
                        )
                    );
                } else if (typeof meta !== "undefined" && meta != null && typeof meta.visible !== "undefined" && meta.visible === false) {
                    return null;
                }
                return React.createElement(
                    "div",
                    { className: "griddle-column-selection checkbox", key: col,
                        style: that.props.useGriddleStyles ? { "float": "left", width: "20%" } : null },
                    React.createElement(
                        "label",
                        null,
                        React.createElement("input", { type: "checkbox", name: "check",
                            onChange: that.handleChange,
                            checked: checked,
                            "data-name": col }),
                        displayName
                    )
                );
            });
        }

        var toggleCustom = that.props.enableToggleCustom ? React.createElement(
            "div",
            { className: "form-group" },
            React.createElement(
                "label",
                { htmlFor: "maxRows" },
                React.createElement("input", { type: "checkbox", checked: this.props.useCustomComponent,
                    onChange: this.props.toggleCustomComponent }),
                " ",
                this.props.enableCustomFormatText
            )
        ) : "";

        var setPageSize = this.props.showSetPageSize ? React.createElement(
            "div",
            null,
            React.createElement(
                "label",
                { htmlFor: "maxRows" },
                this.props.maxRowsText,
                ":",
                React.createElement(
                    "select",
                    { onChange: this.setPageSize, value: this.props.resultsPerPage },
                    React.createElement(
                        "option",
                        { value: "5" },
                        "5"
                    ),
                    React.createElement(
                        "option",
                        { value: "10" },
                        "10"
                    ),
                    React.createElement(
                        "option",
                        { value: "25" },
                        "25"
                    ),
                    React.createElement(
                        "option",
                        { value: "50" },
                        "50"
                    ),
                    React.createElement(
                        "option",
                        { value: "100" },
                        "100"
                    )
                )
            )
        ) : "";

        return React.createElement(
            "div",
            { className: "griddle-settings",
                style: this.props.useGriddleStyles ? { backgroundColor: "#FFF", border: "1px solid #DDD", color: "#222", padding: "10px", marginBottom: "10px" } : null },
            React.createElement(
                "h6",
                null,
                this.props.settingsText
            ),
            React.createElement(
                "div",
                { className: "griddle-columns",
                    style: this.props.useGriddleStyles ? { clear: "both", display: "table", width: "100%", borderBottom: "1px solid #EDEDED", marginBottom: "10px" } : null },
                nodes
            ),
            setPageSize,
            toggleCustom
        );
    }
});

var customFilterComponent = React.createClass({
    displayName: "customFilterComponent",

    getDefaultProps: function () {
        return {
            "query": ""
        };
    },

    searchChange: function (value) {
        console.log("search change:", value);
        value = encodeURIComponent(value);
        this.props.query = value;
        this.props.changeFilter(value);
    },

    render: function () {
        return React.createElement(
            "div",
            { className: "filter-container" },
            React.createElement("input", { type: "text",
                name: "search",
                placeholder: "Filter..." })
        );
    },
    componentDidMount: function () {
        var search_box = $(ReactDOM.findDOMNode(this)).find('input');
        var search_handle_proxy = $.proxy(this.searchChange, this); //holds on to react component's "this" context.
        $(search_box).typeWatch({
            wait: 550,
            callback: function (value) {
                search_handle_proxy(value);
            },
            captureLength: 1,
            allowSubmit: true
        });
    }
});

var customSpeciesObservationPager = React.createClass({
    displayName: "customSpeciesObservationPager",

    getDefaultProps: function () {
        return {
            "maxPage": 0,
            "nextText": "",
            "previousText": "",
            "currentPage": 0
        };
    },
    pageChange: function (event) {
        this.props.setPage(parseInt(event.target.value));
    },
    render: function () {
        var prev = "";
        var next = "";
        var page;

        if (this.props.currentPage > 0) {
            prev = React.createElement(
                "button",
                { type: "button", className: "btn-flat waves-grey text-grey", onClick: this.props.previous },
                "Previous"
            );
        }

        if (this.props.currentPage + 1 < this.props.maxPage) {
            next = React.createElement(
                "button",
                { type: "button", className: "btn-flat waves-grey text-grey", onClick: this.props.next },
                "Next"
            );
        }

        var options = [];
        for (var i = 0; i < this.props.maxPage; i++) {
            options.push(React.createElement(
                "option",
                { key: i, value: i },
                i + 1
            ));
        }

        return React.createElement(
            "div",
            null,
            React.createElement(
                "div",
                { className: "griddle-previous" },
                prev
            ),
            React.createElement(
                "div",
                { className: "griddle-page" },
                React.createElement(
                    "select",
                    { className: "browser-default", value: this.props.currentPage, onChange: this.pageChange },
                    options
                ),
                " / ",
                this.props.maxPage
            ),
            React.createElement(
                "div",
                { className: "griddle-next" },
                next
            )
        );
    }
});

var SpeciesObservationLink = React.createClass({
    displayName: "SpeciesObservationLink",

    render: function () {
        return React.createElement(
            "a",
            { href: this.props.rowData.url },
            "VIEW"
        );
    }
});

var SpeciesObservationsComponent = React.createClass({
    displayName: "SpeciesObservationsComponent",

    getInitialState: function () {
        var initial = { "results": [],
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
    componentWillMount: function () {},
    componentDidMount: function () {
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
                    var columns = localStorage.getItem('speciescolumns').split(",");
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
                    localStorage.setItem('speciescolumns', columns);
                });
            }), 300);
        });
    },
    loadUpdatesFromServer: function () {
        var spinner = $('.progress');
        spinner.css('visibility', 'visible');

        var sort = this.state.externalSortColumn;

        if (sort && !this.state.externalSortAscending) {
            sort = "-" + sort;
        }

        $.ajax({
            url: species_ajax_url + "?" + extra_query + "&limit=" + this.state.externalResultsPerPage + "&offset=" + this.state.currentPage * this.state.externalResultsPerPage + "&ordering=" + sort + "&search=" + this.state.search,
            dataType: 'json',
            cache: false,
            success: function (data) {
                // Craft a custom results array to avoid conflicts between DRF and Griddle
                var results = [];
                // Would be nice if the results came flat so we don't have to do this...
                $.each(data.results, function (key, r) {
                    var url = r.url;
                    var id = r.id;
                    var species = r.species ? r.species.description : '';
                    var use = r.use ? r.use.description : '';
                    var time_frame_start = r.time_frame_start ? r.time_frame_start.description : '';
                    var time_frame_end = r.time_frame_end ? r.time_frame_end.description : '';
                    var harvest_method = r.harvest_method ? r.harvest_method.name : '';
                    var fishing_method = r.fishing_method ? r.fishing_method.description : '';
                    var eco_value = r.ecological_value ? r.ecological_value.description : '';
                    var species_theme = r.species_theme ? r.species_theme.name : '';
                    var temporal_trend = r.temporal_trend ? r.temporal_trend.description : '';
                    var gazetted_place_name = r.gazetted_place_name || '';
                    var first_nations_place_name = r.first_nations_place_name || '';
                    var seasons = r.seasons ? r.seasons.join(', ') : '';
                    var participant_community = r.participant_community || '';

                    // The key still matches the keys of the results, but the list here is flat for now, because
                    // Griddle doesn't like it when multiple columns share child keys.
                    results.push({
                        "url": url,
                        "id": id,
                        "species": species,
                        "use": use,
                        "time_frame_start": time_frame_start,
                        "time_frame_end": time_frame_end,
                        "harvest_method": harvest_method,
                        "fishing_method": fishing_method,
                        "ecological_value": eco_value,
                        "species_theme": species_theme,
                        "temporal_trend": temporal_trend,
                        "gazetted_place_name": gazetted_place_name,
                        "first_nations_place_name": first_nations_place_name,
                        "seasons": seasons,
                        "participant_community": participant_community
                    });
                });

                $(document).trigger('SpeciesObservationsUpdated', [data.results]);

                this.setState({
                    results: results,
                    maxPages: Math.ceil(data.count / this.state.externalResultsPerPage)
                });
                spinner.css('visibility', 'hidden');
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(species_ajax_url, status, err.toString());
            }.bind(this)
        });
    },
    //what page is currently viewed
    setPage: function (index) {
        //This should interact with the data source to get the page at the given index
        index = index > this.state.maxPages ? this.state.maxPages : index < 1 ? 0 : index;
        this.setState({
            currentPage: index
        }, this.loadUpdatesFromServer);
    },
    //this changes whether data is sorted in ascending or descending order
    changeSort: function (sort, sortAscending) {
        this.setState({
            "currentPage": 0,
            "externalSortColumn": sort,
            "externalSortAscending": sortAscending
        }, this.loadUpdatesFromServer);
    },
    //this method handles the filtering of the data
    setFilter: function (filter) {
        this.setState({
            "currentPage": 0,
            "search": filter
        }, this.loadUpdatesFromServer);
    },
    //this method handles determining the page size
    setPageSize: function (size) {
        this.setState({
            "currentPage": 0,
            "externalResultsPerPage": size
        }, this.loadUpdatesFromServer);
    },
    render: function () {
        var default_columns = ["id", "species", "species_theme", "fishing_method", "harvest_method", "ecological_value", "gazetted_place_name", "first_nations_place_name", "use"];

        var columns_are_good = false;

        //Read column names from local storage if present:
        if (localStorage.getItem('speciescolumns')) {
            var columns_local_storage = localStorage.getItem('speciescolumns').split(",");

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
        localStorage.setItem('speciescolumns', columns);

        var columnMetadata = [{
            "columnName": "id",
            "locked": true,
            "visible": true,
            "displayName": "",
            "customComponent": SpeciesObservationLink // A custom component to render this field as a link.
        }, {
            "columnName": "species",
            "displayName": "Species"
        }, {
            "columnName": "species_theme",
            "displayName": "Species theme"
        }, {
            "columnName": "fishing_method",
            "displayName": "Fishing method"
        }, {
            "columnName": "harvest_method",
            "displayName": "Harvest method"
        }, {
            "columnName": "ecological_value",
            "displayName": "Ecological value"
        }, {
            "columnName": "temporal_trend",
            "displayName": "Temporal Trend"
        }, {
            "columnName": "gazetted_place_name",
            "displayName": "Gazetted place name"
        }, {
            "columnName": "first_nations_place_name",
            "displayName": "First nations place name" // Almost always empty.
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
            options.push(React.createElement(
                "option",
                { key: i, value: results_on_page_options[i] },
                results_on_page_options[i]
            ));
        }

        var results_on_page_selector = React.createElement(
            "div",
            { key: "results_on_page_selector", className: "input-field col results-on-page-selector" },
            React.createElement(
                "select",
                { value: this.state.externalResultsPerPage, onChange: this.setPageSize },
                options
            ),
            React.createElement(
                "label",
                null,
                "Results per page"
            )
        );

        return React.createElement(
            "div",
            { className: "row" },
            results_on_page_selector,
            React.createElement(
                "div",
                { className: "col s12" },
                React.createElement(Griddle, { useExternal: true, externalSetPage: this.setPage,
                    columns: columns, columnMetadata: columnMetadata,
                    externalChangeSort: this.changeSort, externalSetFilter: this.setFilter,
                    externalSetPageSize: this.setPageSize, externalMaxPage: this.state.maxPages,
                    externalCurrentPage: this.state.currentPage, results: this.state.results,
                    resultsPerPage: this.state.externalResultsPerPage,
                    externalSortColumn: this.state.externalSortColumn,
                    externalSortAscending: this.state.externalSortAscending,
                    showFilter: true, showSettings: true, useGriddleStyles: false,
                    useCustomPagerComponent: true, customPagerComponent: customSpeciesObservationPager,
                    useCustomFilterComponent: true, customFilterComponent: customFilterComponent,
                    settingsToggleClassName: "btn-flat waves-grey text-grey"
                })
            )
        );
    }
});

ReactDOM.render(React.createElement(SpeciesObservationsComponent, null), document.getElementById(table_id));

},{}]},{},[1]);
