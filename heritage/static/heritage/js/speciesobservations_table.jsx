GridSettings = React.createClass({
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
            "toggleCustomComponent": function () {
            }
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
                var meta = find(that.props.columnMetadata, {columnName: col});
                var displayName = col;

                if (typeof meta !== "undefined" && typeof meta.displayName !== "undefined" && meta.displayName != null) {
                    displayName = meta.displayName;
                }

                if (typeof meta !== "undefined" && meta != null && meta.locked) {
                    return <div className="column checkbox"><label><input type="checkbox" disabled name="check" checked={checked}
                                                                          data-name={col}/>{displayName}</label></div>
                } else if (typeof meta !== "undefined" && meta != null && typeof meta.visible !== "undefined" && meta.visible === false) {
                    return null;
                }
                return <div className="griddle-column-selection checkbox" key={col}
                            style={that.props.useGriddleStyles ? { "float": "left", width: "20%"} : null }><label><input type="checkbox" name="check"
                                                                                                                         onChange={that.handleChange}
                                                                                                                         checked={checked}
                                                                                                                         data-name={col}/>{displayName}
                </label></div>
            });
        }

        var toggleCustom = that.props.enableToggleCustom ?
            (<div className="form-group">
                <label htmlFor="maxRows"><input type="checkbox" checked={this.props.useCustomComponent}
                                                onChange={this.props.toggleCustomComponent}/> {this.props.enableCustomFormatText}</label>
            </div>)
            : "";

        var setPageSize = this.props.showSetPageSize ? (<div>
            <label htmlFor="maxRows">{this.props.maxRowsText}:
                <select onChange={this.setPageSize} value={this.props.resultsPerPage}>
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                </select>
            </label>
        </div>) : "";


        return (<div className="griddle-settings"
                     style={this.props.useGriddleStyles ? { backgroundColor: "#FFF", border: "1px solid #DDD", color: "#222", padding: "10px", marginBottom: "10px"} : null }>
            <h6>{this.props.settingsText}</h6>
            <div className="griddle-columns"
                 style={this.props.useGriddleStyles ? { clear: "both", display: "table", width: "100%", borderBottom: "1px solid #EDEDED", marginBottom: "10px"} : null }>
                {nodes}
            </div>
            {setPageSize}
            {toggleCustom}
        </div>);
    }
});


var customFilterComponent = React.createClass({
    getDefaultProps: function () {
        return {
            "query": ""
        }
    },

    searchChange: function (value) {
        value = encodeURIComponent(value);
        this.props.query = value;
        // this.props.changeFilter(this.props.query);
        this.props.changeFilter(value);

    },

    render: function () {
        return (
            <div className="filter-container">
                <input type="text"
                       name="search"
                       placeholder="Filter..."/>
            </div>
        )
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
            allowSubmit: true,
        });
    }
});

var customSpeciesObservationPager = React.createClass({
    getDefaultProps: function(){
        return{
            "maxPage": 0,
            "nextText": "",
            "previousText": "",
            "currentPage": 0
        }
    },
    pageChange: function(event){
        this.props.setPage(parseInt(event.target.value));
    },
    render: function() {
        var prev = "";
        var next = "";
        var page;

        if (this.props.currentPage > 0) {
            prev = <button type="button" className="waves-effect waves-dark btn-flat white" onClick={this.props.previous}>Previous</button>;
        }

        if (this.props.currentPage + 1 < this.props.maxPage) {
            next = <button type="button" className="waves-effect waves-dark btn-flat white" onClick={this.props.next}>Next</button>;
        }

        var options = [];
        for(var i = 0; i < this.props.maxPage; i++) {
            options.push(<option key={i} value={i}>{i + 1}</option>);
        }

        return (
            <div>
                <div className="griddle-previous">{prev}</div>
                <div className="griddle-page"><select className="browser-default" value={this.props.currentPage} onChange={this.pageChange}>{options}</select> / {this.props.maxPage}</div>
                <div className="griddle-next">{next}</div>
            </div>
        );
    }
});

var SpeciesObservationLink = React.createClass({
    render: function() {
        return <a href={this.props.rowData.url}>VIEW</a>;
    }
});

var SpeciesObservationsComponent = React.createClass({
    getInitialState: function(){
      var initial = { "results": [],
          "currentPage": 0,
          "maxPages": 0,
          "search": '',
          "externalResultsPerPage": 10,
          "externalSortColumn":'',
          "externalSortAscending":true
      };

      return initial;
    },
    //general lifecycle methods
    componentWillMount: function(){
    },
    componentDidMount: function(){
        this.loadUpdatesFromServer();
        $(ReactDOM.findDOMNode(this)).find('div.results-on-page-selector select').material_select();

        $(ReactDOM.findDOMNode(this)).find('div.results-on-page-selector select').on('change', function(e) {
            this.setPageSize(e.target.value);
        }.bind(this));

        //Attach click listener to settings, that then looks for the settings dialog:
        $(ReactDOM.findDOMNode(this)).find(".griddle-settings-toggle > button")
            .on('click', function (evt) {
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
                        }
                        else {
                            if (idx > -1) {
                                columns.splice(idx, 1);
                            }
                        }
                        localStorage.setItem('speciescolumns', columns);
                    });
                }), 300);
            });
        
    },
    loadUpdatesFromServer: function(){
        var spinner = $('.progress');
        spinner.css('visibility', 'visible');

        var sort = this.state.externalSortColumn;

        if (sort && !this.state.externalSortAscending) {
            sort = "-" + sort;
        }

        $.ajax({
            url: species_ajax_url + "?" + extra_query + "&limit=" + this.state.externalResultsPerPage + "&offset=" + (this.state.currentPage) * this.state.externalResultsPerPage + "&ordering=" + sort + "&search=" + this.state.search,
            dataType: 'json',
            cache: false,
            success: function(data) {
                // Craft a custom results array to avoid conflicts between DRF and Griddle
                var results = [];
                // Would be nice if the results came flat so we don't have to do this...
                $.each(data.results, function(key, r) {
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
                    var local_place_name = r.local_place_name || '';
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
                        "local_place_name": local_place_name,
                        "seasons": seasons,
                        "participant_community": participant_community
                    });
                });

                var counter;
                if ($("#species-records-result-count").length) {
                  counter = $("#species-records-result-count");
                } else {
                  counter = $(ReactDOM.findDOMNode(this)).find('div#species-inline-results-count');
                  $(ReactDOM.findDOMNode(this)).find('div#species-inline-results-count-prefix').text("# Results: ");
                }

                counter.text(data.count);

                $( document ).trigger('SpeciesObservationsUpdated', [data.results]);

                this.setState({
                    results: results,
                    maxPages: Math.ceil(data.count / this.state.externalResultsPerPage)
                });
                spinner.css('visibility', 'hidden');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(species_ajax_url, status, err.toString());
            }.bind(this)
        });
    },
    //what page is currently viewed
    setPage: function(index){
        //This should interact with the data source to get the page at the given index
        index = index > this.state.maxPages ? this.state.maxPages : index < 1 ? 0 : index;
        this.setState({
            currentPage: index
        }, this.loadUpdatesFromServer);
    },
    //this changes whether data is sorted in ascending or descending order
    changeSort: function(sort, sortAscending){
        this.setState({
            "currentPage": 0,
            "externalSortColumn": sort,
            "externalSortAscending": sortAscending
        }, this.loadUpdatesFromServer);
    },
    //this method handles the filtering of the data
    setFilter: function(filter){
        this.setState({
            "currentPage": 0,
            "search": filter
        }, this.loadUpdatesFromServer);
    },
    //this method handles determining the page size
    setPageSize: function(size){
        this.setState({
            "currentPage": 0,
            "externalResultsPerPage": size
        }, this.loadUpdatesFromServer);
    },
    render: function(){
        var default_columns = ["id", "species", "species_theme", "fishing_method", "harvest_method", "ecological_value",
            "gazetted_place_name", "first_nations_place_name", "use"];

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
        }
        else {
            console.log("huh, something happened to the columns, fall back to default:", columns_local_storage);
            var columns = default_columns;
        }
        localStorage.setItem('speciescolumns', columns);

        var columnMetadata = [
            {
                "columnName": "id",
                "locked": true,
                "visible": true,
                "displayName": "",
                "customComponent": SpeciesObservationLink  // A custom component to render this field as a link.
            },
            {
                "columnName": "species",
                "displayName": "Species"
            },
            {
                "columnName": "species_theme",
                "displayName": "Species theme"
            },
            {
                "columnName": "fishing_method",
                "displayName": "Fishing method"
            },
            {
                "columnName": "harvest_method",
                "displayName": "Harvest method"
            },
            {
                "columnName": "ecological_value",
                "displayName": "Ecological value"
            },
            {
                "columnName": "temporal_trend",
                "displayName": "Temporal Trend"
            },
            {
                "columnName": "gazetted_place_name",
                "displayName": "Gazetted place name"
            },
            {
                "columnName": "first_nations_place_name",
                "displayName": "First nations place name"  // Almost always empty.
            },
            {
                "columnName": "local_place_name",
                "displayName": "Local place name"
            },
            {
                "columnName": "seasons",
                "displayName": "Seasons"
            },
            {
                "columnName": "use",
                "displayName": "Use"
            },
            {
                "columnName": "time_frame_start",
                "displayName": "Time frame start"
            },
            {
                "columnName": "time_frame_end",
                "displayName": "Time frame end"
            },
            {
                "columnName": "participant_community",
                "displayName": "Participant community"
            }
        ];

        var results_on_page_options = [5, 10, 25, 50, 100, 500, 1000];
        var options = [];

        for (var i = 0; i < results_on_page_options.length; i++) {
            options.push(
                <option key={i} value={results_on_page_options[i]}>{results_on_page_options[i]}</option>
            );
        }

        var results_on_page_selector = (
            <div key="results_on_page_selector" className="input-field col results-on-page-selector">
                <select value={this.state.externalResultsPerPage} onChange={this.setPageSize}>
                    {options}
                </select>
                <label>Results per page</label>
            </div>
        );

        return (
            <div>
                <div className="extra-tight-table-row teal-text text-darken-2 col s12">Note: The Species Records table and map are linked. Filter the table and the map will update correspondingly.</div>
                <div className="extra-tight-table-row grey-text text-darken-2 col s12" style={{fontWeight: "bold"}}>
                    <div id="species-inline-results-count-prefix" style={{display: "inline"}}></div>
                    <div id="species-inline-results-count" style={{display: "inline"}}></div>
                </div>
                <div className="row">
                    {results_on_page_selector}
                    <div className="col s12">
                        <Griddle useExternal={true} externalSetPage={this.setPage}
                                 columns = {columns} columnMetadata = {columnMetadata}
                                 externalChangeSort={this.changeSort} externalSetFilter={this.setFilter}
                                 externalSetPageSize={this.setPageSize} externalMaxPage={this.state.maxPages}
                                 externalCurrentPage={this.state.currentPage} results={this.state.results}
                                 resultsPerPage={this.state.externalResultsPerPage}
                                 externalSortColumn={this.state.externalSortColumn}
                                 externalSortAscending={this.state.externalSortAscending}
                                 showFilter={true} showSettings={true} useGriddleStyles={false}
                                 useCustomPagerComponent={true} customPagerComponent={customSpeciesObservationPager}
                                 useCustomFilterComponent={true} customFilterComponent={customFilterComponent}
                                 settingsToggleClassName={"waves-effect waves-dark btn-flat white"}
                        />
                    </div>
                </div>
            </div>
        );
    }
});

ReactDOM.render(
    <SpeciesObservationsComponent />,
    document.getElementById(table_id)
);

