var gulp = require('gulp');
require('./gulp/gulps/build_tasks.js');
require('./gulp/gulps/filesystem.js');

gulp.task('default', ['build']);
