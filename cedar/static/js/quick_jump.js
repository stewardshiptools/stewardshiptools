/* USE AS REFERENCE */
function formatResult(result) {
    if (result.loading) {
        return result.text;
    }
    else {
        var markup = "<div data-url='" + result.url + "'>" + result.cedar_project_code + "<a href='" + result.url + "'>" + result.cedar_project_name + "</a></div>";
        return markup;
    }
}

/* USE AS REFERENCE */
function formatResultSelection(result_selection) {
    return result_selection.cedar_project_code || result_selection.text;
}

/* USE AS REFERENCE
* Note: I saw this mentioned in a repo but it doesn't work.
* */
function formatInputTooShort(param_1, param_2) {
    console.log("param:", param);
    return "Enter project code number";
}


function prepare_quickjump(options) {
    /*
    formatResult: function defines how results are html formatted.
    formatResultSelection: function defines how selected result is html formatted.

    quick jump assums the response data has a property "url" that the page will be redirected to.

    options = {
        filter_field: "id",
        jump_url_property: "url",
        query_url: "{% url 'development:api:project-list' %}?",
        placeholder: 'Jump to project'
        formatResult: null ,
        formatResultSelection: null
    };
    */

    $("select.quickjump").select2({
        ajax: {
            url: options.query_url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                console.log(params);
                var data_params = {};
                data_params[options.filter_field] = params.term;
                data_params["page"] = params.page;
                // return {
                //     id: params.term,    // filter parameter & term.
                //     page: params.page
                // };
                return data_params;
            },
            processResults: function (data, params) {
                console.log("process results:", data, params);
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;

                return {
                    results: data,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        formatInputTooShort: function (input, min){return "HI";},    // this wasn't taking.
        minimumInputLength: 1,
        placeholder: 'Jump to project',
        templateResult: options.formatResult, // omitted for brevity, see the source of this page
        templateSelection: options.formatResultSelection // omitted for brevity, see the source of this page

    });
    $('.quickjump').on('select2:select', function (evt) {
        window.location.href = evt.params.data[options.jump_url_property];
    });
}