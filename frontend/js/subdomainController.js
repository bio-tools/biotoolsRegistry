// Controllers
angular.module('elixir_front.controllers')
.controller('SubdomainAdminController', ['$scope',  '$stateParams', 'DomainConnection', 'DomainDetailConnection', function($scope, $stateParams, DomainConnection, DomainDetailConnection) {
	var vm = this;
	$scope.isLoadingSubdomains = true;
	$scope.subdomains = [];

	$scope.deleteSubdomainAtIndex = function(index) {
		if (confirm("Are you sure you want to remove this subdomain?")){
			var deleteSubdomain = $scope.subdomains[index];
			$scope.subdomains.splice(index, 1);
			var deleteResponse = DomainDetailConnection.delete({'domain': deleteSubdomain.name}, function(data) {
				// TODO: Handle repsonses
			}, function(error) {
				// TODO: Handle errors
			});
		}
	}

	vm.loadSubdomains = function() {
		$scope.isLoadingSubdomains = true;
		$scope.subdomains = [];
		var domainResponse = DomainConnection.query({}, function(data) {
			$scope.subdomains = data;
			$scope.isLoadingSubdomains = false;
		}, function(errorData) {
			// TODO: Handle errors
		});
	};

	// Initialization
	vm.loadSubdomains()
}])
.controller('SubdomainController', ['$scope',  '$stateParams', 'ToolListOverviewConnection', 'DomainDetailConnection', 'DomainConnection', function($scope, $stateParams, ToolListOverviewConnection, DomainDetailConnection, DomainConnection) {
	var vm = this;
	$scope.ToolListOverviewConnection = ToolListOverviewConnection;
	$scope.updating = false;
	$scope.loading = ($stateParams.id != "");
	$scope.toolsPerPageCount = 10; 

	$scope.search = {};
	$scope.search.searchOption = 'name';
	$scope.search.loadingSearchResults = false;
	$scope.search.searchResults = [];
	$scope.search.searchString = '';
	$scope.search.noResults = false;
	$scope.search.currentPage = 1;
	$scope.search.totalPages = 1;

	$scope.subdomain = {};	
	$scope.subdomain.exists = ($stateParams.id != "");
	$scope.subdomain.domain = $stateParams.id;
	$scope.subdomain.title = '';
	$scope.subdomain.subtitle = '';
	$scope.subdomain.description = '';
	$scope.subdomain.toolList = [];
	$scope.subdomain.resources = [];
	$scope.subdomain.currentPage = 1;
	$scope.subdomain.totalPages = 1;

	$scope.errors = {};
	$scope.errors.general = '';
	$scope.errors.domain = '';
	$scope.errors.loading = '';

	$scope.response = {};
	$scope.response.general = '';

	// Handle tool search
	$scope.clearButtonPressed = function() {
		$scope.search.currentPage = 1;
		var searchQuery = {}
		searchQuery[$scope.search.searchOption] = $scope.search.searchString;
		$scope.search.searchResults = [];
	};

	$scope.searchButtonPressed = function() {
		$scope.search.currentPage = 1;
		var searchQuery = {}
		searchQuery[$scope.search.searchOption] = $scope.search.searchString;
		vm.performSearch(searchQuery);
	};

	$scope.toolInSubdomain = function(toolID, versionID) {
		for (var index in $scope.subdomain.resources) {
			var currentTool = $scope.subdomain.resources[index];
			//console.log(currentTool['biotoolsID']);
			if (currentTool['biotoolsID'] == toolID){// && currentTool['versionId'] == versionID) {
				return true;
			}
		}
		return false;
	}

	$scope.addToSubdomain = function(index) {
		var selectedTool = $scope.search.searchResults[index];
		//console.log($scope.search);
		var selectedDict = { "biotoolsID": selectedTool.biotoolsID, "versionId": selectedTool.versionId };
		$scope.subdomain.toolList.push(selectedTool);
		$scope.subdomain.resources.push(selectedDict);
		$scope.subdomain.totalPages = ($scope.subdomain.toolList.length / $scope.toolsPerPageCount) * 10;
	}

	$scope.addAllToSubdomain = function() {
		for (var tool in $scope.search.searchResults) {
			var selectedTool = $scope.search.searchResults[tool];
			if (selectedTool.biotoolsID && $scope.toolInSubdomain(selectedTool.biotoolsID, selectedTool.versionId) == false) {	
				$scope.subdomain.toolList.push(selectedTool);
				$scope.subdomain.resources.push({ "biotoolsID": selectedTool.biotoolsID, "versionId": selectedTool.versionId });
			}
		}
		$scope.subdomain.totalPages = ($scope.subdomain.toolList.length / $scope.toolsPerPageCount) * 10;
	}

	$scope.removeFromSubdomain = function(index) {
		$scope.subdomain.toolList.splice(index, 1); 
		$scope.subdomain.resources.splice(index, 1);
		$scope.subdomain.totalPages = ($scope.subdomain.toolList.length / $scope.toolsPerPageCount) * 10;
	}

	$scope.saveSubdomain = function() {
		$scope.updating = true;
		$scope.errors.general = '';
		$scope.response.general = '';
		var createResponse = DomainConnection.create(vm.subdomainQuery(), function(data) {
			$scope.subdomain.exists = true;
			$scope.response.general = "Domain '" + $scope.subdomain.domain + "' was created.";
			$scope.updating = false;
		}, function(error) {
			$scope.errors.general = error.data.details;
			$scope.updating = false;
		});
	}

	vm.fetchSubdomain = function() {
		$scope.errors.general = '';
		$scope.response.general = '';
		var updateResponse = DomainDetailConnection.query({'domain': $scope.subdomain.domain}, function(data) {
			$scope.subdomain.title = data.data['title'];
			$scope.subdomain.subtitle = data.data['sub_title'];
			$scope.subdomain.description = data.data['description'];
			for (var index in data.data.resources) {
				var tool = data.data.resources[index];
				tool['biotoolsID'] = tool['biotoolsID'];
				$scope.subdomain.toolList.push(tool);
				$scope.subdomain.resources.push(tool);
			}
			$scope.loading = false;
			$scope.updating = false;
			$scope.subdomain.totalPages = ($scope.subdomain.toolList.length / $scope.toolsPerPageCount) * 10;
		}, function(error) {
			// Handle error
			$scope.errors.loading = 'Data failed to load. Please try to refresh this website. ' + error.data.details;
		});
	}

	$scope.updateSubdomain = function() {
		$scope.updating = true;
		$scope.errors.general = '';
		$scope.response.general = '';
		var updateResponse = DomainDetailConnection.update(vm.subdomainQuery(), function(data) {
			$scope.response.general = "Domain '" + $scope.subdomain.domain + "' was updated with " + $scope.subdomain.resources.length + " entries." ;
			$scope.updating = false;
		}, function(error) {
			$scope.errors.general = error.data.details;
			$scope.updating = false;
		});
	}

	// remove or replace all URL unsafe characters and set software.id
	$scope.makeIdURLSafe = function(value) {
		$scope.errors.domain = "";
		if (typeof value != 'undefined') {
			var id = value.replace(/[^a-zA-Z0-9_~ .-]*/g,'').replace(/[ ]+/g, '_');
		}
		if (value != id) {
			$scope.errors.domain = "Entered value '" + value + "' has been modified. Only URL safe characters can be used for the identifier.";
		}
		$scope.subdomain.domain = id;
	}

	vm.performSearch = function(query) {
		$scope.search.loadingSearchResults = true;
		$scope.search.noResults = false;
		var response = ToolListOverviewConnection.query(query, function() {
			$scope.search.currentPage = 1;
			$scope.search.searchResults = response;
			$scope.search.loadingSearchResults = false;
			$scope.search.totalPages = ($scope.search.searchResults.length / $scope.toolsPerPageCount) * 10;
			if (response.length == 0) {
				$scope.search.noResults = true;
			}
		});
	};

	vm.subdomainQuery = function() {
		return {'domain': $scope.subdomain.domain,
		'title': $scope.subdomain.title,
		'sub_title': $scope.subdomain.subtitle,
		'description': $scope.subdomain.description,
		'resources': $scope.subdomain.resources
	};
}

	// Initialization
	if ($scope.loading) {
		vm.fetchSubdomain()
	}
}]);

