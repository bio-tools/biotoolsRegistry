'use strict';

/* Controllers */

angular.module('elixir_front.controllers', [])
.controller('ToolGridController', ['$scope', '$timeout', 'ToolList', 'ToolTableDataSource', function ($scope, $timeout, ToolList, ToolTableDataSource) {
	$scope.ToolList = ToolList;
	$scope.savedStateExists = function() {
		return localStorage.getItem('gridState') ? true : false;
	};
	$scope.saveState = function() {
		var state = $scope.gridApi.saveState.save();
		localStorage.setItem('gridState', JSON.stringify(state));
	};
	$scope.restoreState = function() {
		$timeout(function() {
            var state = localStorage.getItem('gridState');
			if (state) $scope.gridApi.saveState.restore($scope, JSON.parse(state));
		});
	};
	$scope.gridOptions = {
		enableSorting: false,
		enableColumnMenus: false,
		enableColumnResizing: true,
		enableVerticalScrollbar: 1,
		enableHorizontalScrollbar: true,
		columnVirtualizationThreshold: ToolTableDataSource.columnsDescription([]).length,
		data: ToolList.list,
		columnDefs: ToolTableDataSource.columnsDescription($scope.savedStateExists() == true ? [] : ['Name', 'Description', 'Homepage', 'Credits', 'Operation', 'Topic', 'Input', 'Output']),
		rowHeight: 135,
		enableGridMenu: true,
		onRegisterApi: function(gridApi) {
			$scope.gridApi = gridApi;
			$scope.restoreState();
			// Setup events so we're notified when grid state changes.
			$scope.gridApi.core.on.columnVisibilityChanged($scope, function (column) {
				$scope.saveState();
			});
			$scope.gridApi.colResizable.on.columnSizeChanged($scope, function (column) {
				$scope.saveState();
			});
			$scope.gridApi.colMovable.on.columnPositionChanged($scope, function (column) {
				$scope.saveState();
			});
		}
	};
	$scope.tableHeight = function() {
		return {"height": ((Math.min($scope.ToolList.count, 10) * $scope.gridOptions.rowHeight) + 33) + "px"};
	}
}])
.controller('ToolGridCellController', ['$scope', function ($scope) {
	$scope.init = function(columnName, rowIndex) {
		$scope.columnName = columnName;
		$scope.rowIndex = rowIndex;
	}
	$scope.RowIdentifier = function() {
		return $scope.columnName+$scope.rowIndex;
	}
	$scope.RowName = function() {
		return $scope.columnName;
	}
	$scope.RowHeight = function() {
		var element = document.getElementById($scope.RowIdentifier());
		return (element) ? element.offsetHeight : 0;
	}
	$scope.DefaultRowHeight = function() {
		return 135;
	}
	$scope.CellWidth = function() {
		return document.getElementById($scope.RowIdentifier()).offsetWidth;
	}
	$scope.CellStyle = function() {
		return {'width': CellWidthDescription(),
		'background-color': CellColorDescription()};
	}
	function CellWidthDescription() {
		return ($scope.CellWidth() + 2) + "px";
	}
	function CellColorDescription() {
		return $scope.rowIndex % 2 != 0 ? "#f8f8f8" : "white";
	}
}])
.controller('SearchResultController', ['$scope','$state', 'ToolList', 'ToolTableDataSource', 'DisplayModeSelector', 'Domain', function($scope, $state, ToolList, ToolTableDataSource, DisplayModeSelector, Domain){

	function quoteQueryStringValue(v){
		return '"' + v + '"'
	}

	function stripEdam(t){
		return t.replace("http://edamontology.org/", "");
	}

	$scope.topicNameClicked = function(topic) {
		//$state.go('search', {'topic': topic.term}, {reload: true});
		$state.transitionTo('search', {'topicID': quoteQueryStringValue(stripEdam(topic.uri))},
		{
		reload: true,
		inherit: false,
		notify: true
		});
	}

	$scope.operationNameClicked = function(operation) {
		//$state.go('search', {'topic': topic.term}, {reload: true});
		$state.transitionTo('search', {'operationID': quoteQueryStringValue(stripEdam(operation.uri))},
		{
		reload: true,
		inherit: false,
		notify: true
		});
	}
	$scope.collectionNameClicked = function(collection) {
		//$state.go('search', {'topic': topic.term}, {reload: true});
		$state.transitionTo('search', {'collectionID': quoteQueryStringValue(collection)},
		{
		reload: true,
		inherit: false,
		notify: true
		});
	}

	$scope.shouldLicenseBeALink = function(license) {
  	return !_.includes(['Freeware','Proprietary', 'Other', 'Not licensed'], license);
	}

	$scope.getFlatOperations = function(functions){

		var operations = {};
		for (var i = 0; i < functions.length; i++){
			for (var j = 0; j < functions[i].operation.length; j++){
				var o = functions[i].operation[j];
				operations[o.term] = o;
			}
		}

		var arr = Object.keys(operations);
		var r = [];
		for (var i = 0; i < arr.length;i++){
			r.push(operations[arr[i]]);
		}

		return r;
	}

	$scope.Domain = Domain;
	$scope.ToolTableDataSource = ToolTableDataSource;
	$scope.ToolList = ToolList;
	$scope.DisplayModeSelector = DisplayModeSelector;
	// Get data initially
	ToolList.refresh();
}])
.controller('AlertsController', ['$scope', 'Alert', 'EnvironmentChecker', function($scope, Alert, EnvironmentChecker){
	$scope.Alert = Alert;
	$scope.dev_alert = false;

	// check if the current setup id dev or prod.
	EnvironmentChecker.getEnvironment().then(function(data) {
		if (data == 'Development') {
			$scope.dev_alert = true;
		}
	});

	// check if cookie info was disabled for this user
	if ('cookie_alert' in localStorage) {
		$scope.cookie_alert = (localStorage.cookie_alert === 'true');
	} else {
		$scope.cookie_alert = true;
	}

	// check if welcome message was disabled for this user
	if ('welcome_message' in localStorage) {
		$scope.welcome_message = (localStorage.welcome_message === 'true');
	} else {
		$scope.welcome_message = true;
	}

	$scope.closeCookieInfoButtonClick = function() {
		$scope.cookie_alert = false;
		localStorage.cookie_alert = false;
	};

	$scope.closeWelcomeMessageButtonClick = function() {
		$scope.welcome_message = false;
		localStorage.welcome_message = false;
	};
}])
.controller('ToolEditController', ['$scope', '$controller', '$state', '$stateParams', 'Ontology', 'Attribute', 'CheckUserEditingRights', 'User', '$timeout', 'UsedTerms','$q','$modal', function($scope, $controller, $state, $stateParams, Ontology, Attribute, CheckUserEditingRights, User, $timeout, UsedTerms, $q, $modal ) {

	// reference the service
	$scope.Attribute = Attribute;
	$scope.CheckUserEditingRights = CheckUserEditingRights;
	$scope.$state = $state;
	$scope.form = {};
	$scope.canEditTool = false;
	$scope.canEditToolPermissions = false;
	$scope.User = User;
	$scope.orderby = 'text';
	
	$scope.registeringInProgress = false;
	

	// for storing validation and saving progess
	$scope.validationProgress = {}, $scope.savingProgress = {}, $scope.deletingProgress = {};

	$scope.initializePermissions = function() {
		$scope.canEditTool = false;
		$scope.canEditToolPermissions = false;
		// Owner can edit anything.
		if (!_.isEmpty($scope.software)){
			if ($scope.software.owner == $scope.User.getUsername()) {
				$scope.canEditTool = true;
				$scope.canEditToolPermissions = true;
			}
			else if ($scope.software.editPermission != undefined) {
				$scope.canEditTool = $scope.CheckUserEditingRights.canEdit($scope.software);
				$scope.canEditToolPermissions = false;
				delete $scope.software.editPermission;
			}
		}
	}

	// handle sending the resource to either validation or saving endpoints
	$scope.sendResource = function(service, progress, isRemoval, action) {
		progress.success = false;
		progress.error = false;
		progress.inProgress = true;
		$scope.registrationErrorPayload = null;

		service($stateParams, $scope.software, function (response) {
			// handle success
			progress.inProgress = false;
			progress.success = true;
			if (isRemoval) {
				alert('Resource removed succesfully.');
				$state.go('search');
			}

			if (action == "create"){
				$state.go('tool.edit', {id: response.biotoolsID});
			}

		}, function(response) {
			// handle error
			progress.error = true;
			progress.inProgress = false;
			$scope.registrationErrorPayload = response.data;
		});
	}

	// modals
	$scope.openModal = function (edam, type, suggestions) {
		var ontoMap = {
			'data': $scope.EDAM_data,
			'format': $scope.EDAM_format,
			'operation': $scope.EDAM_operation
		};
		var onto = ontoMap[type] || $scope.EDAM_data;

		var modalInstance = $modal.open({
			templateUrl: 'partials/tool_edit/toolEditEdamModal.html',
			controllerAs: 'vm',
			controller: ['$modalInstance', 'edam', 'onto', 'type', 'suggestions', EdamModalCtrl],
			resolve: {
				edam: function () { return edam; },
				onto: function () { return onto; },
				type: function () { return type; },
				suggestions: function () { return suggestions; },
			}
		});

		modalInstance.result.then(function (updatedEdam) {
			angular.copy(updatedEdam, edam);
		}, function () { });

		return modalInstance.result;
	}


	$scope.findObjectByUri = function (obj, targetUri) {
		function search(current) {
			if (current.data && current.data.uri === targetUri) {
				return current;
			}
			if (current.children) {
				for (var i = 0; i < current.children.length; i++) {
					var result = search(current.children[i]);
					if (result) return result;
				}
			}
			return null;
		}

		for (var i = 0; i < obj.length; i++) {
			var result = search(obj[i]);
			if (result) return result;
		}
		return null;
	};

	$scope.flattenObject = function (obj) {
		var result = [];
		var stack = [obj];

		while (stack.length > 0) {
			var current = stack.pop();
			for (var key in current) {
				if (current.hasOwnProperty(key)) {
					var value = current[key];
					if (typeof value === 'object' && value !== null) {
						stack.push(value);
					} else {
						result.push(value);
					}
				}
			}
		}
		return result;
	};	

	$scope.recommend_terms = function (edam, type) {
		var edamArray = $scope.flattenObject(edam).filter(function (word) {
			return typeof word === 'string' && word.indexOf('http://edamontology.org/') !== -1;
		});

		if (type === "operation") return null;  // No recommendations for operations

		var ontoMap = {
			'format': $scope.EDAM_data,
			'input': $scope.EDAM_operation,
			'output': $scope.EDAM_operation
		};
		var onto = ontoMap[type] || $scope.EDAM_operation;

		var suggestions = [];

		for (var i = 0; i < edamArray.length; i++) {
			var element = edamArray[i];
			var edamObj = $scope.findObjectByUri(onto, element);
			if (!edamObj) continue;

			var appendSuggestions = getSuggestions(type, edamObj, edam);
			if (appendSuggestions.length) {
				suggestions = suggestions.concat(appendSuggestions);
			}
		}

		return mapSuggestions(suggestions, type);
	};

	function getSuggestions(type, edamObj, edam) {
		switch (type) {
			case 'input':
				return getInputSuggestions(edamObj, edam);
			case 'output':
				return getOutputSuggestions(edamObj, edam);
			default:
				return [];
		}
	}

	function getInputSuggestions(edamObj, edam) {
		if (!edamObj.has_input) return [];
		if (!edam.hasOwnProperty('input')) return edamObj.has_input;
		return edamObj.has_input.filter(function (input) {
			return !edam.input.some(function (existingInput) {
				return existingInput.data.uri === input;
			});
		});
	}

	function getOutputSuggestions(edamObj, edam) {
		if (!edamObj.has_output) return [];
		if (!edam.hasOwnProperty('output')) return edamObj.has_output;
		return edamObj.has_output.filter(function (output) {
			return !edam.output.some(function (existingOutput) {
				return existingOutput.data.uri === output;
			});
		});
	}

	function mapSuggestions(suggestions, type) {
		var ontoMap = {
			'format': $scope.EDAM_format,
			'output': $scope.EDAM_data,
			'input': $scope.EDAM_data
		};
		var onto = ontoMap[type];

		return suggestions.map(function (element) {
			var edamObj = $scope.findObjectByUri(onto, element);
			return {
				'uri': element,
				'term': edamObj ? edamObj.text : ''
			};
		});
	}

	$scope.addWithModal = function (type, edam) {
		var pickerTypeMap = {
			'input': 'data',
			'output': 'data',
			'format': 'format',
			'function': 'operation',
			'operation': 'operation'
		};
		var pickertype = pickerTypeMap[type] || '';

		var suggestions = $scope.recommend_terms(edam, type);

		var modalPromise = $scope.openModal({}, pickertype, suggestions);

		modalPromise.then(function (newEdam) {
			handleModalResult(type, edam, newEdam);
		}, function () { });
	};

	function handleModalResult(type, edam, newEdam) {
		switch (type) {
			case 'format':
				$scope.addButtonClick('format', edam, true, true);
				edam.format[edam.format.length - 1] = newEdam;
				break;
			case 'output':
				$scope.addButtonClick('output', edam, true, true);
				edam.output[edam.output.length - 1] = newEdam;
				break;
			case 'input':
				$scope.addButtonClick('input', edam, true, true);
				edam.input[edam.input.length - 1] = newEdam;
				break;
			case 'function':
				$scope.addButtonClick('function', edam, true, true);
				edam.function[edam.function.length - 1].operation = [newEdam];
				break;
			case 'operation':
				$scope.addButtonClick('function', edam, true, true);
				edam.push(newEdam);
				break;
		}
	}
	
	// reset success flags when changes are made
	$scope.$watch('software', function(newVal, oldVal) {
		if (newVal !== oldVal) {
			$scope.savingProgress.success = false;
			$scope.validationProgress.success = false;
		}
	}, true);
	
	// used terms (biotoolsID) for searching in relations
	function getBiotoolsIDs(){
		var d = $q.defer();
		var params = {
			"usedTermName": "biotoolsID"
		};
		UsedTerms.get(params, function(response) {
			d.resolve(response.data);
		});
		return d.promise;
	}
	
	$scope.loadBiotoolsIDs = function(query) {
		return getBiotoolsIDs().then(function(list) {
			return list.filter(function (str) { return str.toLowerCase().includes(query.toLowerCase()); }).slice(0,50).sort();
		});
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

	// used terms (credit names) for searching in credits
	function getCreditNames(){
		var d = $q.defer();
		var params = {
			"usedTermName": "credit"
		};
		UsedTerms.get(params, function(response) {
			d.resolve(response.data);
		});
		return d.promise;
	}
	
	$scope.loadCreditNames = function(query) {
		return getCreditNames().then(function(list) {
			return list.filter(function (str) { return str.toLowerCase().includes(query.toLowerCase()); }).slice(0,10).sort();
		});
	}



	// add attribute or list entry
	$scope.addButtonClick = function (_what, _where, _isList, _isObject) {
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

	$scope.addObjectClick = function(_what, _parent, _where){
		_parent[_where] = {}
		_parent[_where][_what] = {}

	}

	$scope.removeObjectClick = function(_what, _parent, _where){
		var message = _parent[_what][_index].term ? `Are you sure you want to remove ${_parent[_what][_index].term}?` : "Are you sure you want to remove this element?"

		if (confirm(message)){
			if (_parent[_where][_what]){
				delete _parent[_where][_what];
			}
			if (Object.keys(_parent[_where]).length === 0){
				delete _parent[_where];
			}
		}
	}

	// remove attribute or list entry
	$scope.removeButtonClick = function (_what, _parent, _index, _event) {
		var message = _parent[_what][_index].term 
			? `Are you sure you want to remove ${_parent[_what][_index].term}?` 
			: "Are you sure you want to remove this element?";
	
		if (_parent[_what][_index] ? confirm(message) : true) {
			// remove jstree if exists
			if (_event) {
				$(_event.target).closest('div').find('.jstree').jstree("destroy").remove();
			}
	
			_parent[_what].splice(_index, 1);
	
			// if last instance in array delete entire attribute from the parent object
			if (_parent[_what].length == 0) {
				delete _parent[_what];
	
				// If we're removing an operation and it's the last one, remove the entire function
				if (_what === 'operation') {
					var functionIndex = $scope.software.function.indexOf(_parent);
					if (functionIndex > -1) {
						$scope.software.function.splice(functionIndex, 1);
					}
				}
			}
		}
	};	

	// create connections between entries
	$scope.errorConnections = {
		"name" : ["id"]
	};

	// reset error on change
	$scope.resetError = function (_what, _parent, _index) {
		// select appropriate error type handling
		if (_index != undefined && _index >= 0) {
			$scope.resetListError(_what, _parent, _index);
		}
		else {
			// remove all connected error warnings
			var whatConnections = $scope.errorConnections[_what];
			if (whatConnections) {
				whatConnections.forEach( function(connection) {
					if (_parent != undefined && _parent[connection]) {
						delete _parent[connection];
					}
				});
			}
			// remove the actual error
			if (_parent != undefined && _parent[_what]) {
				delete _parent[_what];
			}

		}
	}

	$scope.resetListError = function (_what, _parent, _index) {
		if (_parent[_what] && _parent[_what][_index]) {
			_parent[_what][_index] = {};
		}
	}

	$scope.isString = function(value) {
		if (typeof value === 'string') {
			return true;
		} else {
			return false;
		}
	}

	// get ontology objects for the various widgets
	Ontology.get({"name":"EDAM_topic"}, function(response) {$scope.EDAM_topic = response.data.children});
	Ontology.get({"name":"EDAM_data"}, function(response) {$scope.EDAM_data = response.data.children});
	Ontology.get({"name":"EDAM_format"}, function(response) {$scope.EDAM_format = response.data.children});
	Ontology.get({"name":"EDAM_operation"}, function(response) {$scope.EDAM_operation = response.data.children});

	// populate the JSON edit textarea
	$scope.$watch('software', function(newVal, oldVal) {
		$scope.jsonEdit.model = angular.toJson($scope.software, 2);
		// Check permissions
		if ($scope.canEditTool == false) {
				$scope.initializePermissions();
		}
	}, true);

	// parse the edited JSON for errors
	$scope.jsonEdit = {};
	var initializing = true;
	$scope.$watch('jsonEdit.model', function (newVal, oldVal) {
		if (!initializing) {
			try {
				$scope.software = angular.fromJson($scope.jsonEdit.model);
				$scope.jsonEdit.error = null;
			} catch(exp) {
				$scope.jsonEdit.error = exp.message;
			};
		} else {
			initializing = false;
		}

	});

	// download JSON from the editor
	$scope.downloadTool = function(_pretty) {
		var hiddenElement = document.createElement('a');
		if (_pretty) {
			hiddenElement.href = 'data:attachment/json,' + encodeURI(angular.toJson($scope.software, 2));
		} else {
			hiddenElement.href = 'data:attachment/json,' + encodeURI(angular.toJson($scope.software));
		}
		hiddenElement.target = '_blank';
		hiddenElement.download = ($scope.software.name ? $scope.software.name : 'resource') + '.json';
		document.body.appendChild(hiddenElement);
		hiddenElement.click();
	}

	// settings for the EDAM tree widget
	$scope.treeOptions = {
		nodeChildren: "children",
		dirSelectable: true
	}


	// set term and uri when picked from EDAM widget
	$scope.ontologyOnSelect = function (_object, _index, _node) {
		// if _object[_index] is not an object, make it one
		if ( !(_object[_index] === Object(_object[_index]) ) ) {
			_object[_index] = {};
		}
		_object[_index].term = _node.text;
		_object[_index].uri = _node.data.uri;
	}

	$scope.latestOptions = [
		{value: 1, text: "Yes"},
		{value: 0, text: "No"}
	];

	$scope.contactRoleOptions = [
		{value: "General", text: "General"},
		{value: "Developer", text: "Developer"},
		{value: "Technical", text: "Technical"},
		{value: "Scientific", text: "Scientific"},
		{value: "Helpdesk", text: "Helpdesk"},
		{value: "Maintainer", text: "Maintainer"}
	];

	$scope.licenseOptions = [
		{value: "Freeware", text: "Freeware"},
		{value: "Proprietary", text: "Proprietary"},
		{value: "Other", text: "Other"},
		{value: "Not licensed", text: "Not licensed"},
		{value: "0BSD", text: "0BSD"},
		{value: "AAL", text: "AAL"},
		{value: "ADSL", text: "ADSL"},
		{value: "AFL-1.1", text: "AFL-1.1"},
		{value: "AFL-1.2", text: "AFL-1.2"},
		{value: "AFL-2.0", text: "AFL-2.0"},
		{value: "AFL-2.1", text: "AFL-2.1"},
		{value: "AFL-3.0", text: "AFL-3.0"},
		{value: "AGPL-1.0", text: "AGPL-1.0"},
		{value: "AGPL-3.0", text: "AGPL-3.0"},
		{value: "AMDPLPA", text: "AMDPLPA"},
		{value: "AML", text: "AML"},
		{value: "AMPAS", text: "AMPAS"},
		{value: "ANTLR-PD", text: "ANTLR-PD"},
		{value: "APAFML", text: "APAFML"},
		{value: "APL-1.0", text: "APL-1.0"},
		{value: "APSL-1.0", text: "APSL-1.0"},
		{value: "APSL-1.1", text: "APSL-1.1"},
		{value: "APSL-1.2", text: "APSL-1.2"},
		{value: "APSL-2.0", text: "APSL-2.0"},
		{value: "Abstyles", text: "Abstyles"},
		{value: "Adobe-2006", text: "Adobe-2006"},
		{value: "Adobe-Glyph", text: "Adobe-Glyph"},
		{value: "Afmparse", text: "Afmparse"},
		{value: "Aladdin", text: "Aladdin"},
		{value: "Apache-1.0", text: "Apache-1.0"},
		{value: "Apache-1.1", text: "Apache-1.1"},
		{value: "Apache-2.0", text: "Apache-2.0"},
		{value: "Artistic-1.0", text: "Artistic-1.0"},
		{value: "Artistic-1.0-Perl", text: "Artistic-1.0-Perl"},
		{value: "Artistic-1.0-cl8", text: "Artistic-1.0-cl8"},
		{value: "Artistic-2.0", text: "Artistic-2.0"},
		{value: "BSD-2-Clause", text: "BSD-2-Clause"},
		{value: "BSD-2-Clause-FreeBSD", text: "BSD-2-Clause-FreeBSD"},
		{value: "BSD-2-Clause-NetBSD", text: "BSD-2-Clause-NetBSD"},
		{value: "BSD-3-Clause", text: "BSD-3-Clause"},
		{value: "BSD-3-Clause-Attribution", text: "BSD-3-Clause-Attribution"},
		{value: "BSD-3-Clause-Clear", text: "BSD-3-Clause-Clear"},
		{value: "BSD-3-Clause-LBNL", text: "BSD-3-Clause-LBNL"},
		{value: "BSD-3-Clause-No-Nuclear-License", text: "BSD-3-Clause-No-Nuclear-License"},
		{value: "BSD-3-Clause-No-Nuclear-License-2014", text: "BSD-3-Clause-No-Nuclear-License-2014"},
		{value: "BSD-3-Clause-No-Nuclear-Warranty", text: "BSD-3-Clause-No-Nuclear-Warranty"},
		{value: "BSD-4-Clause", text: "BSD-4-Clause"},
		{value: "BSD-4-Clause-UC", text: "BSD-4-Clause-UC"},
		{value: "BSD-Protection", text: "BSD-Protection"},
		{value: "BSD-Source-Code", text: "BSD-Source-Code"},
		{value: "BSL-1.0", text: "BSL-1.0"},
		{value: "Bahyph", text: "Bahyph"},
		{value: "Barr", text: "Barr"},
		{value: "Beerware", text: "Beerware"},
		{value: "BitTorrent-1.0", text: "BitTorrent-1.0"},
		{value: "BitTorrent-1.1", text: "BitTorrent-1.1"},
		{value: "Borceux", text: "Borceux"},
		{value: "CATOSL-1.1", text: "CATOSL-1.1"},
		{value: "CC-BY-1.0", text: "CC-BY-1.0"},
		{value: "CC-BY-2.0", text: "CC-BY-2.0"},
		{value: "CC-BY-2.5", text: "CC-BY-2.5"},
		{value: "CC-BY-3.0", text: "CC-BY-3.0"},
		{value: "CC-BY-4.0", text: "CC-BY-4.0"},
		{value: "CC-BY-NC-1.0", text: "CC-BY-NC-1.0"},
		{value: "CC-BY-NC-2.0", text: "CC-BY-NC-2.0"},
		{value: "CC-BY-NC-2.5", text: "CC-BY-NC-2.5"},
		{value: "CC-BY-NC-3.0", text: "CC-BY-NC-3.0"},
		{value: "CC-BY-NC-4.0", text: "CC-BY-NC-4.0"},
		{value: "CC-BY-NC-ND-1.0", text: "CC-BY-NC-ND-1.0"},
		{value: "CC-BY-NC-ND-2.0", text: "CC-BY-NC-ND-2.0"},
		{value: "CC-BY-NC-ND-2.5", text: "CC-BY-NC-ND-2.5"},
		{value: "CC-BY-NC-ND-3.0", text: "CC-BY-NC-ND-3.0"},
		{value: "CC-BY-NC-ND-4.0", text: "CC-BY-NC-ND-4.0"},
		{value: "CC-BY-NC-SA-1.0", text: "CC-BY-NC-SA-1.0"},
		{value: "CC-BY-NC-SA-2.0", text: "CC-BY-NC-SA-2.0"},
		{value: "CC-BY-NC-SA-2.5", text: "CC-BY-NC-SA-2.5"},
		{value: "CC-BY-NC-SA-3.0", text: "CC-BY-NC-SA-3.0"},
		{value: "CC-BY-NC-SA-4.0", text: "CC-BY-NC-SA-4.0"},
		{value: "CC-BY-ND-1.0", text: "CC-BY-ND-1.0"},
		{value: "CC-BY-ND-2.0", text: "CC-BY-ND-2.0"},
		{value: "CC-BY-ND-2.5", text: "CC-BY-ND-2.5"},
		{value: "CC-BY-ND-3.0", text: "CC-BY-ND-3.0"},
		{value: "CC-BY-ND-4.0", text: "CC-BY-ND-4.0"},
		{value: "CC-BY-SA-1.0", text: "CC-BY-SA-1.0"},
		{value: "CC-BY-SA-2.0", text: "CC-BY-SA-2.0"},
		{value: "CC-BY-SA-2.5", text: "CC-BY-SA-2.5"},
		{value: "CC-BY-SA-3.0", text: "CC-BY-SA-3.0"},
		{value: "CC-BY-SA-4.0", text: "CC-BY-SA-4.0"},
		{value: "CC0-1.0", text: "CC0-1.0"},
		{value: "CDDL-1.0", text: "CDDL-1.0"},
		{value: "CDDL-1.1", text: "CDDL-1.1"},
		{value: "CECILL-1.0", text: "CECILL-1.0"},
		{value: "CECILL-1.1", text: "CECILL-1.1"},
		{value: "CECILL-2.0", text: "CECILL-2.0"},
		{value: "CECILL-2.1", text: "CECILL-2.1"},
		{value: "CECILL-B", text: "CECILL-B"},
		{value: "CECILL-C", text: "CECILL-C"},
		{value: "CNRI-Jython", text: "CNRI-Jython"},
		{value: "CNRI-Python", text: "CNRI-Python"},
		{value: "CNRI-Python-GPL-Compatible", text: "CNRI-Python-GPL-Compatible"},
		{value: "CPAL-1.0", text: "CPAL-1.0"},
		{value: "CPL-1.0", text: "CPL-1.0"},
		{value: "CPOL-1.02", text: "CPOL-1.02"},
		{value: "CUA-OPL-1.0", text: "CUA-OPL-1.0"},
		{value: "Caldera", text: "Caldera"},
		{value: "ClArtistic", text: "ClArtistic"},
		{value: "Condor-1.1", text: "Condor-1.1"},
		{value: "Crossword", text: "Crossword"},
		{value: "CrystalStacker", text: "CrystalStacker"},
		{value: "Cube", text: "Cube"},
		{value: "D-FSL-1.0", text: "D-FSL-1.0"},
		{value: "DOC", text: "DOC"},
		{value: "DSDP", text: "DSDP"},
		{value: "Dotseqn", text: "Dotseqn"},
		{value: "ECL-1.0", text: "ECL-1.0"},
		{value: "ECL-2.0", text: "ECL-2.0"},
		{value: "EFL-1.0", text: "EFL-1.0"},
		{value: "EFL-2.0", text: "EFL-2.0"},
		{value: "EPL-1.0", text: "EPL-1.0"},
		{value: "EUDatagrid", text: "EUDatagrid"},
		{value: "EUPL-1.0", text: "EUPL-1.0"},
		{value: "EUPL-1.1", text: "EUPL-1.1"},
		{value: "Entessa", text: "Entessa"},
		{value: "ErlPL-1.1", text: "ErlPL-1.1"},
		{value: "Eurosym", text: "Eurosym"},
		{value: "FSFAP", text: "FSFAP"},
		{value: "FSFUL", text: "FSFUL"},
		{value: "FSFULLR", text: "FSFULLR"},
		{value: "FTL", text: "FTL"},
		{value: "Fair", text: "Fair"},
		{value: "Frameworx-1.0", text: "Frameworx-1.0"},
		{value: "FreeImage", text: "FreeImage"},
		{value: "GFDL-1.1", text: "GFDL-1.1"},
		{value: "GFDL-1.2", text: "GFDL-1.2"},
		{value: "GFDL-1.3", text: "GFDL-1.3"},
		{value: "GL2PS", text: "GL2PS"},
		{value: "GPL-1.0", text: "GPL-1.0"},
		{value: "GPL-2.0", text: "GPL-2.0"},
		{value: "GPL-3.0", text: "GPL-3.0"},
		{value: "Giftware", text: "Giftware"},
		{value: "Glide", text: "Glide"},
		{value: "Glulxe", text: "Glulxe"},
		{value: "HPND", text: "HPND"},
		{value: "HaskellReport", text: "HaskellReport"},
		{value: "IBM-pibs", text: "IBM-pibs"},
		{value: "IC", text: "IC"},
		{value: "IJG", text: "IJG"},
		{value: "IPA", text: "IPA"},
		{value: "IPL-1.0", text: "IPL-1.0"},
		{value: "ISC", text: "ISC"},
		{value: "ImageMagick", text: "ImageMagick"},
		{value: "Imlib2", text: "Imlib2"},
		{value: "Info-ZIP", text: "Info-ZIP"},
		{value: "Intel", text: "Intel"},
		{value: "Intel-ACPI", text: "Intel-ACPI"},
		{value: "Interbase-1.0", text: "Interbase-1.0"},
		{value: "JSON", text: "JSON"},
		{value: "JasPer-2.0", text: "JasPer-2.0"},
		{value: "LAL-1.2", text: "LAL-1.2"},
		{value: "LAL-1.3", text: "LAL-1.3"},
		{value: "LGPL-2.0", text: "LGPL-2.0"},
		{value: "LGPL-2.1", text: "LGPL-2.1"},
		{value: "LGPL-3.0", text: "LGPL-3.0"},
		{value: "LGPLLR", text: "LGPLLR"},
		{value: "LPL-1.0", text: "LPL-1.0"},
		{value: "LPL-1.02", text: "LPL-1.02"},
		{value: "LPPL-1.0", text: "LPPL-1.0"},
		{value: "LPPL-1.1", text: "LPPL-1.1"},
		{value: "LPPL-1.2", text: "LPPL-1.2"},
		{value: "LPPL-1.3a", text: "LPPL-1.3a"},
		{value: "LPPL-1.3c", text: "LPPL-1.3c"},
		{value: "Latex2e", text: "Latex2e"},
		{value: "Leptonica", text: "Leptonica"},
		{value: "LiLiQ-P-1.1", text: "LiLiQ-P-1.1"},
		{value: "LiLiQ-R-1.1", text: "LiLiQ-R-1.1"},
		{value: "LiLiQ-Rplus-1.1", text: "LiLiQ-Rplus-1.1"},
		{value: "Libpng", text: "Libpng"},
		{value: "MIT", text: "MIT"},
		{value: "MIT-CM", text: "MIT-CM"},
		{value: "MIT-advertising", text: "MIT-advertising"},
		{value: "MIT-enna", text: "MIT-enna"},
		{value: "MIT-feh", text: "MIT-feh"},
		{value: "MITNFA", text: "MITNFA"},
		{value: "MPL-1.0", text: "MPL-1.0"},
		{value: "MPL-1.1", text: "MPL-1.1"},
		{value: "MPL-2.0", text: "MPL-2.0"},
		{value: "MPL-2.0-no-copyleft-exception", text: "MPL-2.0-no-copyleft-exception"},
		{value: "MS-PL", text: "MS-PL"},
		{value: "MS-RL", text: "MS-RL"},
		{value: "MTLL", text: "MTLL"},
		{value: "MakeIndex", text: "MakeIndex"},
		{value: "MirOS", text: "MirOS"},
		{value: "Motosoto", text: "Motosoto"},
		{value: "Multics", text: "Multics"},
		{value: "Mup", text: "Mup"},
		{value: "NASA-1.3", text: "NASA-1.3"},
		{value: "NBPL-1.0", text: "NBPL-1.0"},
		{value: "NCSA", text: "NCSA"},
		{value: "NGPL", text: "NGPL"},
		{value: "NLOD-1.0", text: "NLOD-1.0"},
		{value: "NLPL", text: "NLPL"},
		{value: "NOSL", text: "NOSL"},
		{value: "NPL-1.0", text: "NPL-1.0"},
		{value: "NPL-1.1", text: "NPL-1.1"},
		{value: "NPOSL-3.0", text: "NPOSL-3.0"},
		{value: "NRL", text: "NRL"},
		{value: "NTP", text: "NTP"},
		{value: "Naumen", text: "Naumen"},
		{value: "NetCDF", text: "NetCDF"},
		{value: "Newsletr", text: "Newsletr"},
		{value: "Nokia", text: "Nokia"},
		{value: "Noweb", text: "Noweb"},
		{value: "Nunit", text: "Nunit"},
		{value: "OCCT-PL", text: "OCCT-PL"},
		{value: "OCLC-2.0", text: "OCLC-2.0"},
		{value: "ODbL-1.0", text: "ODbL-1.0"},
		{value: "OFL-1.0", text: "OFL-1.0"},
		{value: "OFL-1.1", text: "OFL-1.1"},
		{value: "OGTSL", text: "OGTSL"},
		{value: "OLDAP-1.1", text: "OLDAP-1.1"},
		{value: "OLDAP-1.2", text: "OLDAP-1.2"},
		{value: "OLDAP-1.3", text: "OLDAP-1.3"},
		{value: "OLDAP-1.4", text: "OLDAP-1.4"},
		{value: "OLDAP-2.0", text: "OLDAP-2.0"},
		{value: "OLDAP-2.0.1", text: "OLDAP-2.0.1"},
		{value: "OLDAP-2.1", text: "OLDAP-2.1"},
		{value: "OLDAP-2.2", text: "OLDAP-2.2"},
		{value: "OLDAP-2.2.1", text: "OLDAP-2.2.1"},
		{value: "OLDAP-2.2.2", text: "OLDAP-2.2.2"},
		{value: "OLDAP-2.3", text: "OLDAP-2.3"},
		{value: "OLDAP-2.4", text: "OLDAP-2.4"},
		{value: "OLDAP-2.5", text: "OLDAP-2.5"},
		{value: "OLDAP-2.6", text: "OLDAP-2.6"},
		{value: "OLDAP-2.7", text: "OLDAP-2.7"},
		{value: "OLDAP-2.8", text: "OLDAP-2.8"},
		{value: "OML", text: "OML"},
		{value: "OPL-1.0", text: "OPL-1.0"},
		{value: "OSET-PL-2.1", text: "OSET-PL-2.1"},
		{value: "OSL-1.0", text: "OSL-1.0"},
		{value: "OSL-1.1", text: "OSL-1.1"},
		{value: "OSL-2.0", text: "OSL-2.0"},
		{value: "OSL-2.1", text: "OSL-2.1"},
		{value: "OSL-3.0", text: "OSL-3.0"},
		{value: "OpenSSL", text: "OpenSSL"},
		{value: "PDDL-1.0", text: "PDDL-1.0"},
		{value: "PHP-3.0", text: "PHP-3.0"},
		{value: "PHP-3.01", text: "PHP-3.01"},
		{value: "Plexus", text: "Plexus"},
		{value: "PostgreSQL", text: "PostgreSQL"},
		{value: "Python-2.0", text: "Python-2.0"},
		{value: "QPL-1.0", text: "QPL-1.0"},
		{value: "Qhull", text: "Qhull"},
		{value: "RHeCos-1.1", text: "RHeCos-1.1"},
		{value: "RPL-1.1", text: "RPL-1.1"},
		{value: "RPL-1.5", text: "RPL-1.5"},
		{value: "RPSL-1.0", text: "RPSL-1.0"},
		{value: "RSA-MD", text: "RSA-MD"},
		{value: "RSCPL", text: "RSCPL"},
		{value: "Rdisc", text: "Rdisc"},
		{value: "Ruby", text: "Ruby"},
		{value: "SAX-PD", text: "SAX-PD"},
		{value: "SCEA", text: "SCEA"},
		{value: "SGI-B-1.0", text: "SGI-B-1.0"},
		{value: "SGI-B-1.1", text: "SGI-B-1.1"},
		{value: "SGI-B-2.0", text: "SGI-B-2.0"},
		{value: "SISSL", text: "SISSL"},
		{value: "SISSL-1.2", text: "SISSL-1.2"},
		{value: "SMLNJ", text: "SMLNJ"},
		{value: "SMPPL", text: "SMPPL"},
		{value: "SNIA", text: "SNIA"},
		{value: "SPL-1.0", text: "SPL-1.0"},
		{value: "SWL", text: "SWL"},
		{value: "Saxpath", text: "Saxpath"},
		{value: "Sendmail", text: "Sendmail"},
		{value: "SimPL-2.0", text: "SimPL-2.0"},
		{value: "Sleepycat", text: "Sleepycat"},
		{value: "Spencer-86", text: "Spencer-86"},
		{value: "Spencer-94", text: "Spencer-94"},
		{value: "Spencer-99", text: "Spencer-99"},
		{value: "SugarCRM-1.1.3", text: "SugarCRM-1.1.3"},
		{value: "TCL", text: "TCL"},
		{value: "TMate", text: "TMate"},
		{value: "TORQUE-1.1", text: "TORQUE-1.1"},
		{value: "TOSL", text: "TOSL"},
		{value: "UPL-1.0", text: "UPL-1.0"},
		{value: "Unicode-TO", text: "Unicode-TO"},
		{value: "Unlicense", text: "Unlicense"},
		{value: "VOSTROM", text: "VOSTROM"},
		{value: "VSL-1.0", text: "VSL-1.0"},
		{value: "Vim", text: "Vim"},
		{value: "W3C", text: "W3C"},
		{value: "W3C-19980720", text: "W3C-19980720"},
		{value: "WTFPL", text: "WTFPL"},
		{value: "Watcom-1.0", text: "Watcom-1.0"},
		{value: "Wsuipa", text: "Wsuipa"},
		{value: "X11", text: "X11"},
		{value: "XFree86-1.1", text: "XFree86-1.1"},
		{value: "XSkat", text: "XSkat"},
		{value: "Xerox", text: "Xerox"},
		{value: "Xnet", text: "Xnet"},
		{value: "YPL-1.0", text: "YPL-1.0"},
		{value: "YPL-1.1", text: "YPL-1.1"},
		{value: "ZPL-1.1", text: "ZPL-1.1"},
		{value: "ZPL-2.0", text: "ZPL-2.0"},
		{value: "ZPL-2.1", text: "ZPL-2.1"},
		{value: "Zed", text: "Zed"},
		{value: "Zend-2.0", text: "Zend-2.0"},
		{value: "Zimbra-1.3", text: "Zimbra-1.3"},
		{value: "Zimbra-1.4", text: "Zimbra-1.4"},
		{value: "Zlib", text: "Zlib"},
		{value: "bzip2-1.0.5", text: "bzip2-1.0.5"},
		{value: "bzip2-1.0.6", text: "bzip2-1.0.6"},
		{value: "curl", text: "curl"},
		{value: "diffmark", text: "diffmark"},
		{value: "dvipdfm", text: "dvipdfm"},
		{value: "eGenix", text: "eGenix"},
		{value: "gSOAP-1.3b", text: "gSOAP-1.3b"},
		{value: "gnuplot", text: "gnuplot"},
		{value: "iMatix", text: "iMatix"},
		{value: "libtiff", text: "libtiff"},
		{value: "mpich2", text: "mpich2"},
		{value: "psfrag", text: "psfrag"},
		{value: "psutils", text: "psutils"},
		{value: "xinetd", text: "xinetd"},
		{value: "xpp", text: "xpp"},
		{value: "zlib-acknowledgement", text: "zlib-acknowledgement"},
		{value: "Freeware", text: "Freeware"},
		{value: "Proprietary", text: "Proprietary"},
		{value: "Other", text: "Other"},
		{value: "Not licensed", text: "Not licensed"}
	];

	$scope.costOptions = [
		{value: "Free of charge", text: "Free of charge"},
		{value: "Free of charge (with restrictions)", text: "Free of charge (with restrictions)"},
		{value: "Commercial", text: "Commercial"}
	];

	$scope.languageOptions = [
		{value: "ActionScript", text: "ActionScript"},
		{value: "Ada", text: "Ada"},
		{value: "AppleScript", text: "AppleScript"},
		{value: "Assembly language", text: "Assembly language"},
		{value: "AWK", text: "AWK"},
		{value: "Bash", text: "Bash"},
		{value: "C", text: "C"},
		{value: "C#", text: "C#"},
		{value: "C++", text: "C++"},
		{value: "COBOL", text: "COBOL"},
		{value: "ColdFusion", text: "ColdFusion"},
		{value: "CWL", text: "CWL"},
		{value: "D", text: "D"},
		{value: "Delphi", text: "Delphi"},
		{value: "Dylan", text: "Dylan"},
		{value: "Eiffel", text: "Eiffel"},
		{value: "Elm", text: "Elm"},
		{value: "Forth", text: "Forth"},
		{value: "Fortran", text: "Fortran"},
		{value: "Groovy", text: "Groovy"},
		{value: "Haskell", text: "Haskell"},
		{value: "Icarus", text: "Icarus"},
		{value: "Java", text: "Java"},
		{value: "JavaScript", text: "JavaScript"},
		{value: "JSP", text: "JSP"},
		{value: "Julia", text: "Julia"},
		{value: "LabVIEW", text: "LabVIEW"},
		{value: "Lisp", text: "Lisp"},
		{value: "Lua", text: "Lua"},
		{value: "Maple", text: "Maple"},
		{value: "Mathematica", text: "Mathematica"},
		{value: "MATLAB", text: "MATLAB"},
		{value: "MLXTRAN", text: "MLXTRAN"},
		{value: "NMTRAN", text: "NMTRAN"},
		{value: "OCaml", text: "OCaml"},
		{value: "Pascal", text: "Pascal"},
		{value: "Perl", text: "Perl"},
		{value: "PHP", text: "PHP"},
		{value: "Prolog", text: "Prolog"},
		{value: "PyMOL", text: "PyMOL"},
		{value: "Python", text: "Python"},
		{value: "R", text: "R"},
		{value: "Racket", text: "Racket"},
		{value: "REXX", text: "REXX"},
		{value: "Ruby", text: "Ruby"},
		{value: "Rust", text: "Rust"},
		{value: "SAS", text: "SAS"},
		{value: "Scala", text: "Scala"},
		{value: "Scheme", text: "Scheme"},
		{value: "Shell", text: "Shell"},
		{value: "Smalltalk", text: "Smalltalk"},
		{value: "SQL", text: "SQL"},
		{value: "Turing", text: "Turing"},
		{value: "Verilog", text: "Verilog"},
		{value: "VHDL", text: "VHDL"},
		{value: "Visual Basic", text: "Visual Basic"},
		{value: "XAML", text: "XAML"},
		{value: "Other", text: "Other"}
	];

	$scope.platformOptions = [
		{value: "Mac", text: "Mac"},
		{value: "Linux", text: "Linux"},
		{value: "Windows", text: "Windows"},
	];

	$scope.accessibilityOptions = [
		{value: "Open access", text: "Open access"},
		{value: "Open access (with restrictions)", text: "Open access (with restrictions)"},
		{value: "Restricted access", text: "Restricted access"}
	];

	$scope.maturityOptions = [
		{value: "Emerging", text: "Emerging"},
		{value: "Mature", text: "Mature"},
		{value: "Legacy", text: "Legacy"}
	];

	$scope.toolTypeOptions = [
		{value: "Bioinformatics portal", text: "Bioinformatics portal"},
		{value: "Command-line tool", text: "Command-line tool"},
		{value: "Database portal", text: "Database portal"},
		{value: "Desktop application", text: "Desktop application"},
		{value: "Library", text: "Library"},
		{value: "Ontology", text: "Ontology"},
		{value: "Plug-in", text: "Plug-in"},
		{value: "Script", text: "Script"},
		{value: "SPARQL endpoint", text: "SPARQL endpoint"},
		{value: "Suite", text: "Suite"},
		{value: "Web application", text: "Web application"},
		{value: "Web API", text: "Web API"},
		{value: "Web service", text: "Web service"},
		{value: "Workbench", text: "Workbench"},
		{value: "Workflow", text: "Workflow"}
	];

	$scope.linkTypeOptions = [
		{value: "Discussion forum", text: "Discussion forum"},
		{value: "Galaxy service", text: "Galaxy service"},
		{value: "Helpdesk", text: "Helpdesk"},
		{value: "Issue tracker", text: "Issue tracker"},
		{value: "Mailing list", text: "Mailing list"},
		{value: "Mirror", text: "Mirror"},
		{value: "Repository", text: "Repository"},
		{value: "Service", text: "Service"},
		{value: "Social media", text: "Social media"},
		{value: "Software catalogue", text: "Software catalogue"},
		{value: "Technical monitoring", text: "Technical monitoring"},
		{value: "Other", text: "Other"}
	];

	$scope.downloadTypeOptions = [
		{value: "Downloads page", text: "Downloads page"},
		{value: "API specification", text: "API specification"},
		{value: "Biological data", text: "Biological data"},
		{value: "Binaries", text: "Binaries"},
		{value: "Command-line specification", text: "Command-line specification"},
		{value: "Container file", text: "Container file"},
		{value: "Icon", text: "Icon"},
		{value: "Screenshot", text: "Screenshot"},
		{value: "Software package", text: "Software package"},
		{value: "Source code", text: "Source code"},
		{value: "Test data", text: "Test data"},
		{value: "Test script", text: "Test script"},
		{value: "Tool wrapper (CWL)", text: "Tool wrapper (CWL)"},
		{value: "Tool wrapper (Galaxy)", text: "Tool wrapper (Galaxy)"},
		{value: "Tool wrapper (Taverna)", text: "Tool wrapper (Taverna)"},
		{value: "Tool wrapper (Other)", text: "Tool wrapper (Other)"},
		{value: "VM Image", text: "VM Image"},
		{value: "Other", text: "Other"}
	];

	$scope.documentationTypeOptions = [
		{value: "API documentation", text: "API documentation"},
		{value: "Citation instructions", text: "Citation instructions"},
		{value: "Code of conduct", text: "Code of conduct"},
		{value: "Command-line options", text: "Command-line options"},
		{value: "Contributions policy", text: "Contributions policy"},
		{value: "FAQ", text: "FAQ"},
		{value: "General", text: "General"},
		{value: "Governance", text: "Governance"},
		{value: "Installation instructions", text: "Installation instructions"},
		{value: "Quick start guide", text: "Quick start guide"},
		{value: "Release notes", text: "Release notes"},
		{value: "Terms of use", text: "Terms of use"},
		{value: "Training material", text: "Training material"},
		{value: "User manual", text: "User manual"},
		{value: "Other", text: "Other"}
	];

	$scope.publicationTypeOptions = [
		{value: "Primary", text: "Primary"},
		{value: "Benchmarking study", text: "Benchmarking study"},
		{value: "Method", text: "Method"},
		{value: "Usage", text: "Usage"},
		{value: "Review", text: "Review"},
		{value: "Other", text: "Other"}
	];

	$scope.entityTypeOptions = [
		{value: "Person", text: "Person"},
		{value: "Project", text: "Project"},
		{value: "Division", text: "Division"},
		{value: "Institute", text: "Institute"},
		{value: "Consortium", text: "Consortium"},
		{value: "Funding agency", text: "Funding agency"}
	];

	$scope.roleTypeOptions = [
		{value: "Primary contact", text: "Primary contact"},
		{value: "Contributor", text: "Contributor"},
		{value: "Developer", text: "Developer"},
		{value: "Documentor", text: "Documentor"},
		{value: "Maintainer", text: "Maintainer"},
		{value: "Provider", text: "Provider"},
		{value: "Support", text: "Support"}
	];

	$scope.elixirPlatformOptions = [
		{value: "Data", text: "Data"},
		{value: "Tools", text: "Tools"},
		{value: "Compute", text: "Compute"},
		{value: "Interoperability", text: "Interoperability"},
		{value: "Training", text: "Training"}
	];

	$scope.elixirNodeOptions = [
		{value: "Belgium", text: "Belgium"},
		{value: "Czech Republic", text: "Czech Republic"},
		{value: "Denmark", text: "Denmark"},
		{value: "EMBL", text: "EMBL"},
		{value: "Estonia", text: "Estonia"},
		{value: "Finland", text: "Finland"},
		{value: "France", text: "France"},
		{value: "Germany", text: "Germany"},
		{value: "Greece", text: "Greece"},
		{value: "Hungary", text: "Hungary"},
		{value: "Ireland", text: "Ireland"},
		{value: "Israel", text: "Israel"},
		{value: "Italy", text: "Italy"},
		{value: "Luxembourg", text: "Luxembourg"},
		{value: "Netherlands", text: "Netherlands"},
		{value: "Norway", text: "Norway"},
		{value: "Portugal", text: "Portugal"},
		{value: "Slovenia", text: "Slovenia"},
		{value: "Spain", text: "Spain"},
		{value: "Sweden", text: "Sweden"},
		{value: "Switzerland", text: "Switzerland"},
		{value: "UK", text: "UK"}
	];

	$scope.elixirCommunityOptions = [
		{value: "3D-BioInfo", text: "3D-BioInfo", link: "3d-bioinfo"},
		{value: "Federated Human Data", text: "Federated Human Data", link: "human-data"},
		{value: "Galaxy", text: "Galaxy", link: "galaxy"},
		{value: "Human Copy Number Variation", text: "Human Copy Number Variation", link: "hcnv"},
		{value: "Intrinsically Disordered Proteins", text: "Intrinsically Disordered Proteins", link: "intrinsically-disordered-proteins"},
		{value: "Marine Metagenomics", text: "Marine Metagenomics", link: "marine-metagenomics"},
		{value: "Metabolomics", text: "Metabolomics", link: "metabolomics"},
		{value: "Microbial Biotechnology", text: "Microbial Biotechnology", link: "microbial-biotechnology"},
		{value: "Plant Sciences", text: "Plant Sciences", link: "plant-sciences"},
		{value: "Proteomics", text: "Proteomics", link: "proteomics"},
		{value: "Rare Diseases", text: "Rare Diseases", link: "rare-diseases"}
		
	];

	$scope.otherIdTypeOptions = [
		{value: "doi", text: "doi"},
		{value: "rrid", text: "rrid"},
		{value: "cpe", text: "cpe"}
	];

	$scope.relationTypeOptions = [
		{value: "isNewVersionOf", text: "isNewVersionOf"},
		{value: "hasNewVersion", text: "hasNewVersion"},
		{value: "uses", text: "uses"},
		{value: "usedBy", text: "usedBy"},
		{value: "includes", text: "includes"},
		{value: "includedIn", text: "includedIn"}

	];

	$scope.confidenceOptions = [
		{value: "tool", text: "tool"},
		{value: "high", text: "high"},
		{value: "medium", text: "medium"},
		{value: "low", text: "low"},
		{value: "very low", text: "very low"},
	];

	$scope.$watch('software.license', function(newValue) {
        if (newValue === "") {
            // Remove the license property if the empty option is selected
            delete $scope.software.license;
        }
    });

}])
.controller('ToolUpdateController', ['$scope', '$controller','$timeout','$state', '$stateParams', 'Tool', 'ToolUpdateValidator', 'CommunityCollection', function($scope, $controller, $timeout, $state, $stateParams, Tool, ToolUpdateValidator, CommunityCollection) {
	// inherit common controller
	$controller('ToolEditController', {$scope: $scope});

	// sets which controller is in use, so the HTML can adapt
	$scope.controller = 'update';

	// set the ID to not autoupdate when name is changed
	$scope.autoUpdateId = false;
	$scope.CommunityCollection = CommunityCollection;
	$scope.validateButtonClick = function() {
		$timeout(function() {
			$scope.sendResource(ToolUpdateValidator.update, $scope.validationProgress, false, 'update-validate');
		},100);
	}

	$scope.registerButtonClick = function() {
		$timeout(function() {
			if (confirm("Are you sure you want to update the resource? ")) {
				$scope.sendResource(Tool.update, $scope.savingProgress, false, 'update');
			}
		},100);
	}

	$scope.deleteButtonClick = function() {
		$timeout(function() {
			if (confirm("Are you sure you want to remove the resource? ")) {
				if (confirm("This will remove the resource and cannot be undone. Are you sure you want to continue? ")) {
					$scope.sendResource(Tool.remove, $scope.deletingProgress, true, 'delete');
				}
			}
		},100);
	}

	$scope.naviagateToTool = function(biotoolsID) {
		$timeout(function() {
			if (confirm("Make sure you save before navigating away! Are you sure you want to leave? ")) {
				$state.go('tool', {id: biotoolsID}, {reload: true});
			}
		},100);
	}


	// when a tool is being updated, display the current URL
	// $scope.$watch('software', function() {
	// 	$scope.setURL();
	// })

}])
.controller('ToolCreateController', ['$scope', '$controller', '$timeout', 'ToolListConnection', 'ToolCreateValidator', 'User', '$stateParams',  'CommunityCollection',function($scope, $controller, $timeout, ToolListConnection, ToolCreateValidator, User, $stateParams, CommunityCollection){
	// inherit common controller
	$controller('ToolEditController', {$scope: $scope});
	$scope.orderby = 'text';
	// sets which controller is in use, so the HTML can adapt
	$scope.controller = 'create';

	// initially set the ID to change automatically when name is modified
	$scope.biotoolsIDDisabled = true;
	$scope.editIdButtonText = 'Edit ID';
	$scope.CommunityCollection = CommunityCollection;
	// remove or replace all URL unsafe characters and set software.id
	$scope.makeIdURLSafe = function(value) {
		if (typeof value != 'undefined' && $scope.biotoolsIDDisabled) {
			$scope.software.biotoolsID = value.replace(/[^a-zA-Z0-9_~ .-]*/g,'').replace(/[ ]+/g, '_').toLowerCase();
		}else if ($scope.biotoolsIDDisabled){
			$scope.software.biotoolsID = "";
		}
		
	}

	$scope.editIdToggleButtonClick = function () {
		$scope.biotoolsIDDisabled = !$scope.biotoolsIDDisabled;
		$scope.makeIdURLSafe($scope.software.name);

		if ($scope.biotoolsIDDisabled){
			$scope.editIdButtonText = 'Edit ID';
		}else{
			$scope.editIdButtonText = 'From Name';
		}
	}

	

	$scope.validateButtonClick = function() {
		$timeout(function() {
			$scope.sendResource(ToolCreateValidator.save, $scope.validationProgress, false, 'create-validate');
		},100);
	}

	$scope.registerButtonClick = function() {
		if (confirm("Are you sure you want to save the resource?\nOnce saved the tool ID cannot be changed!")) {
			$timeout(function() {
				$scope.sendResource(ToolListConnection.save, $scope.savingProgress, false, 'create');
			},100);
		}
	}

	// TODO: needs to keep it DRY and in a service
	// function to clean all nulls from tool gotten from API
	function cleanNulls (object) {
		for (var key in object) {
			if (object[key] == null) {
				delete object[key]
			} else if (object[key].constructor === Array) {
				if (object[key].length == 0) {
					delete object[key]
				} else {
					for (var i in object[key]) {
						cleanNulls(object[key][i])
					}
				}
			} else if (typeof object[key] === 'object') {
				cleanNulls(object[key]);
			}
		}
	}

	if (typeof $stateParams.newVersionOf !== 'undefined') {
		$scope.newVersion = true;
		$scope.software = ToolLatest.get({id: $stateParams.newVersionOf}, function(response) {
			// success handler
			cleanNulls($scope.software);
			$scope.software.version = null;
		}, function(response) {
			// error handler
			if (response.status == 404) {
				$scope.notFound = true;
			}
		});
	} else {
		$scope.newVersion = false;
		// create the 'empty' software object
		$timeout(function() {
			$scope.software = {
				"owner": $scope.User.getUsername(),
				"name":"",
				"description":"",
				"homepage":""
				,
			};
		},100);
	}



}])
.controller('LoginController', ['$scope', '$state', 'djangoAuth', '$rootScope',function($scope, $state, djangoAuth, $rootScope) {
	$scope.credentials = {};

	$scope.loginButtonClick = function() {
		djangoAuth.login($scope.credentials.username, $scope.credentials.password)
		.then(function (response) {
			// go to states set before redirection to login
			if(typeof $rootScope.toState == 'undefined' || /signup/.test($rootScope.toState.name) || /reset-password/.test($rootScope.toState.name)) {
				$state.go('search');
			} else {
				$state.go($rootScope.toState.name, $rootScope.toStateParams);
			}
		}, function (response) {
			$scope.loginErrors = response.general_errors;
		});
	}

	// clean errors when credentials are changed
	$scope.$watch('credentials', function() {
		if ($scope.loginErrors) {
			$scope.loginErrors.pop();
			delete $scope.loginErrors;
		}
	}, true);
}])
.controller('SignupController', ['$scope', '$state', 'djangoAuth', '$rootScope', '$timeout', function($scope, $state, djangoAuth, $rootScope, $timeout) {
	$scope.credentials = {};
	$scope.error_message = {};
	$scope.error_message.username = '';
	$scope.error_message.email = '';
	$scope.error_message.creation = '';

	// check if username is taken
	var initializing_username = true;
	$scope.$watch('credentials.username', function(newValue, oldValue, scope) {
		if (!initializing_username) {
			$scope.error_message.username = '';
			djangoAuth.register($scope.credentials.username, null, null, null, null)
			.then(function (response) {
				// success never happens since parameters are missing
			}, function (response) {
				if (response.hasOwnProperty('username')) {
					$scope.error_message.username = 'Username is already taken.';
				}
			});
		} else {
			initializing_username = false;
		}
	});

	// check if email is taken
	var initializing_email = true;
	$scope.$watch('credentials.email', function(newValue, oldValue, scope) {
		if (!initializing_email) {
			$scope.error_message.email = '';
			djangoAuth.register(null, null, null, $scope.credentials.email, null)
			.then(function (response) {
				// success never happens since parameters are missing
			}, function (response) {
				if (response.hasOwnProperty('email')) {
					$scope.error_message.email = 'Email is invalid or already taken.';
				}
			});
		} else {
			initializing_email = false;
		}
	});

	$scope.signupButtonClick = function() {
		$scope.loading = true;
		$timeout(function() {
			djangoAuth.register($scope.credentials.username, $scope.credentials.password, $scope.credentials.password, $scope.credentials.email, null)
			.then(function (response) {
				$state.go('signup.success');
				$scope.loading = false;
			}, function (response) {
				$scope.error_message.email = response.email.join();
				$scope.error_message.username = response.username.join();
				$scope.error_message.creation = response.message;
				$scope.loading = false;
			});
		},100);
	}
}])
.controller('SignupVerifyEmailKeyController', ['$scope', '$state', '$stateParams', 'djangoAuth', function($scope, $state, $stateParams, djangoAuth) {
	$scope.error_message = '';

	djangoAuth.verify($stateParams.key)
	.then(function (response) {
		$state.go('signup.verify-email.success');
	}, function (response) {
		$scope.error_message = response.message;
	});
}])
.controller('ResetPasswordController', ['$scope', '$state', '$stateParams', 'djangoAuth', function($scope, $state, $stateParams, djangoAuth) {
	$scope.credentials = {};
	$scope.error_message = '';
	$scope.success_message = '';

	$scope.loading = false;
	$scope.resetButtonClick = function() {
		$scope.error_message = '';
		$scope.success_message = '';
		$scope.loading = true;
		djangoAuth.resetPassword($scope.credentials.email)
		.then(function (response) {
			$scope.success_message = 'If this email is linked to an account, a reset link will be sent.';
			$scope.loading = false;
		}, function (response) {
			$scope.error_message = response;
			$scope.loading = false;
		});
	}
}])
.controller('ResetPasswordConfirmController', ['$scope', '$state', '$stateParams', 'djangoAuth', function($scope, $state, $stateParams, djangoAuth) {
	$scope.credentials = {};
	$scope.error_message = false;
	var uid = $stateParams.uid;
	var token = $stateParams.token;

	$scope.loading = false;
	$scope.resetButtonClick = function() {
		$scope.error_message = false;
		$scope.loading = true;
		djangoAuth.confirmReset(uid, token, $scope.credentials.password, $scope.credentials.password)
		.then(function (response) {
			$state.go('reset-password.confirm.success');
			$scope.loading = false;
		}, function (response) {
			$scope.error_message = true;
			$scope.loading = false;
		});
	}
}]);

function EdamModalCtrl($modalInstance, edam, onto, type, suggestions) {
	var vm = this;
	vm.data = angular.copy(edam);
	vm.onto = onto;
	vm.self = $modalInstance;
	vm.type = type;
	vm.suggestions = suggestions;

	vm.saveData = function () {
		if (isEmptyObject(vm.data)) {
			$modalInstance.dismiss('cancel');
			return;
		}
		$modalInstance.close(vm.data);
	};

	vm.apply_suggestion = function (suggestion) {
		vm.predicate = suggestion.term;
	};

	vm.customOrder = function (node) {
		if (!vm.suggestions) {
			return node.text.toLowerCase();
		}

		var isSuggested = containsSuggestion(node);
		return (isSuggested ? '0' : '1') + node.text.toLowerCase();
	};

	vm.isSuggested = function (node) {
		return vm.suggestions && containsSuggestion(node);
	};

	vm.cancel = function () {
		$modalInstance.dismiss('cancel');
	};

	function isEmptyObject(obj) {
		return angular.equals(obj, {});
	}

	function containsSuggestion(node) {
		return vm.suggestions.some(function (suggestion) {
			return suggestion.term === node.text;
		});
	}
}
