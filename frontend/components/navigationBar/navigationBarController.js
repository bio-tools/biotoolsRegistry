angular.module('elixir_front')
.directive('navigationBar', [function() {
	return {
		restrict: 'A',
		templateUrl: 'components/navigationBar/navigationBar.html',
		link: function(scope, element, attrs) {
			scope.showSearch = scope.toState.name != "home";
			scope.$watch(function(){
				return scope.toState.name
			}, function(newVal, oldVal){
    			scope.showSearch = (scope.toState.name != "home");
			}) 
		}
	}
}])
.controller('NavbarController', ['$scope', 'djangoAuth', 'User', '$stateParams', '$timeout', 'Domain', '$state', function($scope, djangoAuth, User, $stateParams, $timeout, Domain, $state) {
	// reference the service
	var vm = this;

	$scope.User = User;
	$scope.Domain = Domain;
	
	$timeout(function() {
		Domain.load($stateParams['domain']);
	}, 500);

	$scope.logoutButtonClick = function() {
		djangoAuth.logout();
	};

	$scope.homeButtonClicked = function() {
		$scope.Domain.unload();
		$state.go('home');
	};

	$scope.aboutButtonClicked = function() {
		$scope.Domain.unload();
		$state.go('about');
	};


}]);