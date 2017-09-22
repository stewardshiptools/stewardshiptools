var React = require('react');
var ReactDOM = require('react-dom');

// This is where you'd setup an item, or a row.
var Project = React.createClass({
    render: function() {
        var columns = [];
        const nowrap_style = {
            whiteSpace: 'nowrap'
        };

        var status;
        if (this.props.data.status == 'active') {
            status = <span className="badge cedar-badge green white-text">Active</span>;
        } else if (this.props.data.status == 'inactive') {
            status = <span className="badge cedar-badge grey darken-3 white-text">Inactive</span>;
        } else {
            status = this.props.data.status;
        }

        var dates = [];
        if (this.props.data.initial_date) {
            dates.push((<span style={nowrap_style}><em>{this.props.data.initial_date}</em></span>));
        }
        if (this.props.data.due_date) {
            dates.push((<span style={nowrap_style}><strong>{this.props.data.due_date}</strong></span>));
        }

        var dates_string = dates.map((item, i) => [item, <br key={i + '-date-' + 'br'} />]);

        columns.push((
            <td className="extra-tight-table-row" key={this.props.data.id + '-name'}><a href={this.props.data.url}>{this.props.data.cedar_project_name}</a></td>));

        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-dates'}>{dates_string}</td>));

        columns.push((
            <td className="extra-tight-table-row" key={this.props.data.id + '-code'}><span style={nowrap_style}>{this.props.data.cedar_project_code}</span></td>));

        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-status'}>{status}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-filing-code'}>{this.props.data.filing_code}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-company'}>{this.props.data.company}</td>));

        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-num-files'}>{this.props.data.num_files}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-num-comms'}>{this.props.data.num_comms}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-num-comments'}>{this.props.data.num_comments}</td>));
        columns.push((<td className="extra-tight-table-row" key={this.props.data.id + '-file-numbers'}>{this.props.data.file_numbers.join(', ')}</td>));

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
        headers.push((<th key="dates" data-field="cedar_project_dates">Dates</th>));
        headers.push((<th key="code" data-field="cedar_project_code">Harvest Code</th>));
        headers.push((<th key="status" data-field="status">Status</th>));
        headers.push((<th key="filing_code" data-field="filing_code">Filing Code</th>));
        headers.push((<th key="company" data-field="company">Company</th>));

        headers.push((<th key="num_files" data-field="num_files">Files</th>));
        headers.push((<th key="num_comms" data-field="num_comms">Comm.</th>));
        headers.push((<th key="num_comments" data-field="num_comments">Disc.</th>));
        headers.push((<th key="file_numbers" data-field="file_numbers">File Numbers</th>));

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
    ['id', 'Project ID'],
    ['cedar_project_name', 'Name'],
    ['initial_date_null,initial_date', 'Initial date'],
    ['due_date_null,due_date', 'Due date'],
    ['status', 'Status'],
    ['filing_code__code', 'Filing code'],
    ['company__name', 'Company']
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
        'name': 'status',
        'verbose_name': 'Status',
        'id': 'status-filter',
        'options': [['active', 'Active'], ['inactive', 'Inactive']],
        'default_value': '-1',
        'component': "select",
        'select_type': 'material',
        'disallow_reset': true
    },
    {
        'name': 'id',
        'verbose_name': 'Project ID',
        'id': 'id-filter',
        'default_value': '',
        'component': "text"
    },
    {
        'name': 'highlight',
        'verbose_name': 'Highlighted?',
        'id': 'hightlight',
        'options': [[2, 'Yes'], [3, 'No']],
        'default_value': '-1',
        'component': "select",
        'select_type': 'material'
    },
    {
        'name': 'has_geom',
        'verbose_name': 'Has location?',
        'id': 'has-geom-filter',
        'options': [['yes', 'Yes'], ['no', 'No']],
        'default_value': '-1',
        'component': "select",
        'select_type': 'material'
    },
    {
        'name': 'tag',
        'verbose_name': 'Tags',
        'id': 'tags-filter',
        'options': tags_options,
        'default_value': [],
        'component': "select",
        'labelClasses': "active",
        'select_type': 'select2',
        'is_multiple': true
    },
    {
        'name': 'people',
        'verbose_name': 'People',
        'id': 'people-filter',
        'options': people_options,
        'default_value': [],
        'component': "select",
        'labelClasses': "active",
        'select_type': 'select2',
        'is_multiple': true
    },
    {
        'name': 'organizations',
        'verbose_name': 'Organizations',
        'id': 'org-filter',
        'options': org_options,
        'default_value': [],
        'component': "select",
        'labelClasses': "active",
        'select_type': 'select2',
        'is_multiple': true
    },
    {
        'name': 'consultation_stage',
        'verbose_name': 'Consultation stage',
        'id': 'stage-filter',
        'options': consultation_stage_options,
        'default_value': '-1',
        'component': "select",
        'select_type': 'material'
    },
    {
        'name': 'filing_code',
        'verbose_name': 'Filing code',
        'id': 'filing-code-filter',
        'options': filing_code_options,
        'default_value': '-1',
        'component': "select",
        'select_type': 'material'
    },
    {
        'name': 'comments_contain',
        'verbose_name': 'Discussion text',
        'id': 'comments-filter',
        'default_value': '',
        'component': "text",
    },
    {
        'name': 'file_number',
        'verbose_name': 'File number',
        'id': 'filenumber-filter',
        'default_value': '',
        'component': "text",
    }
];

if (!Window.cedarListSettings) {
    Window.cedarListSettings = {};
}

var list_settings = {
    "project-table": {
        attach_id: developmentproject_list_attach_id,
        ajax_url: developmentproject_list_ajax_url,
        show_pager: developmentproject_list_show_pager,
        show_search: developmentproject_list_show_search,
        show_set_page_size: developmentproject_list_show_set_page_size,
        default_page_size: developmentproject_list_default_page_size,
        show_set_sort: developmentproject_list_show_set_sort,
        default_sort: developmentproject_list_default_sort,
        show_reset: developmentproject_list_show_reset,
        show_filters: developmentproject_list_show_filters,
        filters: filters,
        reset_event: reset_event,
        list_component: ProjectList,
        page_size_options: page_size_options,
        sort_field_options: sort_field_options
    }
};

$.extend(Window.cedarListSettings, list_settings);
console.log("project_list.jsx:", Window.cedarListSettings);
