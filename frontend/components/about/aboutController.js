angular.module('elixir_front')
.controller('AboutController', ['$scope', function($scope) {
	var vm = this;
	window.scrollTo(0, 0);
}]);


angular.module('elixir_front')
.directive('homeInfo', ['$state','$stateParams', function($state, $stateParams) {
	return {
		restrict: 'EA',
		templateUrl: 'components/about/aboutContact.html',
		scope: true,
		link: function(scope, element, attrs) {
			scope.name = attrs["name"];
			scope.initials = attrs["initials"];
			scope.role = attrs["role"];
			scope.image = attrs["image"];

		}
	}
}]);