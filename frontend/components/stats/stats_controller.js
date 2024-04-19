angular.module('elixir_front.services')
// Gets stats info from the server.
.factory('Stats', ['$resource', function($resource){
	return $resource('/api/stats', null, {
		'query': { 
			isArray:false,
			method:'GET'
		}
	})
}])
.factory('StatsTotalEntries', ['$resource', function($resource){
	return $resource('/api/stats/total-entries', null, {
		'query': { 
			isArray:true,
			method:'GET'
		}
	})
}])
.factory('StatsUserData', ['$resource', function($resource){
	return $resource('/api/stats/users', null, {
		'query': { 
			isArray:true,
			method:'GET'
		}
	})
}])
.factory('TotalAnnotationsStatsData', ['$resource', function($resource){
	return $resource('/api/stats/annotation-count', null, {
		'query': { 
			isArray:true,
			method:'GET'
		}
	})
}])
// Get and manage the stats data from the server.
.service('StatsDataSource', ['$stateParams', 'Stats', 'StatsTotalEntries', 'StatsUserData', 'TotalAnnotationsStatsData', function($stateParams, Stats, StatsTotalEntries, StatsUserData, TotalAnnotationsStatsData) {
	var _this = this;
	this.isLoadingData = true;
	this.isLoadingTotalEntriesData = true;
	this.isLoadingUserStatsData = true;
	this.isLoadingTotalAnnotationsStats = true;
	this.statsData = {};
	this.totalEntriesData = {};
	this.userStatsData = {};
	this.totalAnnotationsStatsData = {};
	this.totalAnnotationsCount = function() {
		var totalCount = 0;
		for (var key in this.statsData.totalAnnotationCount) {
			var value = this.statsData.totalAnnotationCount[key];
			totalCount += value;
		}
		return totalCount;
	}
	// Operations
	this.fetchStatsData = function(completion) {
		this.isLoadingData = true;
		var response = Stats.query($stateParams, function() {
			_this.statsData = response;
			_this.isLoadingData = false;
			completion()
		});
	}
	this.fetchTotalEntriesData = function(completion) {
		this.isLoadingTotalEntriesData = true;
		var response = StatsTotalEntries.query($stateParams, function() {
			_this.totalEntriesData = response;
			_this.isLoadingTotalEntriesData = false;
			completion()
		});
	}
	this.fetchUserStatsData = function(completion) {
		this.isLoadingUserStatsData = true;
		var response = StatsUserData.query($stateParams, function() {
			_this.userStatsData = response;
			_this.isLoadingUserStatsData = false;
			completion();
		});
	}
	this.fetchTotalAnnotationsStatsData = function(completion) {
		this.isLoadingTotalAnnotationsStats = true;
		var response = TotalAnnotationsStatsData.query($stateParams, function() {
			_this.totalAnnotationsStatsData = response;
			_this.isLoadingTotalAnnotationsStats = false;
			completion();
		});
	}
}])
// Controller for the stats website.
angular.module('elixir_front.controllers').controller('StatsController', ['$scope', '$http', 'StatsDataSource', function($scope, $http, StatsDataSource) {
	// Initialization
	var _this = this;
	$scope.labels = [];
	$scope.labelsUsers = [];
	$scope.series = ['Total entries'];
	$scope.seriesEDAM = ['EDAM annotations'];
	$scope.seriesEDAMBreakdown = ['Data Type annotations', 'Topic annotations', 'Function annotations', 'Format annotations'];
	$scope.seriesUsers = ['Total contributors count', 'New contributors this month'];
	$scope.seriesTotalAnnotationDetail = ['Name', 'Description', 'Homepage', 'Tool Type', 'Unique Id', 'Topic', 'Publication', 'Contact', 'Operation', 'Documentation', 'Operating System', 'Input output', 'Code availability', 'Accessibility', 'Data format', 'Community', 'Downloads', 'Total'];
	$scope.seriesTotalAnnotation = ['Total'];
	$scope.data = [[]];
	$scope.dataEDAM = [[]];
	$scope.dataEDAMBreakdown = [[]];
	$scope.dataUsers = [[]];
	$scope.dataTotalAnnotation = [[]];
	$scope.dataTotalAnnotationDetail = [[]];
	$scope.totalAnnotationOptions = {
		tooltips: {
			titleFontSize: 10,
			bodyFontSize: 9,
			bodySpacing: 0
		}
	};
	$scope.statsDataSource = StatsDataSource;
	$scope.statsDataSource.fetchStatsData(function(){
		_this.initializeTopContributorsStatsGraph();
	});
	$scope.statsDataSource.fetchTotalEntriesData(function() {
		_this.initializeTotalEntriesGraph();
	});
	$scope.statsDataSource.fetchUserStatsData(function() {
		_this.initializeUserStatsGraph();
	});
	$scope.statsDataSource.fetchTotalAnnotationsStatsData(function() {
		_this.initializeTotalAnnotationsStatsGraph();
		_this.initializeTotalAnnotationsDetailStatsGraph();
	});
	$scope.topContributorsLabels = [];
	$scope.topContributorsData = [];
	$scope.topContributorsOptions = {legend: {display: true}};
	// Total Entries Grpah handling
	this.initializeTotalEntriesGraph = function() {
		var data = $scope.statsDataSource.totalEntriesData;
		$scope.labels = _.map(data, function(x) {
			var date = x.date.split('T')[0];
			return moment(date).format("MMM YY");
		});
		$scope.data = [_.map(data, function(x) {
			return x.entriesCount;
		})];
		$scope.dataEDAM = [_.map(data, function(x) {
			return x.edamAnnotationsCount;
		})];
		$scope.dataEDAMBreakdown = [_.map(data, function(x) {
			return x.dataTypeAnnotationsCount;
		}),
		_.map(data, function(x) {
			return x.topicAnnotationsCount;
		}),
		_.map(data, function(x) {
			return x.functionAnnotationsCount;
		}),
		_.map(data, function(x) {
			return x.formatAnnotationsCount;
		})];
	};
	// Total Entries Grpah handling
	this.initializeUserStatsGraph = function() {
		var data = $scope.statsDataSource.userStatsData;
		$scope.labelsUsers = _.map(data, function(x) {
			var date = x.date.split('T')[0];
			return moment(date).format("MMM YY");
		});
		$scope.dataUsers = [_.map(data, function(x) {
			return x.totalUsersCount;
		}),
		_.map(data, function(x) {
			return x.newUsersCount;
		})];
	};
	// Top contributors data.
	this.initializeTopContributorsStatsGraph = function() {
		var contributorData = $scope.statsDataSource.statsData.topContributors;
		$scope.topContributorsLabels = _.map(contributorData, function(x) {
			return x.domain;
		});
		$scope.topContributorsData = _.map(contributorData, function(x) {
			return x.count;
		});
	};
	// Total annotations data.
	this.initializeTotalAnnotationsStatsGraph = function() {
		var annotationData = $scope.statsDataSource.totalAnnotationsStatsData
		$scope.dataTotalAnnotation = [_.map(annotationData, function(x) {
			var data = x;
			var totalCount = 0;
			for (var key in data) {
				if (key != 'date' && !isNaN(data[key])) {
					totalCount += data[key];
				}
			}
			return totalCount;
		})];
	};
	this.initializeTotalAnnotationsDetailStatsGraph = function() {
		var annotationData = $scope.statsDataSource.totalAnnotationsStatsData
		$scope.dataTotalAnnotationDetail = [_.map(annotationData, function(x) {
			return x.nameAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.descriptionAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.homepageAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.toolTypeAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.uniqueIDAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.topicAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.publicationAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.contactAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.operationAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.documentationAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.operatingSystemAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.inputOutputAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.codeAvailabilityAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.accessibilityAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.dataFormatsAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.communityAnnotationCount;
		}),
		_.map(annotationData, function(x) {
			return x.downloadsAnnotationCount;
		})];
	};
}]);



