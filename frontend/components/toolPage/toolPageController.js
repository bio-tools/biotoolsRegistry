angular.module('elixir_front')
.controller('ToolPageController', ['$scope', '$state', '$timeout', '$stateParams', 'Tool', 'User', 'CheckUserEditingRights', 'ResourceRequestProvider', 'ngMeta', 'Query', function($scope, $state, $timeout, $stateParams, Tool, User, CheckUserEditingRights, ResourceRequestProvider, ngMeta, Query) {
	$scope.notFound = false;
	$scope.versions = [];
	$scope.CheckUserEditingRights = CheckUserEditingRights;
	$scope.editingRequestedSuccess = null; 

	$scope.User = User;

	// go to 404 in special case when URL is /tool/
	if ($stateParams.id.length == 0) {
		$state.go('404');
	}
	
	$scope.topicNameClicked = function(topic) {
		$state.go('search', {'topic': topic.term});
	}

	$scope.functionNameClicked = function(functionName) {
		$state.go('search', {'operation': functionName.term});
	}

	$scope.inputNameClicked = function(inputName) {
		$state.go('search', {'input': inputName.data.term});
	}

	$scope.inputFormatNameClicked = function(formatName) {
		$state.go('search', {'input': formatName.term});
	}

	$scope.outputFormatNameClicked = function(formatName) {
		$state.go('search', {'output': formatName.term});
	}

	$scope.outputNameClicked = function(outputName) {
		$state.go('search', {'output': outputName.data.term});
	}

	$scope.toolsNameClicked = function(functionName) {
		$state.go('search', {'name': $scope.software.name});
	}

	$scope.collectionNameClicked = function(collectionName) {
		$state.go('search', {'collectionID': '"'+ collectionName + '"'});
	}

	$scope.creditNameClicked = function(creditName) {
		var url = $state.href('search', {'credit': '"'+ creditName + '"'});
		window.open(url,'_blank');
	}

	$scope.publicationDetailsExist = function() {
		for (var index in $scope.software.publication) {
			if ($scope.software.publication[index].metadata != null) {
				return true;
			}
		}
		return false;
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

	var initAltmetricsScore = function() {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = "https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js";
		document.body.appendChild(script);
	}

	$scope.altMetricsScorePublication = function() {
		var publication = ""
		for (var index in $scope.software.publication) {
			var publication = $scope.software.publication[index];
			if (publication.type == "Primary" && publication.doi) {
				publication = publication;
				break;
			}
			else {
				publication = publication;
			}
		}
		return publication;
	}

	$scope.versionSelected = function(versionId) {
		$state.go('tool', {id: $scope.software.id, version: versionId});
	}

	$scope.shouldLicenseBeALink = function(license) {
		return !_.includes(['Proprietary', 'Other', 'Unlicensed'], license);
	}

	$scope.setMetadataForSoftware = function(software) {
		ngMeta.setTitle(software.name, ' · bio.tools');
		ngMeta.setTag('description', software.description);
		ngMeta.setTag('og:title', software.name);
		ngMeta.setTag('og:description', software.description);
	}

	// get tool
	$scope.software = Tool.get($stateParams, function(response) {
		// success handler
		initAltmetricsScore();
		cleanNulls($scope.software);
		$scope.setMetadataForSoftware($scope.software)
		$timeout(function(){ window.OpEB_widgets.OpEB.apply(); }, 100);
	}, function(response) {
		// error handler
		if (response.status == 404) {
			$scope.notFound = true;
		}
	});

	$scope.requestOwnership = function(resourceId) {
		$scope.ownershipRequestedSuccess = null;
		ResourceRequestProvider.requestOwnership(resourceId).then(function successCallback(response) {
			$scope.ownershipRequestedSuccess = true;
		}, function errorCallback(response) {
			$scope.ownershipRequestedSuccess = false;
		});
	}

	$scope.requestEditing = function(resourceId) {
		$scope.editingRequestedSuccess = null; 
		ResourceRequestProvider.requestEditingRights(resourceId).then(function successCallback(response) {
			$scope.editingRequestedSuccess = true;
		}, function errorCallback(response) {
			$scope.editingRequestedSuccess = false;
		});
	}
}])
.directive("publicationDetailCallout", function(){
	return {
		restrict: 'A',
		templateUrl: 'components/toolPage/partials/publicationDetailCallout.html'
	};
})
.directive("toolPageLinkCallout", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			return '<div class="bs-callout-sm bs-callout-primary" style="border-left-color: ' + attr.color + ';">' +
			'<div class="tool-page-callout-header" style="color: black;">' + 
			'<a href="' + attr.url + '" tooltips tooltip-side="top" tooltip-content="' + attr.url + '">' + attr.name + ' › </a>' +
			'<i ng-show="' +  attr.toshow  + '" class="fa fa-question-circle" aria-hidden="true" style="font-size: 100%; margin-left: 0.5em; color: ' + attr.color + ';" tooltips tooltip-side="top" tooltip-content="' + attr.comment + '"></i>' +
			'</div>' + 
			'</div>';
		},
		replace: true
	};
})
.directive("toolPagePublicationCallout", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			var callout = '<div class="bs-callout-sm bs-callout-primary" style="border-left-color: ' + attr.color + '">';
			callout += '<span ng-show="' + attr.name + '" class="tool-page-callout-header" style="color: black;">{{::' + attr.name + '}}<br>';
			callout += '</span>';
			callout += '<span ng-show="' + attr.pmcid + '"><a href="http://www.ncbi.nlm.nih.gov/pmc/{{::' + attr.pmcid + '}}">PMC › </a>';
			callout += '<span ng-show="' + attr.pmid + ' || ' + attr.doi + ' " style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.pmid + '"><a href="http://www.ncbi.nlm.nih.gov/pubmed/{{::' + attr.pmid + '}}">PUBMED › </a><span class="pull-right">Cited by <a href=" http://europepmc.org/search?query=CITES%3A{{::' + attr.pmid + '}}_MED" class="fa fa-external-link" style="padding-top: 3px; text-color=' + attr.color + ';" aria-hidden="true"></a></span></span>';
			callout += '<span ng-show="(' + attr.pmid + ' || ' + attr.pmcid + ') && ' + attr.doi + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.doi + '"><a href="https://dx.doi.org/{{::' + attr.doi + '}}">DOI › </a></span>';
			callout += '</div>';
			return callout;
		},
		replace: true
	};
})
.directive("toolPageContactCallout", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			var callout = '<div class="bs-callout-sm bs-callout-primary" style="border-left-color: ' + attr.color + ';">';
			callout += '<div ng-show="' + attr.name + '" class="tool-page-callout-header" style="color: black;">{{::' + attr.name + '}}</div>';
			callout += '<div class="tool-page-callout-text">';
			callout += '<span ng-show="' + attr.phone + '">{{::' + attr.phone + '}}';
			callout += '<span ng-show="' + attr.email + ' || ' + attr.url + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.email + '"><i class="fa fa-envelope-o" aria-hidden="true"></i> {{' + attr.email +'.replace(\'@\', \' at \') }}';
			callout += '<span ng-show="' + attr.url + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.url + '"><a href="{{::' + attr.url + '}}">Link › </a></span>';
			callout += '</div>';
			callout += '</div>';
			return callout;
		},
		replace: true
	};
})
.directive("toolPageCreditCallout", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			var callout = '<div class="bs-callout-sm bs-callout-primary" style="border-left-color: ' + attr.color + ';">';
			callout += '<div ng-show="' + attr.name + '" class="tool-page-callout-header" style="color: black;"><a href="" ng-click="creditNameClicked(credit.name)">{{' + attr.name + '}}</a>';
			callout += '<i ng-show="' +  attr.toshow  + '" class="fa fa-question-circle" aria-hidden="true" style="font-size: 100%; margin-left: 0.5em; color: ' + attr.color + ';" tooltips tooltip-side="top" tooltip-content="' + attr.comment + '"></i>';
			callout += '<span ng-show="' + attr.typeentity + ' && ' + attr.typeentity + ' != \'Person\'">';
			callout += '<span ng-show="' + attr.typeentity + '" style="color: #CCCCCC;"> | </span>'; 
			callout += '<span ng-show="' + attr.typeentity + '">{{' + attr.typeentity + '}}</span>';
			callout += '</div>';
			callout += '<div class="tool-page-callout-text">';
			callout += '<span ng-show="' + attr.typerole.count + ' != 0" ng-repeat="role in ' + attr.typerole + '">{{role}}{{$last ? "" : ", "}}';
			callout += '<span ng-show="' + attr.email + ' || ' + attr.url + ' || ' + attr.orcidid + ' || ' + attr.gridid + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.email + '"><i class="fa fa-envelope-o" aria-hidden="true"></i> {{' + attr.email +'.replace(\'@\', \' at \') }}';
			callout += '<span ng-show="' + attr.url + ' || ' + attr.orcidid + ' || ' + attr.gridid + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.url + '"><a href="{{' + attr.url + '}}">Link › </a>';
			callout += '<span ng-show="' + attr.orcidid + ' || ' + attr.gridid + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.orcidid + '">ORCID {{' + attr.orcidid + '}}';
			callout += '<span ng-show="' + attr.gridid + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.gridid + '">GRIDID {{' + attr.gridid + '}}';
			callout += '</div>';
			callout += '</div>';
			return callout;
		},
		replace: true
	};
});