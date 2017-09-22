$(document).ready(function () {
    // Declare some local globals.
    cedar = {
        spinner: $('.progress'),
        tbody: $('#datatable tbody'),
        controls: $('#con-hor, #con-vert'),
    }
    //load_data('../api/interview/');
    load_data(interview_ajax_url);
});

function load_data(url){

    cedar.spinner.css('visibility', 'visible');
    cedar.tbody.empty();
    cedar.controls.css('opacity', 0.1)

    $.get( url, function(result) {
        console.log("result:", result);
        // If the data was requested with a limit or offsets it is returned in a different structure,
        // standardize it if need be.
        if (result.hasOwnProperty('results')) {
            result = result.results
        }

        for (var i = 0; i < result.length; i++) {
            var datum = result[i];
            if (datum.primary_interviewer){
                if (datum.primary_interviewer.initials != null){
                    var initials = datum.primary_interviewer.initials;
                }
                else{
                    var initials = datum.primary_interviewer;
                }
            }
            cedar.tbody.append(
                '<tr> \
                    <td class="extra-tight-table-row"><a href="' + datum.url_page + '">VIEW</a></td> \
                    <td class="extra-tight-table-row">' + datum.project_name + '</td> \
                    <td class="extra-tight-table-row">' + initials + '</td> \
                    <td class="extra-tight-table-row">' + datum.participant_number + '</td> \
                </tr>'
            );
        }

        cedar.spinner.css('visibility', 'hidden');
        cedar.controls.css('opacity', 1)


        cedar.datatable = $('#datatable').DataTable({
            //"dom":' <"search-box"f><"top"l>rt<"bottom"ip><"clear">',
            'dom':'t',  // Just the table, no controls.
            'pagingType': 'simple',
            'bPaginate': enable_pagination,
            // 'searchDelay' : 500,     //ignored due to external search box
            "columnDefs": [
                {"orderable": false, "targets": 0}  //disable sort on View column
            ],
            "order": [[1, "asc"]]   //default order on Project column, asc
        });


        update_table_info()
        
        $('#search-box').typeWatch({
            wait: 550,
            callback: function (value) {
                cedar.datatable.search(value).draw();
            },
            captureLength: 1,
            allowSubmit: true,
        });

    });
}

function update_table_info() {
    var info = cedar.datatable.page.info();
}
