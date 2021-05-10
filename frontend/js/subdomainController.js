// Controllers
angular.module('elixir_front.controllers')
.controller('SubdomainAdminController', ['$scope',  '$stateParams', 'DomainConnection', 'DomainDetailConnection', function($scope, $stateParams, DomainConnection, DomainDetailConnection) {
	var vm = this;
	$scope.isLoadingSubdomains = true;
	$scope.subdomains = [];

	$scope.deleteSubdomainAtIndex = function(index){
		if (confirm("Are you sure you want to remove this subdomain?")){
			// COVID-19 subdomain hack
			if ($scope.subdomains[index].name.toLowerCase() == 'covid-19'){
				alert('Cannot delete the covid-19 subdomain');
				return;
			}
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
.controller('SubdomainController', ['$scope',  '$stateParams', 'ToolListOverviewConnection', 'DomainDetailConnection', 'DomainConnection', '$q', 'UsedTerms', function($scope, $stateParams, ToolListOverviewConnection, DomainDetailConnection, DomainConnection, $q, UsedTerms) {
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
	$scope.subdomain.tag = [];
	$scope.subdomain.collection = [];
	$scope.subdomain.is_private = true;
	$scope.subdomain.currentPage = 1;
	$scope.subdomain.totalPages = 1;

	$scope.errors = {};
	$scope.errors.general = '';
	$scope.errors.domain = '';
	$scope.errors.loading = '';
	$scope.errors.data = {}


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
			
			if (currentTool['biotoolsID'] == toolID){// && currentTool['versionId'] == versionID) {
				return true;
			}
		}
		return false;
	}

	$scope.addToSubdomain = function(index) {
		var selectedTool = $scope.search.searchResults[index];
		
		var selectedDict = { "biotoolsID": selectedTool.biotoolsID, "versionId": selectedTool.versionId };
		$scope.subdomain.toolList.push(selectedTool);
		$scope.subdomain.resources.push(selectedDict);
		$scope.subdomain.totalPages = ($scope.subdomain.toolList.length / $scope.toolsPerPageCount) * 10;
	}

	$scope.domainAddButtonClick = function (_what, _where, _isList, _isObject) {
		if (_isList) {
			// if array does not exist create it
			if (typeof _where[_what] == 'undefined') {
				_where[_what] = [];
			}
			// add either an object or string to array
			_where[_what].push(_isObject ? {} : '');
		} else {
			// if object does not exist create it
			if (typeof _where[_what] == 'undefined') {
				_where[_what] = _isObject ? {} : '';
			}
		}
	}

	$scope.removeButtonClick = function (_what, _parent, _index, _event){
		$scope.removeButtonClickAux(_what, _parent, _index, _event);

		if ($scope.errors.data[_what] && $scope.errors.data[_what][_index]){
			$scope.removeButtonClickAux(_what, $scope.errors.data, _index, _event);
		}
		
	}

	// remove attribute or list entry
	$scope.removeButtonClickAux = function (_what, _parent, _index, _event) {
		if (_parent[_what][_index] ? confirm("Are you sure you want to remove this element?") : 1) {
			// remove jstree if exists
			if (_event) {
				$(_event.target).closest('div').find('.jstree').jstree("destroy").remove();
			}
			_parent[_what].splice(_index, 1);
			// if last instance in array delete entire attribute from the software object
			if (_parent[_what].length == 0) {
				delete _parent[_what];
			}
		}
	}

	// used terms (collectionID) for searching in collections
	function getCollectionIDs(){
		var d = $q.defer();
		var params = {
			"usedTermName": "collectionID"
		};
		UsedTerms.get(params, function(response) {
			d.resolve(response.data);
		});
		return d.promise;
	}
	
	$scope.loadCollectionIDs = function(query) {
		return getCollectionIDs().then(function(list) {
			return list.filter(function (str) { return str.toLowerCase().includes(query.toLowerCase()); }).slice(0,10).sort();
		});
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
			$scope.errors.general = error.data.detail;
			console.log(error);
			$scope.updating = false;
			$scope.errors.data = error.data;
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

			for (var i in data.data.tag){
				$scope.subdomain.tag.push(data.data.tag[i]);
			}
		
			for (var i in data.data.collection){
				$scope.subdomain.collection.push(data.data.collection[i]);
			}

			$scope.subdomain.is_private = data.data.is_private;

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
			$scope.errors.general = error.data.detail;
			$scope.updating = false;
			$scope.errors.data = error.data;
		});
	}

	// remove or replace characters not allowed for subdomains
	// See https://tools.ietf.org/html/rfc952 for guidelines
	$scope.makeSubdomainURLSafe = function(value) {
		$scope.errors.domain = "";
		if (typeof value != 'undefined') {
			var id = value.replace(/[^a-zA-Z0-9_-]*/g,'').replace(/[ ]+/g, '-').replace(/[_]+/g, '-').toLowerCase();
		}
		if (value != id) {
			$scope.errors.domain = "Entered value '" + value + "' has been modified. Only alphanumeric characters and dashes can be used for the subdomain name.";
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
		'resources': $scope.subdomain.resources,
		'tag': $scope.subdomain.tag,
		'collection': $scope.subdomain.collection,
		'is_private': $scope.subdomain.is_private
	};
}

	// Initialization
	if ($scope.loading) {
		vm.fetchSubdomain()
	}
}]);

