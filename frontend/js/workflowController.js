// Controllers
angular.module('elixir_front.controllers')
.controller('WorkflowController', ['$scope',  '$stateParams', '$modal', 'WorkflowProvider', function($scope, $stateParams, $modal, WorkflowProvider) {
	var vm = this;
	$scope.loading = true
	$scope.filteredWorkflows = []
	$scope.workflows = []

	// Data feteching
	vm.loadRequests = function($item, $model, $label) {
		$scope.loading = true;
		WorkflowProvider.getWorkflows().then(function successCallback(response) {
			$scope.workflows = response.data;
			$scope.filterWorkflows();
			$scope.loading = false;
		}, function errorCallback(response) {
			//TODO: Handle error
		});
	};	

	$scope.filterWorkflows = function() {
		var searchString = $scope.search.searchString;
		if (searchString == undefined || searchString == '') {
			$scope.filteredWorkflows = $scope.workflows;
		}
		else {
			$scope.filteredWorkflows = $scope.workflows.filter(function(x) {
				var foundAnnotations = x.annotations.filter(function(annotation) {
					var regularExpression = new RegExp(searchString,"i");
					if (annotation.title.match(regularExpression) || annotation.title.match(regularExpression) || annotation.edam_term.match(regularExpression)) {
						return true;
					}
					return false;
				});
				return foundAnnotations.length > 0;
			});
		}
	}

	$scope.openModal = function(workflow) {
		$modal.open({
			templateUrl: 'partials/workflows/modal.html',
			controller: ['$modalInstance', 'workflow', WorkflowModalCtrl],
			controllerAs: 'vm',
			windowClass: 'workflow-modal-window',
			resolve: {
				workflow: function () { return workflow },
			}
		});
	};

	$scope.handleAnnotationClick = function(annotation) {
		console.log(annotation);
	}

	$scope.search = function() {
		console.log(string);
	};

	// Initialization
	vm.loadRequests();
}]);

function WorkflowModalCtrl($modalInstance, workflow) {
	var vm = this;
	vm.workflow = workflow;
	vm.currentTitle = "";
	vm.currentDescription = "";
	vm.currentEdam = "";

	vm.mapDimensions = function(annotation) {
		return vm.mapXDimension(annotation.startX) + "," + vm.mapYDimension(annotation.startY) + "," + vm.mapXDimension(annotation.endX) + "," + vm.mapYDimension(annotation.endY);
	}

	vm.imageHeight = function() {
		var img = document.getElementById('image'); 
		return img.clientHeight;
	}

	vm.imageWidth = function() {
		var img = document.getElementById('image'); 
		return img.clientWidth;
	}

	vm.mapXDimension = function(dim_x) {
		var multiplier_x = vm.imageWidth() / vm.workflow.width
		return dim_x * multiplier_x
	}

	vm.mapYDimension = function(dim_y) {
		var multiplier_y = vm.imageHeight() / vm.workflow.height
		return dim_y * multiplier_y
	}

	vm.hover = function(annotation) {
		vm.currentTitle = annotation.title;
		vm.currentDescription = annotation.description;
		vm.currentEdam = annotation.edam_term;
	}

	vm.endHover = function(annotation) {
		vm.currentTitle = "";
		vm.currentDescription = "";
		vm.currentEdam = "";
	}
}

// Services and Factories
var elixir_front = angular.module('elixir_front');
elixir_front.factory('WorkflowProvider', ['$http', function ($http) {
	return {
		getWorkflows: function() {
			return $http({
				method: 'GET',
				url: '/api/w',
				params: {}
			})
		}
	};
}]);