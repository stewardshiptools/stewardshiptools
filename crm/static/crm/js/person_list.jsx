var Person = React.createClass({
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

        return (
            <div className={"collection-item avatar col " + this.props.collectionItemGridClass }>
                <img src={image_url} alt="" className="circle" />
                <a href={this.props.data.url}>
                    <span className="title">{this.props.data.name_last}, {this.props.data.name_first}</span>
                </a>
                {roles}
                {organizations}
            </div>
        );
    }
});

var PersonList = React.createClass({
    render: function() {
        var collectionItemGridClass = this.props.collectionItemGridClass;
        var personNodes = this.props.data.map(function(person) {
            return (
                <Person key={person.url} data={person} collectionItemGridClass={collectionItemGridClass} />
            );
        });

        return (
            <div className="personList">
                <div className="collection">
                    {personNodes}
                </div>
            </div>
        );
    }
});

var PersonPager = React.createClass({
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

var PersonSearch = React.createClass({
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
        var search_handle_proxy = $.proxy(this.handleSearch, this);     //holds on to react component's "this" context.
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

var PersonBox = React.createClass({
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
    loadPersonData: function() {
        var spinner = $('.progress');

        var query_start = '?';
        if (this.props.url.split('?').length > 1) {
            query_start = '&';
        }

        var pager_query = '';
        if (this.props.showPager) {
            pager_query = query_start + "limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize;
        }

        var search_query = '';
        if (this.props.showSearch) {
            if (this.props.showPager) {
                search_query = '&search=' + this.state.search;
            } else {
                search_query = query_start + 'search=' + this.state.search;
            }
        }

        spinner.css('visibility', 'visible');
        $.ajax({
            url: this.props.url + pager_query + '&search=' + this.state.search,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("Person results:", data);
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
        this.loadPersonData();
    },
    handleSearch: function(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadPersonData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadPersonData);
    },
    render: function () {
        var pager = "";
        if (this.props.showPager) {
            pager = <PersonPager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }

        var search = "";
        if (this.props.showSearch) {
            search = <PersonSearch handleSearch={this.handleSearch} />;
        }

        return (
            <div className="personBox">
                {search}
                {pager}
                <PersonList data={this.state.data} collectionItemGridClass={this.props.collectionItemGridClass}  />
                {pager}
            </div>
        );
    }
});

ReactDOM.render(
    <PersonBox url={crm_person_list_ajax_url}
               showPager={crm_person_list_show_pager}
               showSearch={crm_person_list_show_search}
               collectionItemGridClass={crm_person_list_grid_class}
    />,
    document.getElementById(crm_person_list_attach_id)
);
