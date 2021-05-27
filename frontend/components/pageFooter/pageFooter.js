angular.module('elixir_front')
.directive('pageFooter', [function() {
	return {
		restrict: 'A',
		templateUrl: 'components/pageFooter/pageFooter.html',
		link: function(scope, element, attrs) {

		}
	}
}])