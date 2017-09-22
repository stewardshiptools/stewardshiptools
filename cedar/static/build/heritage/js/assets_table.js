(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

$(document).ready(function () {
    // Declare some local globals.
    cedar = {
        spinner: $('.progress'),
        tbody: $('#asset_datatable tbody'),
        controls: $('#con-hor, #con-vert')
    };

    wipe_datatable();

    //Pull and append new data:
    $.when(load_data(assets_interviews_ajax_url), load_data(assets_sessions_ajax_url)).done(init_datatable); //Re-init the table when ajaxes are done.
});

function load_data(url) {
    return $.get(url, function (result) {
        //console.log("result:", result);
        // If the data was requested with a limit or offsets it is returned in a different structure,
        // standardize it if need be.
        if (result.hasOwnProperty('results')) {
            result = result.results;
        }
        for (var i = 0; i < result.length; i++) {
            var datum = result[i];
            var delete_url = datum.delete_url;
            var delete_anchor = ' \
                <a class="waves-grey lighten-5 grey-text text-darken-1 tooltipped-secureasset-delete" href="' + delete_url + '" \
                    data-tooltip="Delete File" data-position="left"> \
                    <i class="material-icons" style="font-size:inherit;">delete</i> \
                </a>';

            cedar.tbody.append('<tr> \
                    <td class="extra-tight-table-row"><a href="' + datum.url + '">' + datum.name + '</a></td> \
                    <td class="extra-tight-table-row">' + (datum.session_num ? datum.session_num : "") + '</td> \
                    <td class="extra-tight-table-row"><span style="white-space: nowrap;">' + datum.modified + '</span></td> \
                    <td class="extra-tight-table-row">' + datum.file_size + '</td> \
                    <td class="extra-tight-table-row">' + delete_anchor + '</td> \
                </tr>');
        }
    });
}

function init_datatable() {

    cedar.spinner.css('visibility', 'hidden');
    cedar.controls.css('opacity', 1);

    cedar.asset_datatable = $('#asset_datatable').DataTable({
        //"dom":' <"search-box"f><"top"l>rt<"bottom"ip><"clear">',
        'dom': 't', // Just the table, no controls.
        'pagingType': 'simple',
        'bPaginate': enable_pagination,
        "bSort": true,
        "order": [[0, "asc"]] //default order on Filename column, asc
    });

    // Allow Materialize to "upgrade" the select DataTables just created.
    $('select').material_select();

    update_table_info();

    $('#search-box').typeWatch({
        wait: 550,
        callback: function callback(value) {
            cedar.asset_datatable.search(value).draw();
        },
        captureLength: 1,
        allowSubmit: true
    });

    $('#page-length').change(function () {
        cedar.asset_datatable.page.len($(this).val()).draw();
        update_table_info();
    });

    $('#page-previous').on('click', function () {
        cedar.asset_datatable.page('previous').draw('page');
        update_table_info();
    });

    $('#page-next').on('click', function () {
        cedar.asset_datatable.page('next').draw('page');
        update_table_info();
    });
}

function wipe_datatable() {
    cedar.spinner.css('visibility', 'visible');
    cedar.tbody.empty();
    cedar.controls.css('opacity', 0.1);
}

function update_table_info() {
    var info = cedar.asset_datatable.page.info();
    $('#page-start').text(info.start);
    $('#page-end').text(info.end);
    $('#record-length').text(info.recordsTotal);
}

},{}]},{},[1]);
