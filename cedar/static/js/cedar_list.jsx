/**
 * Created by greg on 13/01/17.
 */
require('babel-polyfill');
var React = require('react');
var ReactDOM = require('react-dom');

var filter_components= {};

var CedarListTableItem = React.createClass({
    render: function() {
        //columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-num-comments'}>{this.props.data.num_comments}</td>));

        var columns = this.props.fields.map(function (field) {
            let column_classes = field[0] + "-list-field";

            if (typeof field[1] === 'object') {
                if (field[1].type === 'link') {
                    return (<td className={"extra-tight-table-row " + column_classes} key={this.props.data.id + '-' + field[0]}>
                        <a href={this.props.data[field[1].url_field]}>{this.props.data[field[0]]}</a>
                    </td>);
                } else if (field[1].type === 'link-list') {
                    const values = this.props.data[field[0]];

                    let links = values.map(function (val) {
                        return<a key={field[0] + '-' + val.url}
                                 className="btn btn-little rounded waves-effect waves-light grey lighten-5 grey-text text-darken-1"
                                 href={val.url}> {val.name} </a>;
                    }.bind(field));

                    // We only want to run reduce if links is a non-empty array.
                    if (links.length > 0) {
                        links = links.reduce(function (accu, el, idx, nodes) {
                            // We need to use Array.reduce because its the only way to join and maintain the react components.
                            // After the first pass accu is an Array, append to it with commas
                            if (accu.constructor === Array) {
                                return [...accu, "\u00a0", el];
                            }

                            // The first thing accu is set to is the first element, el is the second one.  Place them in an array.
                            return [accu, "\u00a0", el];
                        });
                    }

                    return <td className={"extra-tight-table-row " + column_classes} key={this.props.data.id + '-' + field[0]}>
                        {links}
                    </td>;
                }
            } else {
                if (this.props.data[field[0]] !== null && this.props.data[field[0]].constructor === Array) {
                    return (<td className={"extra-tight-table-row " + column_classes}
                                key={this.props.data.id + '-' + field[0]}>{this.props.data[field[0]].join(', ')}</td>);
                } else {
                    return (<td className={"extra-tight-table-row " + column_classes}
                                key={this.props.data.id + '-' + field[0]}>{this.props.data[field[0]]}</td>);
                }
            }
        }.bind(this));

        let stripe_class = '';
        if (this.props.index % 2) {
            stripe_class = 'grey lighten-5';
        }

        return (
            <tr className={stripe_class + " list-row"}>
                {columns}
            </tr>
        );
    }
});

// This is where to setup any list wrappers, like tables.
var CedarListTable = React.createClass({
    render: function() {
        var rowNodes = this.props.data.map(function(row, idx) {
            return (
                <CedarListTableItem key={row.id} data={row} fields={this.props.fields} index={idx} />
            );
        }.bind(this));

        var headers = this.props.fields.map(function (field) {
            if (typeof field[1] === 'object') {
                return (<th key={field[0]} data-field={field[0]}>{field[1].verbose_name}</th>);
            } else {
                return (<th key={field[0]} data-field={field[0]}>{field[1]}</th>);
            }
        });

        return (
            <div className="cedarList">
                <table className="">
                    <thead>
                        <tr>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {rowNodes}
                    </tbody>
                </table>
            </div>
        );
    }
});

var CedarListPager = React.createClass({
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
                <li key="prev" onClick={this.handlePaging.bind(this, parseInt(this.props.currentPage, 10) - 1)}>
                    <a href="#!"><i className="material-icons">chevron_left</i></a>
                </li>
            );
        }

        var options = [];
        var page_size = parseInt(this.props.pageSize, 10);

        // A page size of less than 0 represents that we are showing all the items on a single page.
        if (page_size <= 0) {
            page_size = this.props.count;
        }

        for(var i = 0; i < this.props.count; i += page_size) {
            var page = (i / this.props.pageSize) + 1;

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
                <li key="next" onClick={this.handlePaging.bind(this, parseInt(this.props.currentPage, 10) + 1)}>
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

var PageSizeSelect = React.createClass({
    getInitialState: function() {
        return {
            'value': this.props.currentValue,
            'reset': false
        };
    },
    initialize: function () {
        $(ReactDOM.findDOMNode(this)).find('select').material_select();
    },
    runCallback: function() {
        this.props.setPageSize(parseInt(this.state.value, 10));
    },
    componentDidMount: function () {
        this.initialize();

        // material and select2 both butcher the select lists, so we need to attach a new onChange event.
        $(ReactDOM.findDOMNode(this)).find('select').on('change', function (e) {
            this.handlePageSizeEvent(e);
        }.bind(this));

        $( document ).on(this.props.resetEvent + '-page-size', function(e) {
            this.setState({value: this.props.defaultValue, reset: true});
        }.bind(this));
    },
    componentDidUpdate: function() {
        if (this.state.reset) {
            this.initialize();
            this.setState({reset: false});
        }
    },
    handlePageSizeEvent: function (e) {
        this.setState({
            value: e.target.value
        }, this.runCallback);
    },
    render: function () {
       var page_size_options = this.props.pageSizeOptions.map(function (option) {
           return (<option key={option} value={option}>{option}</option>);
       });
       page_size_options.unshift(<option key="All" value="-1">All</option>);

       return (
           <div className={"page-size-select input-field " + this.props.cssClasses}>
               <select value={this.state.value} onChange={this.handlePageSizeEvent}>
                   {page_size_options}
               </select>
               <label>Results per page</label>
           </div>
       );
   }
});

var SortSelect = React.createClass({
    getInitialState: function () {
        return {
            'value': this.props.currentSort,
            'reset': false
        };
    },
    initialize: function () {
        $(ReactDOM.findDOMNode(this)).find('select').material_select();
    },
    runCallback: function () {
        this.props.setSort(this.state.value);
    },
    componentDidMount: function() {
        this.initialize();

        $(ReactDOM.findDOMNode(this)).find('select').on('change', function (e) {
            this.handleSortEvent(e);
        }.bind(this));

        $( document ).on(this.props.resetEvent + '-sort', function(e) {
            this.setState({value: this.props.defaultSort, reset: true});
        }.bind(this));
    },
    componentDidUpdate: function() {
        if (this.state.reset) {
            this.initialize();
            this.setState({reset: false});
        }
    },
    handleSortEvent: function (e) {
        var sort;

        // Get state values
        var state_split_values = this.state.value.split(',');
        var state_value = state_split_values.splice(-1)[0];

        // If multiple sorts are provided we only alter the last one.
        var split_values = e.target.value.split(',');
        var value = split_values.splice(-1)[0];

        if (e.target.value == 'asc' || e.target.value == 'desc') {
            // Since e.target.value is for the direction dropdown in this case, we want to take our
            // values from the state.
            split_values = state_split_values;

            if (state_value.startsWith("-")) {
                sort = state_value.substring(1);
            } else {
                sort = '-' + state_value;
            }
        } else {
            var direction = '';
            if (state_value.startsWith("-")) {
                direction = '-';
            }
            sort = direction + value;
        }

        var new_sort = split_values.concat([sort]);
        this.setState({
            value: new_sort.join(',')
        }, this.runCallback);
    },
    render: function () {
        // Get state values
        var direction = 'asc';
        var state_split_values = this.state.value.split(',');
        var state_value = state_split_values.splice(-1)[0];

        if (state_value.startsWith('-')) {
            direction = 'desc';
            state_value = state_value.substring(1);
        }
        state_value = state_split_values.concat([state_value]).join(',');

       var sort_options = this.props.sortOptions.map(function (option) {
           return (<option key={option[0]} value={option[0]}>{option[1]}</option>);
       });

       return (
           <div className={"sort-select input-field " + this.props.cssClasses}>
               <div className="col s8">
                   <select value={state_value} onChange={this.handleSortEvent}>
                       {sort_options}
                   </select>
                   <label>Sort options</label>
               </div>
               <div className="col s4">
                   <select value={direction} onChange={this.handleSortEvent}>
                       <option value="asc">Asc.</option>
                       <option value="desc">Desc.</option>
                   </select>
                   <label>Sort options</label>
               </div>
           </div>
       );
   }
});

var CedarListFilterText = React.createClass({
    getInitialState: function () {
        var value = decodeURIComponent(this.props.currentValue) || '';

        return {
            'value': value,
        };
    },
    runCallback: function() {
        this.props.handleFilter(this.props.name, encodeURIComponent(this.state.value));
    },
    componentDidMount: function () {
        var search_box = $(ReactDOM.findDOMNode(this)).find('input');
        var search_handle_proxy = $.proxy(this.handleFilter, this); //holds on to react component's "this" context.
        $(search_box).typeWatch({
            wait: 550,
            callback: function (value) {
                search_handle_proxy(value);
            },
            captureLength: 1,
            allowSubmit: true,
        });

        $( document ).on(this.props.resetEvent + '-' + this.props.name, function(e) {
            this.setState({value: decodeURIComponent(this.props.defaultValue)});
        }.bind(this));
    },
    handleChange: function (e) {
        // React is annoying with controlled inputs.  I have to have an onChange event to keep the value
        // attribute updated when I type, otherwise react will continually replace the value with the
        // previous state.
        this.setState({value: e.target.value});
    },
    handleFilter: function(e) {
        // Triggering search via typewatch means that "e" isn't an event
        // anymore, it's a value. We try the old way first anyways.
        var value = '';
        try {
            value = e.target.value;
        }
        catch (err) {
            value = e;
        }

        this.setState({
            value: value
        }, this.runCallback);
    },
    render: function() {
        return (
            <div className="filter-field input-field col s12">
                <i className="material-icons prefix">search</i>
                <input type="text" id={this.props.id} value={this.state.value} onChange={this.handleChange} />
                <label htmlFor={this.props.id}>{this.props.verboseName}</label>
            </div>
        );
    }
});
filter_components['text'] = CedarListFilterText;

var CedarListFilterDate = React.createClass({
    getInitialState: function () {
        var value = decodeURIComponent(this.props.currentValue) || '';

        return {
            'value': value,
            'reset': false
        };
    },
    initialize: function () {
        var element = $(ReactDOM.findDOMNode(this)).find('input.datefilter');

        const limit_years_option = this.props.limitYears ? new Date() : null;

        let select_years_option = 15;  // Start with a sane default number of years.
        if (this.props.selectYears === 0) {  // We wil interpret 0 or 1 as false or true respectively.
            select_years_option = false;
        } else if (this.props.selectYears === 1) {
            select_years_option = true;
        } else {  // Any other numbers can be passed directly
            select_years_option = this.props.selectYears;
        }

        $(ReactDOM.findDOMNode(this)).find('input.datefilter').on('change', function (e) {
            this.handleFilter(e);
        }.bind(this));

        element.pickadate({
            selectMonths: true, // Creates a dropdown to control month
            selectYears: select_years_option, // Creates a dropdown of x years to control year
            format: 'yyyy-mm-dd',
            max: limit_years_option, // limits max date to today.
            onSet: function (context) {
                element.val(this.get());    // get the picker val and set to input val
            }
        });
    },
    runCallback: function() {
        this.props.handleFilter(this.props.name, encodeURIComponent(this.state.value));
    },
    componentDidMount: function () {
        this.initialize();
        $( document ).on(this.props.resetEvent + '-' + this.props.name, function(e) {
            this.setState({value: decodeURIComponent(this.props.defaultValue)});
        }.bind(this));
    },
    componentDidUpdate: function() {
        // The reason we need the reset flag is that the butchered versions of these lists made by
        // material and select2 don't get updated (after resetting especially) unless we reinitialize them.
        if (this.state.reset) {
            this.initialize();
            this.setState({reset: false});
        }
    },
    handleFilter: function(e) {
        // Triggering search via typewatch means that "e" isn't an event
        // anymore, it's a value. We try the old way first anyways.
        var value = '';
        try {
            value = e.target.value;
        }
        catch (err) {
            value = e;
        }

        this.setState({
            value: value
        }, this.runCallback);
    },
    render: function() {
        return (
            <div className="filter-field input-field col s12">
                <i className="material-icons prefix grey-text">date_range</i>
                <input type="date" className="datefilter" id={this.props.id} value={this.state.value} />
                <label className="active" htmlFor={this.props.id}>{this.props.verboseName}</label>
            </div>
        );
    }
});
filter_components['date'] = CedarListFilterDate;

var CedarListFilterSelect = React.createClass({
    getInitialState: function() {
        return {
            'value': this.props.currentValue,
            'reset': false
        };
    },
    initialize: function () {
        var element = $(ReactDOM.findDOMNode(this)).find('select');
        if (this.props.selectType == 'material') {
            element.material_select();
        } else if (this.props.selectType == 'select2') {
            element.select2();

            $(ReactDOM.findDOMNode(this)).find('span.select2-container').css('width', '100%');
        }
    },
    runCallback: function() {
        this.props.handleFilter(this.props.name, this.state.value);
    },
    componentDidMount: function() {
        this.initialize();

        // material and select2 both butcher the select lists, so we need to attach a new onChange event.
        $(ReactDOM.findDOMNode(this)).find('select').on('change', function (e) {
            this.handleFilter(e);
        }.bind(this));

        $( document ).on(this.props.resetEvent + '-' + this.props.name, function(e) {
            this.setState({value: this.props.defaultValue, reset: true});
        }.bind(this));
    },
    componentDidUpdate: function() {
        // The reason we need the reset flag is that the butchered versions of these lists made by
        // material and select2 don't get updated (after resetting especially) unless we reinitialize them.
        if (this.state.reset) {
            this.initialize();
            this.setState({reset: false});
        }
    },
    handleFilter: function (e) {
        var value;
        if (this.props.isMultiple) {
            value = [];
            for (var option of e.target.options) {
                if (option.selected) {
                    value.push(option.value);
                }
            }

        } else {
            value = e.target.value;
        }
        this.setState({
            value: value
        }, this.runCallback);
    },
    render: function () {
        var filter_options = this.props.options.map(function (value) {
            return (<option key={this.props.name + "-" + value[0]} value={value[0]}>{value[1]}</option>);
        }.bind(this));

        var css_classes = this.props.cssClassess || "col s12";

        var selectFilter;
        if (this.props.isMultiple == true) {
            selectFilter = (
                <select multiple value={this.state.value} onChange={this.handleFilter}>
                    {filter_options}
                </select>
            );
        } else {
            filter_options.unshift(<option key="All" value="-1">All</option>);

            selectFilter = (
                <select value={this.state.value} onChange={this.handleFilter}>
                    {filter_options}
                </select>
            );
        }

        return (
            <div id={this.props.id} className={"filter-select input-field " + css_classes}>
                {selectFilter}
                <label className={this.props.labelClasses}>{this.props.verboseName}</label>
            </div>
        );
    }
});
filter_components['select'] = CedarListFilterSelect;

var GenericButton = React.createClass({
    handleButtonClick: function(e) {
        this.props.handleButtonClick();
    },
    render: function() {
        return (
            <div className={"generic-button " + this.props.cssClasses}>
                <a className={"waves-effect waves-light btn " + this.props.buttonCssClasses} onClick={this.handleButtonClick}>{this.props.text}</a>
            </div>
        );
    }
});

var CedarList = React.createClass({
    getDefaultFilterValues: function () {
        let filter_defaults = {};
        for (let filter of this.props.filters) {
            if (!filter.is_multiple && !filter.disallow_reset) {
                filter_defaults[filter.name] = filter.default_value;
            } else if (filter.disallow_reset && this.state && this.state.filters[filter.name]) {
                // If we exclude this filter from reset, maintain its previous state if it exists.
                filter_defaults[filter.name] = this.state.filters[filter.name];
            } else {
                // It all else fails fall back to the provided default.
                // This happens whenever the previous localStorage is lost.
                filter_defaults[filter.name] = filter.default_value;
            }
        }

        return filter_defaults;
    },
    getDefaultState: function() {
        let state = {
            // pageSize: this.props.defaultPageSize,
            //sort: '-id',
            currentPage: 0,
            maxPages: 0,
            count: 0,
            search: '',
            filters: this.getDefaultFilterValues(),
            hasInitialFilters: false,
            data: []
        };

        state.pageSize = this.props.defaultPageSize;
        if (this.props.showPager == 0) {
            state.pageSize = -1;
        } else if (this.state && this.state.pageSize) {
            state.pageSize = this.state.pageSize;
        }

        state.sort = this.props.defaultSort;
        if (this.state && this.state.sort) {
            state.sort = this.state.sort;
        }

        return state;
    },
    getInitialState: function() {
        let state;
        let initial_filters = {};
        // Check if filters have initial values past.  We only want to load them once!
        for (let filter of this.props.filters) {
            // Check specifically for undefined, because we want to allow zero or null values.
            if (typeof filter.initial_value !== 'undefined' && filter.initial_value !== 'undefined') {
                initial_filters[filter.name] = filter.initial_value;
            }
        }
        const initial_filters_exist = (Object.keys(initial_filters).length > 0);

        const storage_key = this.getStorageKey();
        const storage_string = localStorage.getItem(storage_key);

        // We only want to use the storage string if there's no initial values.
        if (storage_string && !initial_filters_exist) {
            state = JSON.parse(storage_string);
        } else {
            // Default state...
            state = this.getDefaultState();
        }

        if (initial_filters_exist) {
            let default_filters = this.getDefaultFilterValues();
            $.extend(default_filters, initial_filters);

            state.filters = default_filters;
            state.hasInitialFilters = true;
        }

        // TODO delete this line some time after all the broken lists are happy :)
        state['data'] = [];

        // If this is a print page/report fetch the report only state.
        state['search'] = "";  // We can't blank this line on update or search breaks :)
        if (window.location.pathname.substring(0, window.location.pathname.length - 1).match(/\/report$/)) {
            const report_storage_string = localStorage.getItem(storage_key + "-report");
            if (report_storage_string) {
                let report_state = JSON.parse(report_storage_string);
                $.extend(state, report_state);
            }
        }

        return state;
    },
    getStorageKey: function () {
        // Generate a unique storage string based off the list name and the current path.
        let key = this.props.name + window.location.pathname.substring(0, window.location.pathname.length - 1).replace(/\//ig, '-');

        // By convention, print pages all end in /report/
        // We want to use the same state as the non-report pages.
        if (key.match(/-report$/)) {
            key = key.replace(/-report$/, '');
        }

        return key;
    },
    updateCountElement: function () {
        let start, end;

        // Need to convert these all to integers for math!  Strings to screwy things.
        const currentPage = parseInt(this.state.currentPage, 10);
        const pageSize = parseInt(this.state.pageSize, 10);
        const count = parseInt(this.state.count, 10);

        start =  currentPage * pageSize + 1;
        end = start + pageSize - 1;
        if (end > count) {
            end = count;
        }

        const count_html = start + " - " + end + " of " + count;
        $('.' + this.props.name + '-count').each(function () {
            $(this).html(count_html);
        });
    },
    loadCedarListData: function() {
        console.log('Loading Data...');
        var spinner = $('.progress');

        var filter_parts = [];
        $.each(this.state.filters, function(key, value) {
            if (value && value != -1) {
                if (value.constructor === Array) {
                    for (var i of value) {
                        filter_parts.push(key + "=" + i);
                    }
                } else {
                    filter_parts.push(key + "=" + value);
                }
            }
        });

        var query_start = '?';
        if (this.props.url.split('?').length > 1) {
            query_start = '&';
        }

        var page_query = query_start;
        if (this.state.pageSize > 0) {
            page_query += "limit=" + this.state.pageSize + "&offset=" + this.state.currentPage * this.state.pageSize + "&";
        }
        var ajax_url = this.props.url + page_query + 'search=' + this.state.search + '&' + filter_parts.join('&') + '&ordering=' + this.state.sort;

        spinner.css('visibility', 'visible');
        $.ajax({
            url: ajax_url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log("list results:", data);

                var results = data.results || data;
                var data_count = data.count || results.length;

                var max_pages = 1;
                if (this.state.pageSize > 0) {
                    max_pages = Math.ceil(data_count / this.state.pageSize);
                }

                let update_state = {
                    data: results,
                    count: data_count,
                    maxPages: max_pages
                };

                this.setState(update_state);

                spinner.css('visibility', 'hidden');

                // On update... trigger an event that goes by [list-name]-updated and pass the current state.
                $( window ).trigger(this.props.name + '-updated', $.extend(this.state, update_state));

            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function() {
        console.log('Cedar List component loaded...');
        this.loadCedarListData();

        const filters_node = $(ReactDOM.findDOMNode(this)).find('ul.filters');
        filters_node.collapsible();

        if ($(window).width() <= 991)  { // Not great.  This is the pixels for medium and down in materializecss
            filters_node.find('li div.collapsible-header').first().removeClass('active');
            filters_node.collapsible('close', 0)
        } else {
            filters_node.find('li div.collapsible-header').first().addClass('active');
            filters_node.collapsible('open', 0)
        }
    },
    componentDidUpdate: function() {
        this.updateCountElement();

        if (!this.state.hasInitialFilters) {
            // This is a good place to save the current state.
            const storage_key = this.getStorageKey();

            // Replace data with an empty list to save space and prevent issues with the prerender.
            var state_without_data = this.state;
            state_without_data['data'] = [];
            delete state_without_data.hasInitialFilters;  // We don't want to store whether there are initial filters..

            const storage_string = JSON.stringify(state_without_data);
            localStorage.setItem(storage_key, storage_string);

            // Store a second localStorage entry for reports.  It contains only the search query for now.
            const report_state = {
                search: this.state.search
            };
            const report_storage_string = JSON.stringify(report_state);
            localStorage.setItem(storage_key + "-report", report_storage_string);
        }
    },
    handleSearch: function(filter_name, search) {
        this.setState({
            currentPage: 0,
            search: search
        }, this.loadCedarListData);
    },
    setPage: function(page) {
        this.setState({
            currentPage: page
        }, this.loadCedarListData);
    },
    setPageSize: function(page_size) {
        this.setState({
            pageSize: page_size,
            currentPage: 0
        }, this.loadCedarListData);
    },
    setFilter: function(name, value) {
        var filterState = this.state.filters;

        var find_filter = function(filter, index, a) {
            return filter.name == this // This is 'name'
        };
        var filter_settings = this.props.filters.find(find_filter, name);

        if (filter_settings.is_multiple && value.length == 0) {
            // For some reason it seems an empty multiselect filter needs to be absent from the url to work properly...
            delete filterState[name];
        } else {
            filterState[name] = value;
        }
        this.setState({
            filters: filterState,
            currentPage: 0
        }, this.loadCedarListData);
    },
    setSort: function(sort) {
        this.setState({
            sort: sort,
            currentPage: 0
        }, this.loadCedarListData);
    },
    resetState: function() {
        var state = this.getDefaultState();

        $( document ).trigger(this.props.resetEvent + '-search');

        // Removed sort and page size from the reset event.
        // $( document ).trigger(this.props.resetEvent + '-page-size');
        // $( document ).trigger(this.props.resetEvent + '-sort');

        for (var filter of this.props.filters) {
            if (!filter.disallow_reset) {
                var filter_value =  this.state.filters[filter.name] || -1;
                $( document ).trigger(this.props.resetEvent + '-' + filter.name);
            }
        }

        this.setState(state, this.loadCedarListData);
    },
    render: function () {
        console.log('CedarList render function starting...');
        var filters = [];

        var mainClasses = "col s12";
        var filterClasses = "col s12";

        var listStyle = {
            overflowX: 'auto'
        };
        var filterStyle = {};

        var pager = "";
        if (this.props.showPager != 0) {
            pager = <CedarListPager
                currentPage={this.state.currentPage}
                maxPages={this.state.maxPages}
                pageSize={this.state.pageSize}
                count={this.state.count}
                setPage={this.setPage}
            />;
        }

        var search = "";
        if (this.props.showSearch != 0) {
            //search = <CedarListSearch handleSearch={this.handleSearch} />;
            search = <CedarListFilterText
                key="cedar-list-search"
                name="search"
                verboseName="Filter"
                id="cedar-list-search"
                currentValue={this.state.search}
                defaultValue=""
                handleFilter={this.handleSearch}
                resetEvent={this.props.resetEvent}
            />
        }

        var page_size_select = "";
        if (this.props.showSetPageSize != 0) {
            var page_size_options = this.props.pageSizeOptions;
            page_size_select = <PageSizeSelect
                pageSizeOptions={page_size_options}
                currentValue={this.state.pageSize}
                defaultValue={this.props.defaultPageSize}
                resetEvent={this.props.resetEvent}
                setPageSize={this.setPageSize}
                cssClasses="col s12"
            />;
        }

        var sort_select = "";
        if (this.props.showSetSort != 0) {
            var sort_options = this.props.sortFieldOptions;
            sort_select = <SortSelect
                sortOptions={sort_options}
                currentSort={this.state.sort}
                defaultSort={this.props.defaultSort}
                resetEvent={this.props.resetEvent}
                setSort={this.setSort}
                cssClasses="col s12"
            />;
        }

        if (this.props.showFilters != 0) {
            mainClasses = "col s12 m12 l9 pull-l3";
            filterClasses = "col s12 m12 l3 push-l9";

            for (let filter of this.props.filters) {
                let Component = filter_components[filter.component];
                filters.push(
                    <div key={filter.id} className="row">
                        <Component
                            name={filter.name} // Global filter options
                            verboseName={filter.verbose_name}
                            id={filter.id}
                            options={filter.options}
                            currentValue={this.state.filters[filter.name]}
                            defaultValue={filter.default_value}
                            handleFilter={this.setFilter}
                            labelClasses={filter.labelClasses}
                            resetEvent={this.props.resetEvent}
                            selectType={filter.select_type} // Select list options
                            isMultiple={(filter.is_multiple === true || filter.is_multiple === 'true')}
                            selectYears={filter.select_years} // Date options
                            limitYears={filter.limit_years}
                        />
                    </div>
                )
            }
        }
        this.filters = filters;

        // var filter_styles = {
        //     background: 'white',
        //     boxShadow: '0 1px 5px #000000',
        //     padding: '10px',
        //     position: 'fixed',
        //     right: 0,
        //     zIndex: 1000
        // };

        var reset_button = "";
        if (this.props.resetEvent) {
            var button_text = (<span><i className="material-icons left">restore</i>Reset Filters</span>);
            reset_button = <GenericButton
                text={button_text}
                cssClasses="col s12"
                buttonCssClasses="btn-flat white grey-text text-darken-1 right"
                handleButtonClick={this.resetState}
            />;
        }

        var ListComponent;
        if (this.props.listComponent) {
            ListComponent = this.props.listComponent;
        } else if (this.props.listType) {
            if (this.props.listType == 'table') {
                ListComponent = CedarListTable;
            }

        }

        var filter_section = '';
        if (this.props.showFilters != 0) {
            filter_section = (
                <div className={filterClasses} style={filterStyle}>
                    <div style={{height: "1em"}}/>
                    <div className="hide-on-print">
                        {reset_button}
                        <div className="col s12">
                            <ul className="filters">
                                <li>
                                    <div className="collapsible-header">
                                        <i className="material-icons">filter_list</i> Filters
                                    </div>
                                    <div className="collapsible-body">
                                        {page_size_select}
                                        {sort_select}
                                        {this.filters}
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            );
        }

        return (
            <div className="cedarList">
                <div className="row">
                    {filter_section}
                    <div className={mainClasses}>
                        {search}
                        {pager}
                        <div className="col s12" style={listStyle}>
                            <ListComponent data={this.state.data} fields={this.props.fields} />
                        </div>
                        {pager}
                    </div>
                </div>
            </div>
        );
    }
});

window.CedarList = CedarList;

var cedar_list_settings = Window.cedarListSettings;
console.log("cedar_list.jsx", cedar_list_settings);

if (cedar_list_settings) {
    $.each(cedar_list_settings, function(list_name, list_settings) {
        ReactDOM.render(
            <CedarList name={list_name}
                       url={list_settings.ajax_url}
                       showPager={list_settings.show_pager}
                       showSearch={list_settings.show_search}
                       showSetPageSize={list_settings.show_set_page_size}
                       defaultPageSize={list_settings.default_page_size}
                       showSetSort={list_settings.show_set_sort}
                       defaultSort={list_settings.default_sort}
                       showReset={list_settings.show_reset}
                       showFilters={list_settings.show_filters}
                       filters={list_settings.filters}
                       resetEvent={list_settings.reset_event}
                       listComponent={list_settings.list_component}
                       pageSizeOptions={list_settings.page_size_options}
                       sortFieldOptions={list_settings.sort_field_options}
                       fields={list_settings.fields}
                       listType={list_settings.list_type}
            />,
            document.getElementById(list_settings.attach_id)
        );
    });
}
