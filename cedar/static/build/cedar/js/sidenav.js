(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

$(document).ready(function () {

    // Initialize Materialize components that might be on the page:
    $('.button-collapse').sideNav({
        menuWidth: 260, // Default is 240
        edge: 'left',
        closeOnClick: false
    });

    $('ul.tabs').tabs();

    // Current page url must be set in the template.
    activate_nav_li(current_nav_url);
});

function activate_nav_li(page_url) {
    //console.log("page url:", page_url);
    var link_selector_text = 'a[href="' + page_url + '"]'; //Change to href^= for a 'startswith' search
    var anchors = $('nav').find($(link_selector_text));
    var target_anchor;

    if (anchors.length == 0) {
        console.log("side-nav warning: no href matches found for:", link_selector_text);
        // Loosen href search, try again, and take first value:
        link_selector_text = 'a[href^="' + page_url + '"]'; //Change to href^= for a 'startswith' search
        anchors = $('nav').find($(link_selector_text));

        console.log("side-nav warning: re-tried href search with", link_selector_text, anchors.length, 'were found.');
        target_anchor = anchors[0];
    } else {
        if (anchors.length > 1) {
            //Warn and take the first one returned:
            console.log("side-nav warning: current page related to more than one nav link.");
            console.log("found", anchors.length, "element(s).");
        }
        target_anchor = anchors[0];
    }

    var app_level_nav = $(target_anchor).parent().parent().parent().parent();

    // Open collapsible:
    $(app_level_nav).find('div.collapsible-header').addClass('active');

    // Highlight page:
    $(target_anchor).parent().addClass('grey lighten-3');
}

},{}]},{},[1]);
