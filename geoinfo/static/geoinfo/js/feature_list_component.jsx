var Spinner = React.createClass({
    render: function () {
        return (
            <div className="list-spinner preloader-wrapper medium active">
                <div className="spinner-layer spinner-blue">
                    <div className="circle-clipper left">
                        <div className="circle"></div>
                    </div><div className="gap-patch">
                    <div className="circle"></div>
                </div><div className="circle-clipper right">
                    <div className="circle"></div>
                </div>
                </div>

                <div className="spinner-layer spinner-red">
                    <div className="circle-clipper left">
                        <div className="circle"></div>
                    </div><div className="gap-patch">
                    <div className="circle"></div>
                </div><div className="circle-clipper right">
                    <div className="circle"></div>
                </div>
                </div>

                <div className="spinner-layer spinner-yellow">
                    <div className="circle-clipper left">
                        <div className="circle"></div>
                    </div><div className="gap-patch">
                    <div className="circle"></div>
                </div><div className="circle-clipper right">
                    <div className="circle"></div>
                </div>
                </div>

                <div className="spinner-layer spinner-green">
                    <div className="circle-clipper left">
                        <div className="circle"></div>
                    </div><div className="gap-patch">
                    <div className="circle"></div>
                </div><div className="circle-clipper right">
                    <div className="circle"></div>
                </div>
                </div>
            </div>
        );
    }
});

// This is where you'd setup an item, or a row.
var Feature = React.createClass({
    render: function() {
        let columnNodes = [];
        columnNodes.push(<td className="extra-tight-table-row" key={this.props.data.name}><a href={this.props.data.url}>{this.props.data.name}</a>
        </td>);
        $.each(this.props.data.data, function(key, value) {
            columnNodes.push(<td className="extra-tight-table-row" key={key + '-' + value}>{value}</td>);
        });

        return (
            <tr>
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
            headerNodes.push(<th key="name" data-field="name">Name</th>);
            $.each(this.props.data[0].data, function(key, value) {
                headerNodes.push(<th key={key} data-field={key}>{key}</th>);
            });
        }

        var featureNodes = this.props.data.map(function(feature) {
            return (
                <Feature key={feature.url} data={feature} />
            );
        });

        return (
            <div className="featureList row">
                <div className="col s12">
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
                    <Spinner />
                </div>
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
            <div className="input-field col s12 m8 l4">
                <i className="material-icons prefix">search</i>
                <input type="text" id="search_box" onChange={this.handleSearch} />
                <label htmlFor="search_box">Filter</label>
            </div>
        );
    }
});

var PageSizeSelect = React.createClass({
    handlePageSizeEvent: function (e) {
        this.props.setPageSize(e.target.value);
    },
    render: function () {
       var page_size_options = this.props.pageSizeOptions.map(function (option) {
           return (<option key={option} value={option}>{option}</option>);
       });
       page_size_options.unshift(<option key="All" value="-1">All</option>);

       return (
           <div id="page-size-select" className="input-field col s12 m4 l3">
               <select value={this.props.currentPageSize} onChange={this.handlePageSizeEvent}>
                   {page_size_options}
               </select>
               <label>Results per page</label>
           </div>
       );
   }
});

var FeatureBox = React.createClass({
    getInitialState: function() {
        return {
            pageSize: 25,
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            data: []
        };
    },
    featuresLoadedHook: function (results) {
        if (this.props.featuresLoadedHook) {
            var attach_id = $(ReactDOM.findDOMNode(this)).parent().attr('id');
            this.props.featuresLoadedHook(attach_id, results);
        }
    },
    loadFeatureData: function() {
        var spinner = $('.progress');
        var list_spinner = $(ReactDOM.findDOMNode(this)).find(".list-spinner");
        var table_body = $(ReactDOM.findDOMNode(this)).find("tbody");

        spinner.css('visibility', 'visible');
        list_spinner.css('display', 'block');
        table_body.css('display', 'none');

        var query_start = '?';
        if (this.props.url.split('?').length > 1) {
            query_start = '&';
        }

        var page_query = query_start;
        if (this.state.pageSize > 0) {
            page_query += "limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize + "&";
        }
        var ajax_url = this.props.url + page_query + 'search=' + this.state.search;

        $.ajax({
            url: ajax_url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                var results = data.results || data;
                var data_count = data.count || results.length;

                var max_pages = 1;
                if (this.state.pageSize > 0) {
                    max_pages = Math.ceil(data_count / this.state.pageSize);
                }

                this.setState({
                    data: results,
                    count: data_count,
                    maxPages: max_pages
                });

                this.featuresLoadedHook(results);
                spinner.css('visibility', 'hidden');
                list_spinner.css('display', 'none');
                table_body.css('display', 'table-row-group');
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function() {
        this.loadFeatureData();
        $(ReactDOM.findDOMNode(this)).find('div#page-size-select select').material_select();
        $(ReactDOM.findDOMNode(this)).find('div#page-size-select select').on('change', function(e) {
            this.setPageSize(e.target.value);
        }.bind(this));
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
    setPageSize: function(page_size) {
        this.setState({
            pageSize: page_size,
            currentPage: 0
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

        var page_size_options =[5, 10, 25, 50, 100, 500, 1000];
        var page_size_select = <PageSizeSelect
            pageSizeOptions={page_size_options}
            currentPageSize={this.state.pageSize}
            setPageSize={this.setPageSize}
        />;

        return (
            <div className="featureBox">
                <div className="row">
                    {search}
                    {page_size_select}
                </div>
                {pager}
                <FeatureList data={this.state.data} />
                {pager}
            </div>
        );
    }
});

window.FeatureBox = FeatureBox;
