angular.module('elixir_front')
.directive('cookieBanner', function() {
  return {
    restrict: 'E',
    templateUrl: 'components/cookieBanner/cookieBanner.html',
    controller: function($scope) {
      $scope.cookiesAccepted = localStorage.getItem('cookiesAccepted') === 'true';

      $scope.acceptRequiredCookies = function() {
        $scope.cookiesAccepted = true;
        localStorage.setItem('cookiesAccepted', 'required');
      };

      $scope.acceptCookies = function() {
        $scope.cookiesAccepted = true;
        localStorage.setItem('cookiesAccepted', 'true');
      
        // Load Google Analytics
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
      
        ga('create', 'G-9RWP2H84XB');
        ga('send', 'pageview');
      };

      if (localStorage.getItem('cookiesAccepted') === 'true') {
        // User already accepted before, load GA immediately
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
      
        ga('create', 'UA-63650187-1', 'auto');
        ga('send', 'pageview');
      }
    }
  };
});
