// This is where you'd setup an item, or a row.
var Feature = React.createClass({
    render: function() {
        var columnNodes = [];
        var distance = $.isNumeric(this.props.data.distance.value) ? this.props.data.distance.value + " " +
        this.props.data.distance.unit : this.props.data.distance.value;
        
        var modal_id = this.props.data.id + this.props.data.layer.url.replace(/\/$/, '').replace(/\//g, '-');
        var modal_content = [];
        $.each(this.props.data.data, function (key, value) {
            modal_content.push(<span key={modal_id + '-' + key}><strong>{key}:</strong> {value}<br /></span>);
        });

        columnNodes.push(<td className="extra-tight-table-row" key={this.props.data.name + "-data"}>
            <a className="tight-button waves-effect waves-light btn-flat modal-trigger" href={'#' + modal_id}>Detail</a>
            
            <div key={modal_id} id={modal_id} className="modal">
                <div className="modal-content">
                    {modal_content}
                </div>
                <div className="modal-footer">
                    <a href="#!" className="modal-action modal-close waves-effect waves-green btn-flat">Close</a>
                </div>
            </div>
        </td>);
        columnNodes.push(<td className="extra-tight-table-row" key={this.props.data.name}><a href={this.props.data.url}>{this.props.data.name}</a>
        </td>);
        columnNodes.push(<td className="extra-tight-table-row" key={this.props.data.layer.id}><a
            href={this.props.data.layer.url}>{this.props.data.layer.name}</a></td>);
        columnNodes.push(<td className="extra-tight-table-row" key={this.props.data.name + "-distance"}>{distance}</td>);

        return (
            <tr className={this.props.stripe_classes} style={this.props.style} >
                {columnNodes}
            </tr>
        );
    }
});

// This is where to setup any list wrappers, like tables.
var FeatureList = React.createClass({
    render: function() {
        var headerNodes = [];
        if (this.props.data[0]) {
            headerNodes.push(<th key="data" data-field="data">&nbsp;</th>);
            headerNodes.push(<th key="name" data-field="name">Name</th>);
            headerNodes.push(<th key="layer" data-field="layer">Layer</th>);
            headerNodes.push(<th key="distance" data-field="distance">Distance</th>);
        }

        let data = this.props.data;

        // Sort the results by group then by distance
        data.sort(function (a, b) {
            const a_group = a.sort_group.toLowerCase();
            const b_group = b.sort_group.toLowerCase();
            const group_compare = a_group.localeCompare(b_group);

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


        let map_bindings = {
            stripe_classes: '',
            top_border: {},
        };
        let featureNodes = data.map(function(feature, idx, nodes) {
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

            return (
                <Feature key={feature.url} data={feature} stripe_classes={map_bindings.stripe_classes} style={map_bindings.top_border} />
            );
        }.bind(map_bindings));

        return (
            <div className="featureList">
                <table className="">
                    <thead>
                        <tr>
                            {headerNodes}
                        </tr>
                    </thead>
                    <tbody>
                        {featureNodes}
                    </tbody>
                </table>
            </div>
        );
    }
});

var FeaturePager = React.createClass({
    handlePagingEvent: function (e) {
        this.handlePaging(e.target.value);
    },
    handlePaging: function(page) {
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
    render: function() {
        var pages = [];

        if (this.props.currentPage <= 0) {
            pages.push(
                <li key="first" className="disabled">
                    <a href="#!"><i className="material-icons">skip_previous</i></a>
                </li>
            );
            pages.push(
                <li key="prev" className="disabled">
                    <a href="#!"><i className="material-icons">chevron_left</i></a>
                </li>
            );
        } else {
            pages.push(
                <li key="first" onClick={this.handlePaging.bind(this, 0)}>
                    <a href="#!"><i className="material-icons">skip_previous</i></a>
                </li>
            );
            pages.push(
                <li key="prev" onClick={this.handlePaging.bind(this, this.props.currentPage - 1)}>
                    <a href="#!"><i className="material-icons">chevron_left</i></a>
                </li>
            );
        }

        var options = [];
        for(var i = 0; i <= this.props.count; i += this.props.pageSize) {
            var page = i / this.props.pageSize + 1;

            options.push(<option key={i} value={page - 1}>{page}</option>);
        }
        pages.push(<li key="pager_select_li" className="intput-field"><select key="pager_select" className="browser-default" value={this.props.currentPage} onChange={this.handlePagingEvent} style={{width: 'auto', display: 'inline'}}>{options}</select></li>);
        pages.push(
            <li key="pager-text" className="input-field">
                out of {this.props.maxPages}
            </li>
        );

        if (this.props.currentPage >= this.props.maxPages - 1) {
            pages.push(
                <li key="next" className="disabled">
                    <a href="#!"><i className="material-icons">chevron_right</i></a>
                </li>
            );
            pages.push(
                <li key="last" className="disabled">
                    <a href="#!"><i className="material-icons">skip_next</i></a>
                </li>
            );
        } else {
            pages.push(
                <li key="next" onClick={this.handlePaging.bind(this, this.props.currentPage + 1)}>
                    <a href="#!"><i className="material-icons">chevron_right</i></a>
                </li>

            );
            pages.push(
                <li key="last" onClick={this.handlePaging.bind(this, this.props.maxPages - 1)}>
                    <a href="#!"><i className="material-icons">skip_next</i></a>
                </li>

            );
        }

        return (
            <div className="row">
                <div className="center">
                    <ul className="pagination">
                        {pages}
                    </ul>
                </div>
            </div>
        );
    }
});

var FeatureSearch = React.createClass({
    handleSearch: function(e) {
        this.props.handleSearch(e.target.value);
    },
    render: function() {
        return (
            <div className="row">
                <div className="input-field col s12 m8 l4">
                    <i className="material-icons prefix">search</i>
                    <input type="text" id="search_box" onChange={this.handleSearch} />
                    <label htmlFor="search_box">Filter</label>
                </div>
            </div>
        );
    }
});

var FeatureBox = React.createClass({
    getInitialState: function() {
        return {
            pageSize: 20,
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            data: []
        };
    },
    loadFeatureData: function() {


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
                        show_report_running(true);  // keep showing, that's cool.
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
                            $('.modal-trigger').leanModal();  // Also a good time to initialize modals...
                        }

                    }.bind(this)
                });
            }
        }
    },
    componentDidMount: function() {
        this.loadFeatureData();
        //$('.modal-trigger').leanModal();
    },
    handleSearch: function(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadFeatureData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadFeatureData);
    },
    render: function () {
        var pager = "";
        if (this.props.showPager) {
            pager = <FeaturePager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }

        var search = "";
        if (this.props.showSearch) {
            search = <FeatureSearch handleSearch={this.handleSearch} />;
        }

        return (
            <div className="featureBox">
                <FeatureList data={this.state.data} />
            </div>
        );
    }
});

ReactDOM.render(
    <FeatureBox items={spatialreports_items}
               showPager={spatialreports_feature_list_show_pager}
               showSearch={spatialreports_feature_list_show_search} />,
    document.getElementById(spatialreports_feature_list_attach_id)
);

function show_report_running(toggle) {
    var spinner = $('.progress');
    var little_spinner = $("#little-spinner");
    var reporting_complete_check = $("#reporting_complete");

    if (toggle === true) {
        spinner.css('visibility', 'visible');
        little_spinner.show();
        reporting_complete_check.hide();
    }
    else {
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
