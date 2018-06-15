angular.module('elixir_front')
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
.service('Domain', ['DomainDetailConnection', '$rootScope', function(DomainDetailConnection, $rootScope){
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
	this.unload = function() {
		if (this.isLoaded() == true) {
			this.current = {};
			this.loaded = false;
		}
	}
}]);