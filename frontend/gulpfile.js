// required
var gulp = require('gulp'),
	uglify = require('gulp-uglify'),
	plumber = require('gulp-plumber'),
	concat = require('gulp-concat'),
	concatCss = require('gulp-concat-css'),
	urlAdjuster = require('gulp-css-url-adjuster'),
	minifyCss = require('gulp-minify-css'),
	sourcemaps = require('gulp-sourcemaps'),
	rename = require('gulp-rename');

// copy
gulp.task('copy', function () {
	// angular-tree-control
	gulp.src('bower_components/angular-tree-control/images/*.png')
	.pipe(gulp.dest('dist/images/angular-tree-control'))
	// font-awesome
	gulp.src('bower_components/font-awesome/fonts/*.*')
	.pipe(gulp.dest('dist/fonts'))
	// glyphicons
	gulp.src('bower_components/bootstrap/dist/fonts/*.*')
	.pipe(gulp.dest('dist/fonts'))
	// ui-grid
	gulp.src('bower_components/angular-ui-grid/ui-grid.eot')
	.pipe(gulp.dest('dist/fonts'))
	gulp.src('bower_components/angular-ui-grid/ui-grid.svg')
	.pipe(gulp.dest('dist/fonts'))
	gulp.src('bower_components/angular-ui-grid/ui-grid.ttf')
	.pipe(gulp.dest('dist/fonts'))
	gulp.src('bower_components/angular-ui-grid/ui-grid.woff')
	.pipe(gulp.dest('dist/fonts'))
})

// css
gulp.task('css', function() {
	gulp.src([
		'css/lib/abn_tree.css',
		'css/lib/ng-tags-input.css',
		'css/lib/ng-tags-input.bootstrap.css',
		'css/*.css',
		'components/**/*.css'
	])
	.pipe(plumber())
	.pipe(concatCss('app.css'))
	.pipe(rename({suffix:'.min'}))
	.pipe(minifyCss({compatibility: 'ie8'}))
	.pipe(sourcemaps.write())
	.pipe(gulp.dest('dist'));
});

// scripts
gulp.task('scripts', function() {
	gulp.src(['js/**/*.js', '!js/**/*.min.js','components/**/*.js',])
	.pipe(plumber())
	.pipe(concat('app.js'))
	.pipe(rename({suffix:'.min'}))
	.pipe(uglify({ mangle: false }))
	.pipe(gulp.dest('dist'));
});

// bower
gulp.task('bower', function() {
	gulp.src([
		'bower_components/lodash/dist/lodash.min.js',
		'bower_components/angular/angular.min.js',
		'bower_components/angular-cookies/angular-cookies.min.js',
		'bower_components/angular-route/angular-route.min.js',
		'bower_components/angular-sanitize/angular-sanitize.min.js',
		'bower_components/angular-animate/angular-animate.min.js',
		'bower_components/angular-resource/angular-resource.min.js',
		'bower_components/angular-ui-router/release/angular-ui-router.min.js',
		'bower_components/angular-tree-control/angular-tree-control.js',
		'bower_components/angular-bootstrap/ui-bootstrap-tpls.min.js',
		'bower_components/angular-tooltips/dist/angular-tooltips.min.js',
		'bower_components/angular-timeago/dist/angular-timeago.min.js',
		'bower_components/angular-bindonce/bindonce.min.js',
		'bower_components/angular-ui-grid/ui-grid.min.js',
		'bower_components/chart.js/dist/Chart.min.js',
		'bower_components/angular-chart.js/dist/angular-chart.min.js',
		'bower_components/moment/min/moment.min.js',
		'bower_components/ngMeta/dist/ngMeta.min.js'
	])
	.pipe(plumber())
	.pipe(concat('vendor.js'))
	.pipe(rename({suffix:'.min'}))
	//.pipe(uglify())
	.pipe(gulp.dest('dist'));
	
	gulp.src([
		'bower_components/bootstrap/dist/css/bootstrap.min.css',
		'bower_components/font-awesome/css/font-awesome.min.css',
		'bower_components/angular-tree-control/css/tree-control.css',
		'bower_components/angular-tree-control/css/tree-control-attribute.css',
		'bower_components/angular-tooltips/dist/angular-tooltips.min.css',
		'bower_components/angular-ui-grid/ui-grid.min.css',
	])
	.pipe(plumber())
	// ui-grid-fonts
	.pipe(urlAdjuster({
		replace:  ['ui-grid.','/dist/fonts/ui-grid.'],
	}))
	// angular-tree-control
	.pipe(urlAdjuster({
		replace:  ['../images','/dist/images/angular-tree-control'],
	}))
	// font-awesome & glyphicons
	.pipe(urlAdjuster({
		replace:  ['../fonts/','/dist/fonts/'],
	}))
	.pipe(concatCss('vendor.css'))
	.pipe(rename({suffix:'.min'}))
	.pipe(minifyCss({compatibility: 'ie8'}))
	.pipe(sourcemaps.write())
	.pipe(gulp.dest('dist'));
});

// watch
gulp.task('watch', function() {
	gulp.watch('js/**/*.js', ['scripts'])
	gulp.watch('css/**/*.css', ['css'])
	gulp.watch('components/**/*.css', ['css'])
	gulp.watch('components/**/*.js', ['scripts'])
});

// default
gulp.task('default', ['copy', 'css', 'scripts', 'bower', 'watch']);