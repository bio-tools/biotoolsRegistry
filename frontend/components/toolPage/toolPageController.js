angular.module('elixir_front')
.controller('ToolPageController', ['$scope', '$state', '$timeout', '$stateParams', 'Tool', 'User', 'CheckUserEditingRights', 'ResourceRequestProvider', 'ngMeta', 'Query', function($scope, $state, $timeout, $stateParams, Tool, User, CheckUserEditingRights, ResourceRequestProvider, ngMeta, Query) {
	$scope.notFound = false;
	$scope.versions = [];
	$scope.CheckUserEditingRights = CheckUserEditingRights;
	$scope.editingRequestedSuccess = null; 

	$scope.User = User;

	function quoteQueryStringValue(v){
		return '"' + v + '"'
	}

	function stripEdam(t){
		return t.replace("http://edamontology.org/", "");
	}
	// go to 404 in special case when URL is /tool/
	if ($stateParams.id.length == 0) {
		$state.go('404');
	}
	
	$scope.topicNameClicked = function(topic) {
		$state.go('search', {'topicID': quoteQueryStringValue(stripEdam(topic.uri))});
	}

	$scope.functionNameClicked = function(functionName) {
		$state.go('search', {'operationID': quoteQueryStringValue(stripEdam(functionName.uri))});
	}

	$scope.inputNameClicked = function(inputName) {
		//$state.go('search', {'inputDataType': inputName.data.term});
		$state.go('search', {'inputDataTypeID': quoteQueryStringValue(stripEdam(inputName.data.uri)) });
	}

	$scope.inputFormatNameClicked = function(formatName) {
		//$state.go('search', {'inputDataFormat': formatName.term});
		$state.go('search', {'inputDataFormatID': quoteQueryStringValue(stripEdam(formatName.uri)) });
	}

	$scope.outputFormatNameClicked = function(formatName) {
		$state.go('search', {'outputDataFormatID': quoteQueryStringValue(stripEdam(formatName.uri))});
	}

	$scope.outputNameClicked = function(outputName) {
		$state.go('search', {'outputDataTypeID': quoteQueryStringValue(stripEdam(outputName.data.uri))});
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

	var initDimensionsAI = function() {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = "https://badge.dimensions.ai/badge.js";
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
		//initDimensionsAI();
		//window.__dimensions_embed.addBadges();
		//window.__dimensions_embed.addBadges();
		cleanNulls($scope.software);
		$scope.setMetadataForSoftware($scope.software);
		//$timeout(function(){ window.OpEB_widgets.OpEB.apply(); }, 100);*/

		$timeout(function(){ window.__dimensions_embed.addBadges(); }, 100);
		/*$timeout(function(){ window.OpEB_widgets.OpEB.apply(); }, 100);*/
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
		transclude: true,
		templateUrl: 'components/toolPage/partials/publicationDetailCallout.html',
		controller: ['$scope', function($scope) {
			$scope.status = "... More";
			$scope.expandable_status = "expandable-summary";

			var initDimensionsAI = function() {
				var script = document.createElement('script');
				script.type = 'text/javascript';
				script.src = "https://badge.dimensions.ai/badge.js";
				document.body.appendChild(script);
			}

			//initDimensionsAI();
			$scope.toggleStatus = function(){
				if ($scope.status == "... More"){
					$scope.status = "Less";
					$scope.expandable_status = "";
				}else{
					$scope.status = "... More";
					$scope.expandable_status = "expandable-summary";
				}
			}

			$scope.getDoi = function(){
				return $scope.publication.doi;
			}
		}],
		link: function($scope, element, attrs) {
				
				//window.__dimensions_embed.addBadges();

		}
	};
})
.directive("toolPageLinkCallout", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			return '<div class="bs-callout-sm bs-callout-primary" style="border-left-color: ' + attr.color + ';">' +
			'<div class="tool-page-callout-header" style="color: black;">' + 
			'<a target="_blank" href="' + attr.url + '" tooltips tooltip-side="top" tooltip-content="' + attr.url + '">' + attr.name + ' › </a>' +
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
		scope:{
				'pmcid': '=?',
				'doi':'=?',
				'pmid':'=?',
				'name':'=?',
				'color':'@?'
		},
		templateUrl: 'components/toolPage/partials/toolPagePublicationCalloutHTML.html',
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
			callout += '<span ng-show="' + attr.url + '"><a href="{{' + attr.url + '}}" target="_blank">Link › </a>';
			callout += '<span ng-show="' + attr.orcidid + ' || ' + attr.gridid + '" style="color: #CCCCCC;"> | </span></span>';
			callout += '<span ng-show="' + attr.orcidid + '"><a href="{{' + attr.orcidid + '}}" target="_blank">ORCID ›</a></span>';
			callout += '</div>';
			callout += '</div>';
			return callout;
		},
		replace: true
	};
});