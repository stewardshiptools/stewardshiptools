var React = require('react');
var ReactDOM = require('react-dom');

// This is where you'd setup an item, or a row.
var Report = React.createClass({
    render: function() {
        var report_on_nodes = this.props.data.report_on.map(function(layer, key) {
            return (<li key={key} ><a href={layer.url}>{layer.name}</a></li>);
        });

        return (
            <tr>
                <td className="extra-tight-table-row"><a href={this.props.data.url}>{this.props.data.name}</a></td>
                <td className="extra-tight-table-row">{this.props.data.distance_cap}</td>
                <td className="extra-tight-table-row">
                    <ul>{report_on_nodes}</ul>
                </td>
            </tr>
        );
    }
});

// This is where to setup any list wrappers, like tables.
var ReportList = React.createClass({
    render: function() {
        var reportNodes = this.props.data.map(function(report) {
            return (
                <Report key={report.url} data={report} />
            );
        });

        return (
            <div className="reportList">
                <table className="">
                    <thead>
                        <tr>
                            <th data-field="name">Name</th>
                            <th data-field="distance_cap">Default distance cap</th>
                            <th data-field="report_on">Report on items</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reportNodes}
                    </tbody>
                </table>
            </div>
        );
    }
});

var ReportPager = React.createClass({
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

var ReportSearch = React.createClass({
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

var ReportBox = React.createClass({
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
    loadReportData: function() {
        var spinner = $('.progress');

        spinner.css('visibility', 'visible');
        $.ajax({
            url: this.props.url + "?limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize + '&search=' + this.state.search,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("Report results:", data);
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
        this.loadReportData();
    },
    handleSearch: function(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadReportData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadReportData);
    },
    render: function () {
        var pager = "";
        if (this.props.showPager) {
            pager = <ReportPager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }

        var search = "";
        if (this.props.showSearch) {
            search = <ReportSearch handleSearch={this.handleSearch} />;
        }

        return (
            <div className="reportBox">
                {search}
                {pager}
                <ReportList data={this.state.data} />
                {pager}
            </div>
        );
    }
});

ReactDOM.render(
    <ReportBox url={geoinfo_report_list_ajax_url}
               showPager={geoinfo_report_list_show_pager}
               showSearch={geoinfo_report_list_show_search} />,
    document.getElementById(geoinfo_report_list_attach_id)
);
