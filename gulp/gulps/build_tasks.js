
'use strict';

var gulp      = require('gulp'),
    flatten   = require('gulp-flatten'),
    browserify = require('browserify'),

    del = require('del'),
    fs = require('fs'),
    source = require('vinyl-source-stream'),
    es = require('event-stream'),
    rename = require('gulp-rename'),

    sass      = require('gulp-sass'),
    babel     = require('gulp-babel'),
    babelify = require('babelify'),

    sass_cfg = require('../config/sass.json'),
    babel_cfg = require('../config/babel.json'),
    targets = require('../config/targets.json'),

    makeTask  = require('./util.js').makeTask;



makeTask('materialize-sass',  sass(sass_cfg),   targets.materialize, targets.build.materialize);

/*
// Simple non-CommonJS jsx translator.
gulp.task('babel', function() {

    return gulp.src(targets.jsx)
        .pipe(babel(babel_cfg))
        .pipe(flatten({ includeParents: [1, 1]}))
        .pipe(gulp.dest(targets.build.js));

});
*/

gulp.task('babel', function () {
    var files = targets.browserify;

    var tasks = files.map(function(entry) {
        return browserify({ entries: [entry] })
            .transform("babelify", {presets: ["react"]})
            .bundle()
            .pipe(source(entry))
            // rename them to have "bundle as postfix"
            .pipe(rename({
                extname: '.js'
            }))
            .pipe(flatten({ includeParents: [1, 1]}))
            .pipe(gulp.dest(targets.build.js));
    });
    // create a merged stream
    return es.merge.apply(null, tasks);
});

gulp.task('build', ['materialize-sass', 'babel']);
gulp.task('build-clean', ['clean', 'build']);
