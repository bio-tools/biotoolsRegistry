// Controllers
angular.module('elixir_front.controllers').controller('PermissionsController', ['$scope', 'UserSuggestionsProvider', function($scope, UserSuggestionsProvider) {
	var vm = this;

	// Typeahead Support
	$scope.userSuggestions = function(prefix) {
		return UserSuggestionsProvider.getSuggestions(prefix).then(function(data) {
			var suggestions = _.map(data, function(obj){
				return obj.username;
			});
			return _.difference(suggestions, $scope.software.editPermission.authors);
		});
	};

	$scope.userSelected = function($item, $model, $label) {
		// Initialize authors if not present.
		if ($scope.software.editPermission.authors == undefined) {
			$scope.software.editPermission.authors = [];
		}
		// Clear the input field on selection.
		$scope.userSuggestion = '';
		$scope.software.editPermission.authors.push($model);
	};

	$scope.isSoftwareOwner = function() {
		if ($scope.software.owner == $scope.User.getUsername()) {
			return true;
		}
		return false;
	}

	$scope.deleteUser = function(index) {
		$scope.software.editPermission.authors.splice(index, 1);
	}
}]);

// Services and Factories
var elixir_front = angular.module('elixir_front');
elixir_front.factory('UserSuggestionsProvider', ['$http', function ($http) {
	return {
		getSuggestions: function(prefix) {
			return $http({
				method: 'GET',
				url: '/api/user-list',
				params: {term: prefix}
			}).then(function successCallback(response) {
				return response.data;
			}, function errorCallback(response) {
				return {};
			})
		}
	};
}]);
