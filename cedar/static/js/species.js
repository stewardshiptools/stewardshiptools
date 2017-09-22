$(document).ready(function () {
    // Declare some local globals.
    cedar = {
        spinner: $('.progress'),
        tbody: $('#datatable tbody'),
    }

    //load_data('../api/species/?limit=10&offset=0');
    load_data('../api/species/');

});

function load_data(url){

    cedar.spinner.css('visibility', 'visible');
    cedar.tbody.empty();

    $.get( url, function(result) {

        for (var i = 0; i < result.length; i++) {
            var datum = result[i];

            cedar.tbody.append(
                '<tr> \
                    <td><a href="' + datum.id + '">' + datum.description + '</a></td> \
                    <td>' + datum.species_group.name + '</td> \
                </tr>'
            );
        }

        cedar.spinner.css('visibility', 'hidden');

        cedar.datatable = $('#datatable').DataTable({
            //"dom":' <"search-box"f><"top"l>rt<"bottom"ip><"clear">',
            'dom':'t',  // Just the table, no controls.
            'pagingType': 'simple',
        });

        // Allow Materialize to "upgrade" the select DataTables just created.
        $('select').material_select();

        update_table_info()

        // Tie the search box in to the DataTable API.
        $('#search-box').keyup( function() {
            cedar.datatable.search( this.value ).draw();
        });

        $('#page-length').change( function() {
            cedar.datatable.page.len( $(this).val() ).draw();
            update_table_info()
        });

        $('#page-previous').on( 'click', function () {
            cedar.datatable.page( 'previous' ).draw( 'page' );
            update_table_info()
        } );

        $('#page-next').on( 'click', function () {
            cedar.datatable.page( 'next' ).draw( 'page' );
            update_table_info()
        } );

    });
}

function update_table_info() {
    var info = cedar.datatable.page.info()
    $('#page-start').text(info.start)
    $('#page-end').text(info.end)
    $('#record-length').text(info.recordsTotal)
}

