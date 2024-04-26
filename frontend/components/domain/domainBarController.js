angular.module('elixir_front')
.controller('DomainBarController', ['$scope', 'djangoAuth', '$stateParams', '$timeout', 'Domain', function($scope, djangoAuth, $stateParams, $timeout, Domain) {
	// reference the service
	var vm = this;
	vm.Domain = Domain;
	
	$timeout(function() {
		Domain.load($stateParams['domain']);
	}, 500);
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
}]);