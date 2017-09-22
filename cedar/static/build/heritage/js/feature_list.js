(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

/**
 * Trigger a jquery event with the name of the attach_id.  This event is used to populate the map.
 * @param attach_id
 * @param results
 */
var trigger_map = function trigger_map(attach_id, results) {
    $(document).trigger(attach_id, [results]);
};

ReactDOM.render(React.createElement(FeatureBox, { url: heritage_feature_list_ajax_url,
    showPager: heritage_feature_list_show_pager,
    showSearch: heritage_feature_list_show_search,
    featuresLoadedHook: trigger_map
}), document.getElementById(heritage_feature_list_attach_id));

},{}]},{},[1]);
