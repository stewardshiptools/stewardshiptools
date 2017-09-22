(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

var Spinner = React.createClass({
    displayName: "Spinner",

    render: function render() {
        return React.createElement(
            "div",
            { className: "list-spinner preloader-wrapper medium active" },
            React.createElement(
                "div",
                { className: "spinner-layer spinner-blue" },
                React.createElement(
                    "div",
                    { className: "circle-clipper left" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "gap-patch" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "circle-clipper right" },
                    React.createElement("div", { className: "circle" })
                )
            ),
            React.createElement(
                "div",
                { className: "spinner-layer spinner-red" },
                React.createElement(
                    "div",
                    { className: "circle-clipper left" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "gap-patch" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "circle-clipper right" },
                    React.createElement("div", { className: "circle" })
                )
            ),
            React.createElement(
                "div",
                { className: "spinner-layer spinner-yellow" },
                React.createElement(
                    "div",
                    { className: "circle-clipper left" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "gap-patch" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "circle-clipper right" },
                    React.createElement("div", { className: "circle" })
                )
            ),
            React.createElement(
                "div",
                { className: "spinner-layer spinner-green" },
                React.createElement(
                    "div",
                    { className: "circle-clipper left" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "gap-patch" },
                    React.createElement("div", { className: "circle" })
                ),
                React.createElement(
                    "div",
                    { className: "circle-clipper right" },
                    React.createElement("div", { className: "circle" })
                )
            )
        );
    }
});

// This is where you'd setup an item, or a row.
var Feature = React.createClass({
    displayName: "Feature",

    render: function render() {
        var columnNodes = [];
        columnNodes.push(React.createElement(
            "td",
            { className: "extra-tight-table-row", key: this.props.data.name },
            React.createElement(
                "a",
                { href: this.props.data.url },
                this.props.data.name
            )
        ));
        $.each(this.props.data.data, function (key, value) {
            columnNodes.push(React.createElement(
                "td",
                { className: "extra-tight-table-row", key: key + '-' + value },
                value
            ));
        });

        return React.createElement(
            "tr",
            null,
            columnNodes
        );
    }
});

// This is where to setup any list wrappers, like tables.
var FeatureList = React.createClass({
    displayName: "FeatureList",

    render: function render() {
        var headerNodes = [];
        if (this.props.data[0]) {
            headerNodes.push(React.createElement(
                "th",
                { key: "name", "data-field": "name" },
                "Name"
            ));
            $.each(this.props.data[0].data, function (key, value) {
                headerNodes.push(React.createElement(
                    "th",
                    { key: key, "data-field": key },
                    key
                ));
            });
        }

        var featureNodes = this.props.data.map(function (feature) {
            return React.createElement(Feature, { key: feature.url, data: feature });
        });

        return React.createElement(
            "div",
            { className: "featureList row" },
            React.createElement(
                "div",
                { className: "col s12" },
                React.createElement(
                    "table",
                    { className: "" },
                    React.createElement(
                        "thead",
                        null,
                        React.createElement(
                            "tr",
                            null,
                            headerNodes
                        )
                    ),
                    React.createElement(
                        "tbody",
                        null,
                        featureNodes
                    )
                ),
                React.createElement(Spinner, null)
            )
        );
    }
});

var FeaturePager = React.createClass({
    displayName: "FeaturePager",

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
            pages.push(React.createElement(
                "li",
                { key: "first", className: "disabled" },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "skip_previous"
                    )
                )
            ));
            pages.push(React.createElement(
                "li",
                { key: "prev", className: "disabled" },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "chevron_left"
                    )
                )
            ));
        } else {
            pages.push(React.createElement(
                "li",
                { key: "first", onClick: this.handlePaging.bind(this, 0) },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "skip_previous"
                    )
                )
            ));
            pages.push(React.createElement(
                "li",
                { key: "prev", onClick: this.handlePaging.bind(this, this.props.currentPage - 1) },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "chevron_left"
                    )
                )
            ));
        }

        var options = [];
        for (var i = 0; i <= this.props.count; i += this.props.pageSize) {
            var page = i / this.props.pageSize + 1;

            options.push(React.createElement(
                "option",
                { key: i, value: page - 1 },
                page
            ));
        }
        pages.push(React.createElement(
            "li",
            { key: "pager_select_li", className: "intput-field" },
            React.createElement(
                "select",
                { key: "pager_select", className: "browser-default", value: this.props.currentPage, onChange: this.handlePagingEvent, style: { width: 'auto', display: 'inline' } },
                options
            )
        ));
        pages.push(React.createElement(
            "li",
            { key: "pager-text", className: "input-field" },
            "out of ",
            this.props.maxPages
        ));

        if (this.props.currentPage >= this.props.maxPages - 1) {
            pages.push(React.createElement(
                "li",
                { key: "next", className: "disabled" },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "chevron_right"
                    )
                )
            ));
            pages.push(React.createElement(
                "li",
                { key: "last", className: "disabled" },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "skip_next"
                    )
                )
            ));
        } else {
            pages.push(React.createElement(
                "li",
                { key: "next", onClick: this.handlePaging.bind(this, this.props.currentPage + 1) },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "chevron_right"
                    )
                )
            ));
            pages.push(React.createElement(
                "li",
                { key: "last", onClick: this.handlePaging.bind(this, this.props.maxPages - 1) },
                React.createElement(
                    "a",
                    { href: "#!" },
                    React.createElement(
                        "i",
                        { className: "material-icons" },
                        "skip_next"
                    )
                )
            ));
        }

        return React.createElement(
            "div",
            { className: "row" },
            React.createElement(
                "div",
                { className: "center" },
                React.createElement(
                    "ul",
                    { className: "pagination" },
                    pages
                )
            )
        );
    }
});

var FeatureSearch = React.createClass({
    displayName: "FeatureSearch",

    handleSearch: function handleSearch(e) {
        this.props.handleSearch(e.target.value);
    },
    render: function render() {
        return React.createElement(
            "div",
            { className: "input-field col s12 m8 l4" },
            React.createElement(
                "i",
                { className: "material-icons prefix" },
                "search"
            ),
            React.createElement("input", { type: "text", id: "search_box", onChange: this.handleSearch }),
            React.createElement(
                "label",
                { htmlFor: "search_box" },
                "Filter"
            )
        );
    }
});

var PageSizeSelect = React.createClass({
    displayName: "PageSizeSelect",

    handlePageSizeEvent: function handlePageSizeEvent(e) {
        this.props.setPageSize(e.target.value);
    },
    render: function render() {
        var page_size_options = this.props.pageSizeOptions.map(function (option) {
            return React.createElement(
                "option",
                { key: option, value: option },
                option
            );
        });
        page_size_options.unshift(React.createElement(
            "option",
            { key: "All", value: "-1" },
            "All"
        ));

        return React.createElement(
            "div",
            { id: "page-size-select", className: "input-field col s12 m4 l3" },
            React.createElement(
                "select",
                { value: this.props.currentPageSize, onChange: this.handlePageSizeEvent },
                page_size_options
            ),
            React.createElement(
                "label",
                null,
                "Results per page"
            )
        );
    }
});

var FeatureBox = React.createClass({
    displayName: "FeatureBox",

    getInitialState: function getInitialState() {
        return {
            pageSize: 25,
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            data: []
        };
    },
    featuresLoadedHook: function featuresLoadedHook(results) {
        if (this.props.featuresLoadedHook) {
            var attach_id = $(ReactDOM.findDOMNode(this)).parent().attr('id');
            this.props.featuresLoadedHook(attach_id, results);
        }
    },
    loadFeatureData: function loadFeatureData() {
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
            success: function (data) {
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
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function componentDidMount() {
        this.loadFeatureData();
        $(ReactDOM.findDOMNode(this)).find('div#page-size-select select').material_select();
        $(ReactDOM.findDOMNode(this)).find('div#page-size-select select').on('change', function (e) {
            this.setPageSize(e.target.value);
        }.bind(this));
    },
    handleSearch: function handleSearch(search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadFeatureData);
    },
    setPage: function setPage(page) {
        this.setState({
            currentPage: page
        }, this.loadFeatureData);
    },
    setPageSize: function setPageSize(page_size) {
        this.setState({
            pageSize: page_size,
            currentPage: 0
        }, this.loadFeatureData);
    },
    render: function render() {
        var pager = "";
        if (this.props.showPager) {
            pager = React.createElement(FeaturePager, {
                currentPage: this.state.currentPage,
                maxPages: this.state.maxPages,
                pageSize: this.state.pageSize,
                count: this.state.count,
                setPage: this.setPage
            });
        }

        var search = "";
        if (this.props.showSearch) {
            search = React.createElement(FeatureSearch, { handleSearch: this.handleSearch });
        }

        var page_size_options = [5, 10, 25, 50, 100, 500, 1000];
        var page_size_select = React.createElement(PageSizeSelect, {
            pageSizeOptions: page_size_options,
            currentPageSize: this.state.pageSize,
            setPageSize: this.setPageSize
        });

        return React.createElement(
            "div",
            { className: "featureBox" },
            React.createElement(
                "div",
                { className: "row" },
                search,
                page_size_select
            ),
            pager,
            React.createElement(FeatureList, { data: this.state.data }),
            pager
        );
    }
});

window.FeatureBox = FeatureBox;

},{}]},{},[1]);
