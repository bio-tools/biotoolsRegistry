// required
var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    plumber = require('gulp-plumber'),
    concat = require('gulp-concat'),
    concatCss = require('gulp-concat-css'),
    urlAdjuster = require('gulp-css-url-adjuster'),
    cleanCss = require('gulp-clean-css'),
    sourcemaps = require('gulp-sourcemaps'),
    rename = require('gulp-rename');

// copy
gulp.task('copy', function () {
    // angular-tree-control
    gulp.src('node_modules/angular-tree-control/images/*.png').pipe(
        gulp.dest('dist/images/angular-tree-control')
    );
    // font-awesome
    gulp.src('node_modules/font-awesome/fonts/*.*').pipe(gulp.dest('dist/fonts'));
    // glyphicons
    gulp.src('node_modules/bootstrap/dist/fonts/*.*').pipe(gulp.dest('dist/fonts'));
    // ui-grid
    gulp.src('node_modules/angular-ui-grid/ui-grid.eot').pipe(gulp.dest('dist/fonts'));
    gulp.src('node_modules/angular-ui-grid/ui-grid.svg').pipe(gulp.dest('dist/fonts'));
    gulp.src('node_modules/angular-ui-grid/ui-grid.ttf').pipe(gulp.dest('dist/fonts'));
    gulp.src('node_modules/angular-ui-grid/ui-grid.woff').pipe(gulp.dest('dist/fonts'));
});

// css
gulp.task('css', function () {
    gulp.src([
        'css/lib/abn_tree.css',
        'css/lib/ng-tags-input.css',
        'css/lib/ng-tags-input.bootstrap.css',
        'css/*.css',
        'components/**/*.css',
    ])
        .pipe(plumber())
        .pipe(concatCss('app.css'))
        .pipe(rename({ suffix: '.min' }))
        .pipe(cleanCss({ compatibility: 'ie8' }))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('dist'));
});

// scripts
gulp.task('scripts', function () {
    gulp.src(['js/**/*.js', '!js/**/*.min.js', 'components/**/*.js'])
        .pipe(plumber())
        .pipe(concat('app.js'))
        .pipe(rename({ suffix: '.min' }))
        // .pipe(uglify({ mangle: false })) // Causes false errors, need an update
        .pipe(gulp.dest('dist'));
});

// bower
gulp.task('bower', function () {
    gulp.src([
        'node_modules/lodash/lodash.min.js',
        'node_modules/angular/angular.min.js',
        'node_modules/angular-cookies/angular-cookies.min.js',
        'node_modules/angular-route/angular-route.min.js',
        'node_modules/angular-sanitize/angular-sanitize.min.js',
        'node_modules/angular-animate/angular-animate.min.js',
        'node_modules/angular-resource/angular-resource.min.js',
        'node_modules/angular-ui-router/release/angular-ui-router.min.js',
        'node_modules/angular-tree-control/context-menu.js',
        'node_modules/angular-tree-control/angular-tree-control.js',
        'node_modules/angular-ui-bootstrap/ui-bootstrap-tpls.min.js',
        'node_modules/angular-tooltips/dist/angular-tooltips.min.js',
        'node_modules/angular-timeago/dist/angular-timeago.min.js',
        'node_modules/angular-bindonce/bindonce.min.js',
        'node_modules/angular-ui-grid/ui-grid.min.js',
        'node_modules/chart.js/dist/Chart.min.js',
        'node_modules/angular-chart.js/dist/angular-chart.min.js',
        'node_modules/moment/min/moment.min.js',
        'node_modules/ng-meta/dist/ngMeta.min.js',
    ])
        .pipe(plumber())
        .pipe(concat('vendor.js'))
        .pipe(rename({ suffix: '.min' }))
        .pipe(uglify())
        .pipe(gulp.dest('dist'));

    gulp.src([
        'node_modules/bootstrap/dist/css/bootstrap.min.css',
        'node_modules/font-awesome/css/font-awesome.min.css',
        'node_modules/angular-tree-control/css/tree-control.css',
        'node_modules/angular-tree-control/css/tree-control-attribute.css',
        'node_modules/angular-tooltips/dist/angular-tooltips.min.css',
        'node_modules/angular-ui-grid/ui-grid.min.css',
    ])
        .pipe(plumber())
        // ui-grid-fonts
        .pipe(
            urlAdjuster({
                replace: ['ui-grid.', '/dist/fonts/ui-grid.'],
            })
        )
        // angular-tree-control
        .pipe(
            urlAdjuster({
                replace: ['../images', '/dist/images/angular-tree-control'],
            })
        )
        // font-awesome & glyphicons
        .pipe(
            urlAdjuster({
                replace: ['../fonts/', '/dist/fonts/'],
            })
        )
        .pipe(concatCss('vendor.css'))
        .pipe(rename({ suffix: '.min' }))
        .pipe(cleanCss({ compatibility: 'ie8' }))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('dist'));
});

// watch
gulp.task('watch', function () {
    gulp.watch('js/**/*.js', ['scripts']);
    gulp.watch('css/**/*.css', ['css']);
    gulp.watch('components/**/*.css', ['css']);
    gulp.watch('components/**/*.js', ['scripts']);
});

// default
gulp.task('default', ['copy', 'css', 'scripts', 'bower', 'watch']);
