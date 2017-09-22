(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

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
            });
        }
    });
};

},{}]},{},[1]);
