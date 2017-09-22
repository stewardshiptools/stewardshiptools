var React = require('react');
var ReactDOM = require('react-dom');

// This is where you'd setup an item, or a row.
var Layer = React.createClass({
    render: function() {
        var roles = '';
        var organizations = '';
        // TODO Pass default url into this script instead of hard-coding it.
        var image_url = this.props.data.pic || '/static/crm/img/trees_small.jpg';

        if (this.props.data.roles) {
            roles = <p>{this.props.data.roles.join(', ')}</p>;
        }

        if (this.props.data.organizations) {
            organizations = '';  // TODO replace with a concatenated list of orgs.
        }

        var columns = [];
        columns.push((
            <td className="extra-tight-table-row" key={this.props.data.id + '-name'}><a href={this.props.data.url}>{this.props.data.name}</a></td>));

        if (this.props.data.layer_type) {
            columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-layer_type'}>{this.props.data.layer_type}</td>));
        }

        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-feature_count'}>{this.props.data.feature_count}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-author'}>{this.props.data.author}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-created'}>{this.props.data.created}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-notes'}>{this.props.data.notes}</td>));

        return (
            <tr>
                {columns}
            </tr>
        );
    }
});

// This is where to setup any list wrappers, like tables.
var LayerList = React.createClass({
    render: function() {
        var layerNodes = this.props.data.map(function(layer) {
            return (
                <Layer key={layer.id} data={layer} />
            );
        });

        var headers = [];
        var show_type = false;
        $.each(this.props.data, function(key, value) {
            if (value.layer_type) {
                show_type = true;
            }
            return false; // This is dirty... but I can't seem to access the attributes outside a loop.
        });

        headers.push((<th key="name" data-field="name">Name</th>));

        if (show_type) {
            headers.push((<th key="type" data-field="type">Type</th>));
        }

        headers.push((<th key="feature_count" data-field="feature_count"># Features</th>));
        headers.push((<th key="author" data-field="author">Created By</th>));
        headers.push((<th key="created" data-field="created">Created Date</th>));
        headers.push((<th key="notes" data-field="notes">Description</th>));

        return (
            <div className="layerList">
                <table className="">
                    <thead>
                        <tr>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {layerNodes}
                    </tbody>
                </table>
            </div>
        );
    }
});

var LayerPager = React.createClass({
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

var LayerSearch = React.createClass({
    handleSearch: function(e) {
        // Triggering search via typewatch means that "e" isn't an event
        // anymore, it's a value. We try the old way first anyways.
        try {
            this.props.handleSearch(e.target.value);
        }
        catch (err) {
            this.props.handleSearch(e);
        }
    },
    render: function() {
        return (
            <div className="input-field col s12 m8 l4">
                <i className="material-icons prefix">search</i>
                <input type="text" id="search_box"/>
                <label htmlFor="search_box">Filter</label>
            </div>
        );
    },
    componentDidMount: function () {
        var search_box = $(ReactDOM.findDOMNode(this)).find('input');
        var search_handle_proxy = $.proxy(this.handleSearch, this); //holds on to react component's "this" context.
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

var LayerTypeFilter = React.createClass({
    handleLayerFilterEvent: function (e) {
        this.props.setLayerType(e.target.value);
    },
    render: function () {
       var layer_type_options = this.props.layerTypes.map(function (option) {
           var key = Object.keys(option)[0];
           var val = option[key];
           return (<option key={key} value={val}>{key}</option>);

       });
       return (
           <div id="layer-type-filter-select" className="input-field col s12 m4 l3">
               <select value={this.props.currentType} onChange={this.handleLayerFilterEvent}>
                   {layer_type_options}
               </select>
               <label>Layer type</label>
           </div>
       );
   }
});

var LayerBox = React.createClass({
    getInitialState: function() {
        return {
            pageSize: 20,
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            layerType: ((this.props.default_layer_type) ? this.props.default_layer_type : '') ,
            data: []
        };
    },
    loadLayerData: function() {
        var spinner = $('.progress');

        spinner.css('visibility', 'visible');
        $.ajax({
            url: this.props.url + "?limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize + '&search=' + this.state.search + '&layer_type=' + this.state.layerType,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("Layer results:", data);
                if (!data.results){
                    data['results'] = data;
                }
                this.setState({
                    data: data.results,
                    count: data.count,
                    maxPages: Math.ceil(data.count / this.state.pageSize)
                });

                spinner.css('visibility', 'hidden');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function() {
        this.loadLayerData();
        $(ReactDOM.findDOMNode(this)).find('div#layer-type-filter-select select').material_select();
        $(ReactDOM.findDOMNode(this)).find('div#layer-type-filter-select select').on('change', function(e) {
            this.setLayerType(e.target.value);
        }.bind(this));
    },
    handleSearch: function(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadLayerData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadLayerData);
    },
    setLayerType: function (type) {
        this.setState({
            layerType: type
        }, this.loadLayerData);
    },
    render: function () {
        var pager = "";
        if (this.props.showPager) {
            pager = <LayerPager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }


        var layer_type_select = '';
        console.log("state layertype is:", this.state);
        if (geoinfo_layer_types) {
            layer_type_select = <LayerTypeFilter
                layerTypes={geoinfo_layer_types}
                currentType={this.state.layerType}
                setLayerType={this.setLayerType}
            />;
        }

        var search = "";
        if (this.props.showSearch) {
            search = <LayerSearch handleSearch={this.handleSearch} />;
        }

        return (
            <div className="layerBox">
                <div className="row">
                    {search}
                    {layer_type_select}
                </div>
                {pager}
                <LayerList data={this.state.data} />
                {pager}
            </div>
        );
    }
});

ReactDOM.render(
    <LayerBox url={geoinfo_layer_list_ajax_url}
               showPager={geoinfo_layer_list_show_pager}
               showSearch={geoinfo_layer_list_show_search}
              default_layer_type = {geoinfo_layer_list_default_layer_type}
    />,
    document.getElementById(geoinfo_layer_list_attach_id)
);
