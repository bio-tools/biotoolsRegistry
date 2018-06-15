'use strict';

/* Services */

angular.module('elixir_front.services', [])
.service('Alert', function(){
	this.list = [];
	this.add = function(_message, _type) {
		this.list.push({msg: _message, type: _type, ttl:2});
	};
	this.remove = function(_index) {
		this.list.splice(_index, 1);
	}
})
.service('User', [function(){
	this.current = {};
	return {
		isLoggedIn: function () {
			return this.authenticated == true;                   
		},
		getUsername: function () {
			if (!_.isEmpty(this.current)) {
				return this.current.username;
			}
		},
		isSuperuser: function () {
			if (!_.isEmpty(this.current)) {
				return this.current.is_superuser;
			}
		},

	}
}])
.service('Query', [function(){
	this.current = [];
}])
.service('DomainConnection', ['$resource', function($resource){
	return $resource('/api/d/', null, {
		'query': {
			isArray: true,
			method:'GET'
		},
		'create': {
			method:'POST'
		}
	})
}])
.service('DomainDetailConnection', ['$resource', function($resource){
	return $resource('/api/d/:domain', {'domain': '@domain'}, {
		'query': {
			isArray:false,
			method:'GET'
		},
		'update': {
			method:'PUT'
		},
		'delete': {
			method:'DELETE'
		}
	})
}])
.service('Domain', ['DomainDetailConnection', function(DomainDetailConnection){
	var _this = this;
	this.current = {};
	this.loaded = false;
	this.set = function(domain) {
		_this.current = domain;
	}
	this.load = function(domain) {
		if (typeof domain != 'undefined') {
			var response = DomainDetailConnection.query({'domain':domain}, function(response) {
				_this.set(response.data);
				_this.loaded = true;
			});
		} else {
			_this.loaded = false;
		}
	}
	this.isLoaded = function() {
		return _this.loaded;
	}
	this.hasSubdomain = function() {
		return !_.isEmpty(_this.current);
	}
	this.hasTitle = function() {
		return _this.current.title !== undefined;
	}
	this.hasSubTitle = function() {
		return _this.current.sub_title !== undefined;
	}
	this.hasDescription = function() {
		return _this.current.description !== undefined;
	}
}])
.service('Highlighting', [function(){
	var _this = this;
	this.terms = [];
	this.purge = function() {
		while (_this.terms.length > 0) {
			_this.terms.pop();
		}
	}
	this.set = function(query_array) {
		_this.purge();
		for (var i in query_array) {
			_this.terms.push(query_array[i].text.replace(/['"]/g,""));
		}
	}
}])
.service('ToolListConnection', ['$resource', function($resource){
	return $resource('/api/t/', null, {
		'query': {
			isArray:false,
			method:'GET'
		},
		'update': {
			method:'PUT'
		}
	})
}])
.service('ToolListOverviewConnection', ['$resource', function($resource){
	return $resource('/api/tool-list/', null, {
		'query': {
			isArray:true,
			method:'GET'
		}
	})
}])
.service('ToolList', ['$stateParams', 'ToolListConnection', function($stateParams, ToolListConnection){
	var _this = this;
	this.count = 0;
	this.list = [];
	this.loading = true;

	this.refresh = function() {
		// enable spinner
		this.loading = true;

		// get tools
		var response = ToolListConnection.query($stateParams, function() {
			// disable spinner
			_this.loading = false;
			_this.count = response.count;
			_this.list = response.list;
		});
	}
}])
.factory('ToolTableDataSource', function() {
	var columnDescriptionForKey = function(key, hidden) {
		var widthCharMultiplier = 12;
		var columnDescription = {};
		if (key == 'Contact') {
			columnDescription = {field: 'contact', displayName: 'Contact', cellTemplate: '/partials/grid_cells/contactCell.html', width: '250', resizable: true};
		}
		else if (key == 'Name') {
			columnDescription = {field: 'name', displayName: 'Name', cellTemplate: '/partials/grid_cells/nameCell.html', width: '150', resizable: true};
		}
		else if (key == 'Operating System') {
			columnDescription = {field: 'operatingSystem', displayName: 'Operating System', cellTemplate: '/partials/grid_cells/platformCell.html', width: '100', resizable: true};
		}
		else if (key == 'Description') {
			columnDescription = {field: 'description', displayName: 'Description', width: '*', resizable: true, cellTemplate: '/partials/grid_cells/defaultCell.html'};
		}
		else if (key == 'Function') {
			columnDescription = {field: 'function', displayName: 'Function', width: '220', resizable: true, cellTemplate: '/partials/grid_cells/functionCell.html'};
		}
		else if (key == 'Input') {
			columnDescription = {field: 'function', displayName: 'Input', width: '240', resizable: true, cellTemplate: '/partials/grid_cells/inputCell.html'};
		}
		else if (key == 'Output') {
			columnDescription = {field: 'function', displayName: 'Output', width: '240', resizable: true, cellTemplate: '/partials/grid_cells/outputCell.html'};
		}
		else if (key == 'Topic') {
			columnDescription = {field: 'topic', displayName: 'Topic', width: '200', resizable: true, cellTemplate: '/partials/grid_cells/topicCell.html'};
		}
		else if (key == 'Homepage') {
			columnDescription = {field: 'homepage', displayName: 'Homepage', resizable: true, width: '100', cellTemplate: '/partials/grid_cells/urlCell.html'};
		}
		else if (key == 'Tool Type') {
			columnDescription = {field: 'toolType', displayName: 'Type', width: '150', resizable: true, cellTemplate: '/partials/grid_cells/listCell.html'};
		}
		else if (key == 'Publications') {
			columnDescription = {field: 'publication', displayName: 'Publications', width: '250', resizable: true, cellTemplate: '/partials/grid_cells/publicationsCell.html'};
		}
		else if (key == 'Collection') {
			columnDescription = {field: 'collectionID', displayName: 'Collection', width: '150', resizable: true, cellTemplate: '/partials/grid_cells/listCell.html'};
		}
		else if (key == 'Mirror') {
			columnDescription = {field: 'mirror', displayName: 'Mirror', width: '75', resizable: true, cellTemplate: '/partials/grid_cells/urlCell.html'};
		}
		else if (key == 'Uses') {
			columnDescription = {field: 'uses', displayName: 'Uses', width: '220', resizable: true,  cellTemplate: '/partials/grid_cells/usesCell.html'};
		}
		else if (key == 'Source registry') {
			columnDescription = {field: 'sourceRegistry', displayName: 'Source registry', width: '140', resizable: true, cellTemplate: '/partials/grid_cells/urlCell.html'};
		}
		else if (key == 'Cannonical ID') {
			columnDescription = {field: 'canonicalID', displayName: 'Cannonical ID', width: '120', resizable: true, cellTemplate: '/partials/grid_cells/defaultCell.html'};
		}
		else if (key == 'Documentation') {
			columnDescription = {field: 'documentation', displayName: 'Documentation', width: '160', resizable: true, cellTemplate: '/partials/grid_cells/linkListCell.html'};
		}
		else if (key == 'Link') {
			columnDescription = {field: 'link', displayName: 'Links', width: '160', resizable: true, cellTemplate: '/partials/grid_cells/linkListCell.html'};
		}
		else if (key == 'Download') {
			columnDescription = {field: 'download', displayName: 'Downloads', width: '160', resizable: true, cellTemplate: '/partials/grid_cells/linkListCell.html'};
		}
		else if (key == 'Language') {
			columnDescription = {field: 'language', displayName: 'Language', width: '120', resizable: true, cellTemplate: '/partials/grid_cells/listCell.html'};
		}
		else if (key == 'Credits') {
			columnDescription = {field: 'credit', displayName: 'Credits', width: '150', resizable: true, cellTemplate: '/partials/grid_cells/creditsCell.html'};
		}
		else if (key == 'Accessibility') {
			columnDescription = {field: key.toLowerCase(), displayName: key, width: '150', resizable: true, cellTemplate: '/partials/grid_cells/listCell.html'};
		}
		else if (key == 'Cost') {
			columnDescription = {field: key.toLowerCase(), displayName: key, width: '90', resizable: true, cellTemplate: '/partials/grid_cells/defaultCell.html'};
		}
		else {
			columnDescription = {field: key.toLowerCase(), displayName: key, width: key.length * widthCharMultiplier, resizable: true, cellTemplate: '/partials/grid_cells/defaultCell.html'};
		}
		columnDescription.enableHiding = true;
		columnDescription.visible = hidden;
		columnDescription["minWidth"] = 120;
		return columnDescription;
	}

	return {
		columnsDescription : function(visibleColumns) {
			return [
			columnDescriptionForKey('Name', visibleColumns.indexOf('Name') != -1),
			columnDescriptionForKey('Description', visibleColumns.indexOf('Description') != -1),
			columnDescriptionForKey('Function', visibleColumns.indexOf('Function') != -1),
			columnDescriptionForKey('Input', visibleColumns.indexOf('Input') != -1),
			columnDescriptionForKey('Output', visibleColumns.indexOf('Output') != -1),
			columnDescriptionForKey('Topic', visibleColumns.indexOf('Topic') != -1),
			columnDescriptionForKey('Tool Type', visibleColumns.indexOf('Tool Type') != -1),
			columnDescriptionForKey('Accessibility', visibleColumns.indexOf('Accessibility') != -1),
			columnDescriptionForKey('Publications', visibleColumns.indexOf('Publications') != -1),
			columnDescriptionForKey('Collection', visibleColumns.indexOf('Collection') != -1),
			columnDescriptionForKey('Mirror', visibleColumns.indexOf('Mirror') != -1),
			columnDescriptionForKey('Link', visibleColumns.indexOf('Link') != -1),
			columnDescriptionForKey('Download', visibleColumns.indexOf('Download') != -1),
			columnDescriptionForKey('Uses', visibleColumns.indexOf('Uses') != -1),
			columnDescriptionForKey('Source registry', visibleColumns.indexOf('Source registry') != -1),
			columnDescriptionForKey('Homepage', visibleColumns.indexOf('Homepage') != -1),
			columnDescriptionForKey('Cannonical ID', visibleColumns.indexOf('Cannonical ID') != -1),
			columnDescriptionForKey('Cost', visibleColumns.indexOf('Cost') != -1),
			columnDescriptionForKey('Documentation', visibleColumns.indexOf('Documentation') != -1),
			columnDescriptionForKey('Maturity', visibleColumns.indexOf('Maturity') != -1),
			columnDescriptionForKey('Operating System', visibleColumns.indexOf('Operating System') != -1),
			columnDescriptionForKey('Language', visibleColumns.indexOf('Language') != -1),
			columnDescriptionForKey('License', visibleColumns.indexOf('License') != -1),
			columnDescriptionForKey('Credits', visibleColumns.indexOf('Credits') != -1),
			columnDescriptionForKey('Contact', visibleColumns.indexOf('Contact') != -1)
			];
		}
	}
})
.service('ToolPaginator', function(){
	this.currentPage = 1;
	// pagination settings
	this.maxSize = 5;
	this.pageSize = 10;
})
.service('ToolSorter', function(){
	var _this = this;
	this.order = true;
	this.list = [
	{"attrName": "lastUpdate", "text": "Updated"},
	{"attrName": "additionDate", "text": "Added"},
	{"attrName": "name", "text": "Name"},
	{"attrName": "citationCount", "text": "Citation Count"},
	{"attrName": "citationDate", "text": "Publication Date"}
	];
	this.sortBy = this.list[0];

	var scoreEntry = {"attrName": "score", "text": "Score"};

	this.setSortOption = function(parameter) {
		if (parameter == undefined) {
			this.sortBy = this.list[0];
		}
		else {
			for (var i = 0; i < this.list.length; i++) {
				if (this.list[i]['attrName'] == parameter) {
					this.sortBy = this.list[i];
				}
			}
		}
	} 

	// add 'Score' to the list of sortable attributes
	this.addScore = function () {
		if (!_.isEqual(scoreEntry, _this.list[0])) {
			_this.list.unshift(scoreEntry);
			_this.sortBy = _this.list[0];
		}
	}

	// remove 'Score' from the list of sortable attributes
	this.removeScore = function () {
		if (_.isEqual(scoreEntry, _this.list[0])) {
			_this.list.splice(0,1);
			_this.sortBy = _this.list[0];
		}
	}
})
.service('DisplayModeSelector', function(){
	this.list = [
	{"attrName": "cards", "text": "Compact"},
	{"attrName": "grid", "text": "Detailed"}
	];
	this.mode = this.list[0];
})
.factory('Tool', ['$resource', function($resource){
	return $resource('/api/t/:id', null, {
		'query': {
			isArray:false,
			method:'GET'
		},
		'update': {
			method:'PUT'
		}
	})
}])
.factory('DisownToolService', ['$resource', function($resource){
	return $resource('/api/t/:id/disown', {'id': '@id'}, {
		'disown': {
			method:'POST'
		}
	})
}])
.factory('ToolCreateValidator', ['$resource', function($resource){
	return $resource('/api/t/:id/validate', null, {
		'update': {
			method:'PUT'
		}
	})
}])
.factory('ToolUpdateValidator', ['$resource', function($resource){
	return $resource('/api/t/:id/validate', null, {
		'update': {
			method:'PUT'
		}
	})
}])
.factory('Ontology', ['$resource', function($resource){
	return $resource('/api/o/:name', null, {})
}])
.factory('UsedTerms', ['$resource', function($resource){
	return $resource('/api/used-terms/:usedTermName', null, {
		'query': {
			isArray:true,
			method:'GET'
		},
	})
}])
.service('Attribute', function() {
	this.description = {
		everything: {
			label: "Everything"
		},
		name: {
			description: "Resource name",
			label: "Name"
		},
		toolType: {
			description: "Type of tool. A tool may have more than one type reflecting its different facets.",
			label: "Tool type"
		},
		version: {
			description: "Current resource version",
			label: "Current version"
		},
		description: {
			description: "Free text description of the resource",
			label: "Description"
		},
		function: {
			description: "Scientific function of the resource",
			label: "Function"
		},
		functionDescription: {
			description: "Free text description of the function",
			label: "Function description"
		},
		functionName: {
			description: "Name of the function (EDAM term)",
			label: "Function Name"
		},
		input: {
			description: "Input specification",
			label: "Input"
		},
		dataType: {
			description: "Type of data (EDAM term)",
			label: "Data type"
		},
		dataFormat: {
			description: "Allowed format(s) of the data (EDAM terms)",
			label: "Data format"
		},
		dataDescription: {
			description: "Free text description of the data.",
			label: "Data description"
		},
		output: {
			description: "Output specification",
			label: "Output"
		},
		topic: {
			description: "General scientific domain of the resource (EDAM term)",
			label: "Topic"
		},
		homepage: {
			description: "Resource homepage (URL)",
			label: "Homepage URL"
		},
		contact: {
			description: "Primary points of contact, e.g. helpdesk or an individual",
			label: "Contact"
		},
		contactName: {
			description: "Name of contact",
			label: "Name"
		},
		contactEmail: {
			description: "Email address of contact",
			label: "E-mail"
		},
		resourceType: {
			description: "Basic resource type: Tool, Database etc.",
			label: "Resource type"
		},
		interface: {
			description: "Resource interfaces: Web UI, Command line etc.",
			label: "Interface"
		},
		publications: {
			description: "Publications relevant to the resource (PMCID, PMID or DOI)",
			label: "Publications"
		},
		publicationsPrimaryID: {
			description: "PMCID, PMID or DOI of the publication",
			label: "ID of the primary publication"
		},
		publicationsOtherID: {
			description: "PMCID, PMID or DOI of other relevant publications",
			label: "ID of other publications"
		},
		docs: {
			description: "Links to the documentation",
			label: "Documentation"
		},
		docsHome: {
			description: "Main page of documentation",
			label: "Main page"
		},
		docsTermsOfUse: {
			description: "Link to the Terms Of Use",
			label: "Terms of Use"
		},
		docsDownload: {
			description: "Link to the download instructions",
			label: "Download"
		},
		docsCitationInstructions: {
			description: "Link to the citation instructions",
			label: "Citation instructions"
		},
		docsDownloadSource: {
			description: "Source code downloads page (URL)",
			label: "Download source"
		},
		docsDownloadBinaries: {
			description: "Software binaries downloads page (URL)",
			label: "Download binaries"
		},
		docsGithub: {
			description: "Github page (URL)",
			label: "Github page"
		},
		affiliation: {
			description: "Entry owner",
			label: "Affiliation"
		},
		mirror: {
			description: "Mirror homepage (URL)",
			label: "Mirror"
		},
		collectionID: {
			description: "Names of collections of which the resource is a part, e.g. a suite, library etc.",
			label: "Collection"
		},
		sourceRegistry: {
			description: "Link to the registry (or other collection) from which the software was imported (URL)",
			label: "Source registry"
		},
		canonicalID: {
			description: "Canonical Identifier (typically a URI) of the resource, if one is available",
			label: "Canonical ID"
		},
		cost: {
			description: "Cost incurred by the resource",
			label: "Cost"
		},
		elixirInfo: {
			description: "Information specific to ELIXIR services",
			label: "ELIXIR info"
		},
		elixirStatus: {
			description: "ELIXIR Core Service",
			label: "ELIXIR status"
		},
		elixirNode: {
			description: "Name of one of countries participating in ELIXIR",
			label: "ELIXIR node"
		},
		maturity: {
			description: "Resource stage of development",
			label: "Maturity"
		},
		platform: {
			description: "Platforms supported by a downloadable software package",
			label: "Platform"
		},
		language: {
			description: "Languages (for APIs etc.) or technologies (for Web applications, applets etc.)",
			label: "Language"
		},
		license: {
			description: "Software or data usage license",
			label: "License"
		},
		credit: {
			description: "Entities that should be credited",
			label: "Credit"
		},
		creditsDeveloper: {
			description: "Name of person that developed the resource",
			label: "Developer"
		},
		creditsContributor: {
			description: "Name of person contributing to the resource",
			label: "Contributor"
		},
		creditsInstitution: {
			description: "Name of the institution that developed or provide the resource",
			label: "Institution"
		},
		creditsInfrastructure: {
			description: "Research infrastructure in which the resource was developed or provided",
			label: "Infrastructure"
		},
		creditsFunding: {
			description: "Details of grant funding supporting the resource",
			label: "Funding"
		},
		uses: {
			description: "Other resources this resource uses, e.g. as a data source, or auxillary program",
			label: "Uses"
		},
		usesName: {
			description: "Name of a resource that this resource uses",
			label: "Name"
		},
		usesHomepage: {
			description: "Homepage of a resource that this resource uses",
			label: "Homepage"
		},
		usesVersion: {
			description: "Version number of a resource that this resources uses",
			label: "Version"
		},
		operatingSystem: {
			description: "Operating system supported by a downloadable software package.",
			label: "Operating system"
		},
		accessibility: {
			description: "Whether the software is freely available for use.",
			label: "Accessibility"
		}
	};
})
.factory('CheckUserEditingRights', ['User', function(User) {
	return {
		canEdit: function(resource) {

			if (User.isSuperuser()) return true;

			if (User.getUsername() == resource.owner) {
				return true;
			}
			else if (resource.editPermission != undefined) {
				if (resource.editPermission.type == "public") {
					return true;
				}
				else if (resource.editPermission.type == "group") {
					for (var index in resource.editPermission.authors) {
						if (User.getUsername() == resource.editPermission.authors[index]) {
							return true;
						}
					}
				}
			}
			return false;
		},
		isOwner: function(resource) {
			if (User.getUsername() == resource.owner) {
				return true;
			}
			return false;
		}
	};
}])
.factory('ToolVersionProvider', ['$http', function ($http) {
	return {
		getVersions: function(toolId) {
			return $http({
				method: 'GET',
				url: '/api/tool/' + toolId + '/version'
			}).then(function successCallback(response) {
				return response.data;
			}, function errorCallback(response) {
				return [];
			})
		}
	};
}])
.factory('EnvironmentChecker', ['$http', function ($http) {
	return {
		getEnvironment: function() {
			return $http({
				method: 'GET',
				url: '/api/env/'
			}).then(function successCallback(response) {
				return response.data;
			}, function errorCallback(response) {
				return [];
			})
		}
	};
}]);
