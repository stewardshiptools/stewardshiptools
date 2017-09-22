
window.getUrlParameter = function getUrlParameter(sParam) {
    /*
        http://stackoverflow.com/questions/19491336/get-url-parameter-jquery-or-how-to-get-query-string-values-in-js

        http://dummy.com/?technology=jquery&blog=jquerybyexample.

        var tech = getUrlParameter('technology');
        var blog = getUrlParameter('blog');

     */
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

window.chip_hack = function () {
    console.log("removing click listeners on chips without close icons");
    $(".chip > i").each(function () {
        if ($(this).text() !== 'close') {
            $(this).click(function (e) {
                e.preventDefault;
                e.stopPropagation();
            })
        }

    });
}
