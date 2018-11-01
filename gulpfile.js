'use strict';

var gulp        = require('gulp');
var execute     = require('child_process').exec;
var sass        = require('gulp-sass');
var concat      = require('gulp-concat');
var tsc         = require('gulp-typescript');
var tscConfig   = require('./tsconfig.json');
var browserSync = require('browser-sync').create();

// Run the server
gulp.task('runserver', function() {
  var proc = execute('python3 server.py');
  // For non-linux, uncomment the line below
  // var proc = execute('python server.py');
});

// Copy the HTML templates
gulp.task('html-copy', function() {
  return gulp
    .src(['web/app/*.html', 'web/app/**/*.html'])
    .pipe(gulp.dest('web/build/app'));
});

// Compile the SASS files
gulp.task('sass-compile', function() {
  return gulp
    .src(['web/app/*.sass', 'web/app/**/*.sass'])
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(concat('all.min.css'))
    .pipe(gulp.dest('web/build'));
});

// Compile the TypeScript files
gulp.task('ts-compile', function() {
  return gulp
    .src(['web/app/*.ts', 'web/app/**/*.ts'])
    .pipe(tsc(tscConfig.compilerOptions))
    .pipe(gulp.dest('web/build/app'));
});

// Default run command
gulp.task('default', ['runserver', 'html-copy', 'sass-compile', 'ts-compile'], function() {
  browserSync.init({ proxy: 'localhost:5000' });

  // Watchers
  gulp.watch(['web/app/*.html', 'web/app/**/*.html'], ['html-copy']);
  gulp.watch(['web/app/*.scss', 'web/app/**/*.scss'], ['sass-compile']);
  gulp.watch(['web/app/*.ts', 'web/app/**/*.ts'],   ['ts-compile']);
  gulp.watch('web/**/*.*', browserSync.reload);
});
