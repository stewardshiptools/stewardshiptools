var React = require('react');
var ReactDOM = require('react-dom');

// This is where you'd setup an item, or a row.
var Project = React.createClass({
    render: function() {
        var columns = [];
        columns.push((
            <td className="extra-tight-table-row" key={this.props.data.id + '-name'}><a href={this.props.data.url}>{this.props.data.cedar_project_name}</a></td>));
        columns.push((
            <td className="extra-tight-table-row" key={this.props.data.id + '-code'}>{this.props.data.cedar_project_code}</td>));

        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-start-date'}>{this.props.data.start_date}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-end-date'}>{this.props.data.end_date}</td>));

        return (
            <tr>
                {columns}
            </tr>
        );
    }
});

// This is where to setup any list wrappers, like tables.
var ProjectList = React.createClass({
    render: function() {
        var projectNodes = this.props.data.map(function(project) {
            return (
                <Project key={project.id} data={project} />
            );
        });

        var headers = [];

        headers.push((<th key="name" data-field="cedar_project_name">Name</th>));
        headers.push((<th key="code" data-field="cedar_project_code">Harvest Code</th>));
        headers.push((<th key="start-date" data-field="start_date">Start date</th>));
        headers.push((<th key="end-date" data-field="end_date">End date</th>));

        return (
            <div className="projectList">
                <table className="">
                    <thead>
                        <tr>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {projectNodes}
                    </tbody>
                </table>
            </div>
        );
    }
});

const reset_event = "CedarListResetState";

const page_size_options = [5, 10, 25, 50, 100, 500, 1000];

const sort_field_options = [
    ['id', 'ID'],
    ['cedar_project_name', 'Name'],
    ['start_date', 'Start date'],
    ['end_date', 'End date']
];

/**
 * var filters
 *
 * This should be an array with each element being a dictionary describing a filter.
 * each element should provide the following values:
 *  - name: the value that your ViewSet expects to see in the url to identify the filter
 *  - verboseName: the verbose name you'd like to show up in the filter's label
 *  - id: an ID for the filter's id html attribute
 *  - options: an array where each element is
 */
var filters = [
    {
        'name': 'id',
        'verbose_name': 'ID',
        'id': 'id-filter',
        'default_value': '',
        'component': "text",
    }
];

if (!Window.cedarListSettings) {
    Window.cedarListSettings = {};
}

var list_settings = {
    ecosystem_projects: {
        attach_id: ecosystemsproject_list_attach_id,
        ajax_url: ecosystemsproject_list_ajax_url,
        show_pager: ecosystemsproject_list_show_pager,
        show_search: ecosystemsproject_list_show_search,
        show_set_page_size: ecosystemsproject_list_show_set_page_size,
        default_page_size: ecosystemsproject_list_default_page_size,
        show_set_sort: ecosystemsproject_list_show_set_sort,
        default_sort: ecosystemsproject_list_default_sort,
        show_reset: ecosystemsproject_list_show_reset,
        filters: filters,
        reset_event: reset_event,
        list_component: ProjectList,
        page_size_options: page_size_options,
        sort_field_options: sort_field_options
    }
};

$.extend(Window.cedarListSettings, list_settings);
console.log("project_list.jsx:", Window.cedarListSettings);
