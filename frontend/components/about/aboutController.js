angular.module('elixir_front')
.controller('AboutController', ['$scope', function($scope) {
	var vm = this;
}]);


angular.module('elixir_front')
.directive('aboutContact', ['$state','$stateParams', function($state, $stateParams) {
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