var Organization = React.createClass({
    render: function() {
        return (
            <div className="col s12 m6 l4">
                <div className="card dashboard-card hoverable">
                    <div className="card-content">
                        <span className="card-title">
                            <div className="valign-wrapper"><i className="material-icons left grey-text text-darken-2">business</i>
                                <a href={this.props.data.url}>{ this.props.data.name }</a>
                            </div>
                        </span>
                        <div className="center-align">
                            <p><a href={ "mailto:" + this.props.data.email }>{ this.props.data.email }</a></p>
                            <p>{ this.props.data.phone }</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

var OrganizationList = React.createClass({
    render: function() {
        var organizationNodes = this.props.data.map(function(organization) {
            return (
                <Organization key={organization.url} data={organization} />
            );
        });

        return (
            <div className="organizationList row">
                {organizationNodes}
            </div>
        );
    }
});

var OrganizationPager = React.createClass({
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

var OrganizationSearch = React.createClass({
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
            <div className="row">
                <div className="input-field col s12 m8 l4">
                    <i className="material-icons prefix">search</i>
                    <input type="text" id="search_box"/>
                    <label htmlFor="search_box">Filter</label>
                </div>
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

var OrganizationBox = React.createClass({
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
    loadOrganizationData: function() {
        var spinner = $('.progress');

        spinner.css('visibility', 'visible');
        $.ajax({
            url: this.props.url + "?limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize + '&search=' + this.state.search,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("Organization results:", data);
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
        this.loadOrganizationData();
    },
    handleSearch: function(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadOrganizationData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadOrganizationData);
    },
    render: function () {
        var pager = "";
        if (this.props.showPager) {
            pager = <OrganizationPager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }

        var search = "";
        if (this.props.showSearch) {
            search = <OrganizationSearch handleSearch={this.handleSearch} />;
        }

        return (
            <div className="organizationBox">
                {search}
                {pager}
                <OrganizationList data={this.state.data} />
                {pager}
            </div>
        );
    }
});

ReactDOM.render(
    <OrganizationBox url={crm_organization_list_ajax_url}
               showPager={crm_organization_list_show_pager}
               showSearch={crm_organization_list_show_search} />,
    document.getElementById(crm_organization_list_attach_id)
);
