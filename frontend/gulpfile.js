// required
var gulp = require('gulp'),
    plumber = require('gulp-plumber'),
    concat = require('gulp-concat'),
    concatCss = require('gulp-concat-css'),
    minifyCss = require('gulp-minify-css'),
    sourcemaps = require('gulp-sourcemaps'),
    rename = require('gulp-rename');
    through = require('through2'),
    PluginError = require('plugin-error');


// rewriter for vendor CSS
function rewriteVendorUrls() {
  return through.obj(function (file, enc, cb) {
    if (file.isNull()) {
      return cb(null, file);
    }
    if (file.isStream()) {
      this.emit('error', new PluginError('rewriteVendorUrls', 'Streaming not supported'));
      return cb();
    }

    var contents = file.contents.toString('utf8');

    // Apply replacements in order
    contents = contents
      .replace(/\.\.\/\.\.\/\.\.\/font-awesome\/fonts\//g, '/dist/fonts/')
      .replace(/\.\.\/fonts\//g, '/dist/fonts/');

    file.contents = Buffer.from(contents, 'utf8');
    cb(null, file);
  });
}


// copy
gulp.task('copy', function copyTask() {
  return gulp.src([
    'bower_components/angular-tree-control/images/*.png',
    'bower_components/font-awesome/fonts/*.*',
    'bower_components/bootstrap/dist/fonts/*.*',
    'bower_components/angular-ui-grid/ui-grid.eot',
    'bower_components/angular-ui-grid/ui-grid.svg',
    'bower_components/angular-ui-grid/ui-grid.ttf',
    'bower_components/angular-ui-grid/ui-grid.woff'
  ], {
    encoding: false
  })
  .pipe(gulp.dest('dist/fonts'));
});


// css
gulp.task('css', function cssTask() {
    return gulp.src([
        'css/lib/abn_tree.css',
        'css/lib/ng-tags-input.css',
        'css/lib/ng-tags-input.bootstrap.css',
        'css/*.css',
        'components/**/*.css'
    ])
    .pipe(plumber())
    .pipe(concatCss('app.css'))
    .pipe(rename({suffix: '.min'}))
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('dist'));
});


// scripts
gulp.task('scripts', function scriptsTask() {
    return gulp.src([
        'js/**/*.js', 
        '!js/**/*.min.js', 
        'components/**/*.js'
    ])
    .pipe(plumber())
    .pipe(concat('app.js'))
    .pipe(rename({suffix: '.min'}))
    .pipe(gulp.dest('dist'));
});


// bower
gulp.task('bower', function bowerTask() {
    return gulp.src([
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
    .pipe(rename({suffix: '.min'}))
    .pipe(gulp.dest('dist'));
});


// vendor css
gulp.task('css-vendor', function vendorCssTask() {
  return gulp.src([
    'bower_components/bootstrap/dist/css/bootstrap.min.css',
    'bower_components/font-awesome/css/font-awesome.min.css',
    'bower_components/angular-tooltips/dist/angular-tooltips.min.css',
    'bower_components/angular-ui-grid/ui-grid.min.css'
  ], {
    encoding: false
  })
  .pipe(plumber())
  .pipe(rewriteVendorUrls())
  .pipe(concatCss('vendor.css'))
  .pipe(rename({suffix: '.min'}))
  .pipe(minifyCss({compatibility: 'ie8'}))
  .pipe(gulp.dest('dist'));
});


// watch (development only)
gulp.task('watch', function watchTask() {
    gulp.watch('js/**/*.js', gulp.series('scripts'));
    gulp.watch('css/**/*.css', gulp.series('css'));
    gulp.watch('components/**/*.css', gulp.series('css'));
    gulp.watch('components/**/*.js', gulp.series('scripts'));
});


// build (production/Docker - NO WATCH)
gulp.task('build', gulp.parallel('copy', 'css', 'scripts', 'bower', 'css-vendor'));


// default (development - with watch)
gulp.task('default', gulp.series('build', 'watch'));
