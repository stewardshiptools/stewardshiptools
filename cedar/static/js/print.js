/*

    If you want to do something before the print dialog comes up,
    create the following listener for the 'print-page:render' event:

    EG:
    $("#print-page-indicator").on('print-page:render', function(evt){
        <<DO STUFF>>
    });

*/

function isPrintPage(window) {
    return $(window).find('#print-page-indicator').first().is(':visible');
}

// Add the super secret div to the main -- tells us if we're in a print view or not.
$(document).ready(function(evt){
    $(this).find('main').first().append(
        '<div id="print-page-indicator"></div>'
    );
    set_up_print_listeners(this);
});


function set_up_print_listeners(context) {
    /*
    Listens for media matches and triggers the print-page:render event
    on the print-page-indicator div.
     */
    if ('matchMedia' in window) {
        var ppindicator = $("#print-page-indicator");

        // Chrome, Firefox, and IE 10 support mediaMatch listeners
        window.matchMedia('print').addListener(function (media) {
            if (media.matches) {
                //before print
                ppindicator.trigger("print-page:render");
            } else {
                // Fires immediately, so wait for the first mouse movement
                //after print
                // $(document).one('mouseover', afterPrint);
                ppindicator.trigger("print-page:render");
            }
        });
    } else {
        // IE and Firefox fire before/after events
        // var ppindicator = $(this).closest("#print-page-indicator");
        $(window).on('beforeprint', function () {
            ppindicator.trigger("print-page:render");
        });
        $(window).on('afterprint', afterPrint);
    }
}