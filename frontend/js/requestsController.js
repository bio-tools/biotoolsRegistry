// Controllers
angular.module('elixir_front.controllers').controller('RequestsController', ['$scope', 'ResourceRequestProvider', 'User', function($scope, ResourceRequestProvider, User) {
	var vm = this;
	$scope.requests = {};
	$scope.received = [];
	$scope.sent = [];
	$scope.loading = true;
	$scope.error = {}
	$scope.error.status = 0;
	$scope.error.message = "";
	$scope.filters = {};
	$scope.filters.showCompletedReceived = false;
	$scope.filters.showCompletedSent = false;

	// Data feteching
	vm.loadRequests = function($item, $model, $label) {
		$scope.loading = true;
		ResourceRequestProvider.getRequests().then(function successCallback(response) {
			$scope.requests = response.data.requests;
			$scope.filterSentRequests();
			$scope.filterReceivedRequests();
			$scope.loading = false;
		}, function errorCallback(response) {
			$scope.error.status = response.status;
			$scope.error.message = "There was an error communicating with the server. Try refreshing this website.";
			$scope.loading = false;
		});
	};	

	$scope.filterSentRequests = function() {
		if ($scope.filters.showCompletedSent == false) {
			$scope.sent = $scope.requests.sent.filter(vm.checkIfNotCompleted);
		}
		else {
			$scope.sent = $scope.requests.sent;
		}
	}

	$scope.filterReceivedRequests = function() {
		if ($scope.filters.showCompletedReceived == false) {
			$scope.received = $scope.requests.received.filter(vm.checkIfNotCompleted);
		}
		else {
			$scope.received = $scope.requests.received;
		}
	}

	//Operations
	vm.checkIfNotCompleted = function(request) {
		return !request.completed;
	}

	vm.requestsAffectedByAcceptingRequest = function(request) {
		// Accept ownership for not own request.
		if (request.type == "ownership" && request.username != User.current.username) {
			var affectedRequests = [];
			for (var index = 0; index < $scope.requests.received.length; ++index) {
				var checkRequest = $scope.requests.received[index];
				if (checkRequest.completed == false && checkRequest.requestId != request.requestId && checkRequest.resourceId == request.resourceId) {
					affectedRequests.push(checkRequest);
				}
			}
			return affectedRequests;
		}
		return []; 
	}

	$scope.typeDescription = function(type) {
		if (type == "editing") {
			return "Editing rights";
		}
		return "Resource ownership";
	}

	$scope.acceptRequest = function(request) {
		var affectedRequests = vm.requestsAffectedByAcceptingRequest(request);
		var resourceIndex = $scope.requests.received.indexOf(request);
		if (affectedRequests.length == 0) {
			vm.processAcceptRequest(resourceIndex, request, affectedRequests);
		}
		else {
			if (confirm("Are you sure you want to accept this request? " + affectedRequests.length + " of the exisitng requests will be sent to the new owner.")) {
				vm.processAcceptRequest(resourceIndex, request, affectedRequests);
			}
		}
	}	

	vm.processAcceptRequest = function(index, request, affectedRequests) {
		var resourceIndex = index;
		$scope.requests.received[resourceIndex].processing = true
		request.processing = false
		ResourceRequestProvider.acceptRequest(request.requestId).then(function successCallback(response) {
			$scope.requests.received[resourceIndex].processing = false
			$scope.requests.received[resourceIndex].completed = true
			$scope.requests.received[resourceIndex].accepted = true
			$scope.requests.received = _.difference($scope.requests.received, affectedRequests);
			$scope.received = _.difference($scope.received, affectedRequests); 
			request.processing = false
			request.completed = true
			request.accepted = true
			User.current.requests_count = User.current.requests_count - 1 - affectedRequests.length;
		}, function errorCallback(response) {
			vm.loadRequests();
		});
	}

	$scope.declineRequest = function(request) {
		var resourceIndex = $scope.requests.received.indexOf(request);
		request.processing = false
		$scope.requests.received[resourceIndex].processing = true
		ResourceRequestProvider.declineRequest(request.requestId).then(function successCallback(response) {
			$scope.requests.received[resourceIndex].processing = false
			$scope.requests.received[resourceIndex].completed = true
			$scope.requests.received[resourceIndex].accepted = false
			request.processing = false
			request.completed = true
			request.accepted = false
			User.current.requests_count = User.current.requests_count - 1;
		}, function errorCallback(response) {
			vm.loadRequests();
		});
	}

	// Initialization
	vm.loadRequests();
}]);

// Services and Factories
var elixir_front = angular.module('elixir_front');
elixir_front.factory('ResourceRequestProvider', ['$http', function ($http) {
	return {
		getRequests: function() {
			return $http({
				method: 'GET',
				url: '/api/request',
				params: {}
			})
		},
		acceptRequest: function(requestId) {
			return $http({
				method: 'POST',
				url: '/api/request/conclude',
				data: {'requestId': requestId, accept: true}
			})
		},
		declineRequest: function(requestId) {
			return $http({
				method: 'POST',
				url: '/api/request/conclude',
				data: {'requestId': requestId, accept: false}
			})
		},
		requestOwnership: function(resourceId) {
			return $http({
				method: 'PUT',
				url: '/api/request',
				data: {'resourceId': resourceId, type: 'ownership'}
			})
		},
		requestEditingRights: function(resourceId) {
			return $http({
				method: 'PUT',
				url: '/api/request',
				data: {'resourceId': resourceId, type: 'editing'}
			})
		}
	};
}]);