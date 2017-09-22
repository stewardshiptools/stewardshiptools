(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

var Person = React.createClass({
    displayName: 'Person',

    render: function render() {
        var roles = '';
        var organizations = '';
        // TODO Pass default url into this script instead of hard-coding it.
        var image_url = this.props.data.pic || '/static/crm/img/trees_small.jpg';

        if (this.props.data.roles) {
            roles = React.createElement('p', null, this.props.data.roles.join(', '));
        }

        if (this.props.data.organizations) {
            organizations = ''; // TODO replace with a concatenated list of orgs.
        }

        return React.createElement('div', { className: "collection-item avatar col " + this.props.collectionItemGridClass }, React.createElement('img', { src: image_url, alt: '', className: 'circle' }), React.createElement('a', { href: this.props.data.url }, React.createElement('span', { className: 'title' }, this.props.data.name_last, ', ', this.props.data.name_first)), roles, organizations);
    }
});

var PersonList = React.createClass({
    displayName: 'PersonList',

    render: function render() {
        var collectionItemGridClass = this.props.collectionItemGridClass;
        var personNodes = this.props.data.map(function (person) {
            return React.createElement(Person, { key: person.url, data: person, collectionItemGridClass: collectionItemGridClass });
        });

        return React.createElement('div', { className: 'personList' }, React.createElement('div', { className: 'collection' }, personNodes));
    }
});

var PersonPager = React.createClass({
    displayName: 'PersonPager',

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

var PersonSearch = React.createClass({
    displayName: 'PersonSearch',

    handleSearch: function handleSearch(e) {
        // Triggering search via typewatch means that "e" isn't an event
        // anymore, it's a value. We try the old way first anyways.
        try {
            this.props.handleSearch(e.target.value);
        } catch (err) {
            this.props.handleSearch(e);
        }
    },
    render: function render() {
        return React.createElement('div', { className: 'row' }, React.createElement('div', { className: 'input-field col s12 m8 l4' }, React.createElement('i', { className: 'material-icons prefix' }, 'search'), React.createElement('input', { type: 'text', id: 'search_box' }), React.createElement('label', { htmlFor: 'search_box' }, 'Filter')));
    },
    componentDidMount: function componentDidMount() {
        var search_box = $(ReactDOM.findDOMNode(this)).find('input');
        var search_handle_proxy = $.proxy(this.handleSearch, this); //holds on to react component's "this" context.
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

var PersonBox = React.createClass({
    displayName: 'PersonBox',

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
    loadPersonData: function loadPersonData() {
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
            success: function (data) {
                console.log("Person results:", data);
                if (!data.results) {
                    data['results'] = data;
                }
                this.setState({
                    data: data.results,
                    count: data.count,
                    maxPages: Math.ceil(data.count / this.state.pageSize)
                });

                spinner.css('visibility', 'hidden');
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function componentDidMount() {
        this.loadPersonData();
    },
    handleSearch: function handleSearch(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadPersonData);
    },
    setPage: function setPage(page) {
        this.setState({
            currentPage: page
        }, this.loadPersonData);
    },
    render: function render() {
        var pager = "";
        if (this.props.showPager) {
            pager = React.createElement(PersonPager, {
                currentPage: this.state.currentPage,
                maxPages: this.state.maxPages,
                pageSize: this.state.pageSize,
                count: this.state.count,
                setPage: this.setPage
            });
        }

        var search = "";
        if (this.props.showSearch) {
            search = React.createElement(PersonSearch, { handleSearch: this.handleSearch });
        }

        return React.createElement('div', { className: 'personBox' }, search, pager, React.createElement(PersonList, { data: this.state.data, collectionItemGridClass: this.props.collectionItemGridClass }), pager);
    }
});

ReactDOM.render(React.createElement(PersonBox, { url: crm_person_list_ajax_url,
    showPager: crm_person_list_show_pager,
    showSearch: crm_person_list_show_search,
    collectionItemGridClass: crm_person_list_grid_class
}), document.getElementById(crm_person_list_attach_id));

},{}]},{},[1]);
