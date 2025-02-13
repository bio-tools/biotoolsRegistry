'use strict';

/* Directives */

angular.module('elixir_front.directives', [])
.directive('toolList', ['ToolList', 'Highlighting', function(ToolList, Highlighting) {
	return {
		restrict: 'A',
		templateUrl: 'partials/directives/toolList.html',
		link: function(scope, element, attrs) {
			// reference the ToolList in the scope
			scope.ToolList = ToolList;
			// reference Highlighting in the scope
			scope.Highlighting = Highlighting;
		}
	}
}])
.directive('showMore',
	[function(){
		return {
			templateUrl: 'showMore.html',
			restrict: 'A',
			transclude: true,
			scope:{
				'showMoreHeight': '@'
			},
			controller: ['$scope', '$element', '$interval', function($scope, $element, $interval) {

				$scope.expanded = false;

				$interval(function(){
					renderStyles();
				}, 300);

				$scope.expandable = false;
				function renderStyles(){
					if($element.height() >= $scope.showMoreHeight && $scope.expanded === false){
						$scope.expandable = true;
					}
				}

				$scope.showLessStyle = {
					'max-height': $scope.showMoreHeight + 'px',
					'overflow': 'hidden'
				};

			}]
		};
	}])
.directive('toolListTable', ['ToolList', 'ToolTableDataSource', 'Highlighting', function(ToolList, ToolTableDataSource, Highlighting) {
	return {
		restrict: 'A',
		templateUrl: 'partials/directives/toolListTable.html',
		link: function(scope, element, attrs) {
			// reference Highlighting in the scope
			scope.Highlighting = Highlighting;
			scope.ToolTableDataSource = ToolTableDataSource;
		}
	}
}])
.directive('toolSorter', ['ToolList', '$state','$stateParams', '$timeout', 'ToolSorter', 'Query', '$rootScope', function(ToolList, $state, $stateParams, $timeout, ToolSorter, Query, $rootScope) {
	return {
		restrict: 'A',
		templateUrl: 'partials/directives/sorter.html',
		link: function(scope, element, attrs) {
			// reference the ToolPaginator in the scope
			scope.ToolSorter = ToolSorter;

			// put sorting attributes in the url
			scope.addToURL = function() {
				var params = $stateParams;
				// set the sorting url parameters
				if (ToolSorter.sortBy.attrName == 'lastUpdate' && ToolSorter.order == true) {
					// set defaults as null
					params['sort'] = null;
					params['ord'] = null;
				} else {
					params['sort'] = ToolSorter.sortBy.attrName;
					params['ord'] = ToolSorter.order ? 'desc' : 'asc';
				}
				$state.transitionTo('search', params, { notify: false });
			}

			// ran on changing the dropdown value
			scope.sortingChangedByDropdown = function() {
				scope.addToURL();
				$timeout( function() {
					ToolList.refresh();
				});
			}

			scope.validateSelectedSortOption = function() {
  				if (Query.current.length > 0) {
					ToolSorter.addScore();
				} else {
					ToolSorter.removeScore();
				}
				ToolSorter.setSortOption($stateParams['sort']);
  			}

			// read current sorting attribute from url
			if ($stateParams['sort'] != null) {
				if ($stateParams['sort'] == 'score') {
					ToolSorter.addScore();
				}
				ToolSorter.sortBy = ToolSorter.list[_.findIndex(ToolSorter.list, {"attrName": $stateParams['sort']}) || 0];
			}
			// read current sorting order from url
			if ($stateParams['ord'] != null) {
				if ($stateParams['ord'] == 'desc') {
					ToolSorter.order = true;
				} else if($stateParams['ord'] == 'asc'){
					ToolSorter.order = false;
				}
			}

			$rootScope.$on('$stateChangeSuccess', function(event, toState, toStateParams, fromState, fromStateParams) {
				scope.validateSelectedSortOption();
			});

			$rootScope.$on('search-bar-tags-changed', function handler() {
    			scope.validateSelectedSortOption();
  			});


		}
	}
}])
.directive('displayModeSelector', ['ToolList', '$state','$stateParams', '$timeout', 'DisplayModeSelector', function(ToolList, $state, $stateParams, $timeout, DisplayModeSelector) {
	return {
		restrict: 'A',
		templateUrl: 'partials/directives/displaySelector.html',
		link: function(scope, element, attrs) {
			scope.DisplayModeSelector = DisplayModeSelector;

			// put sorting attributes in the url
			scope.modeChanged = function() {
				$timeout( function() {
					ToolList.refresh();
				});
			}
		}
	}
}])
.directive('toolPaginator', ['ToolList', '$state','$stateParams', 'Query', '$timeout', 'ToolPaginator', function(ToolList, $state, $stateParams, Query, $timeout, ToolPaginator) {
	return {
		restrict: 'A',
		template: '<div style="display: flex; align-items: center; margin-top: 25px; margin-bottom: 25px;"><ul uib-pagination total-items="ToolList.count" ng-model="ToolPaginator.currentPage" items-per-page="ToolPaginator.pageSize" max-size="ToolPaginator.maxSize" ng-change="pageChanged()" class="pagination-sm pagination-top" boundary-links="true" rotate="true" ng-disabled="ToolList.loading"></ul><div style="margin-left: 15px; display: flex; align-items: center;"><label for="pageInput" style="margin-right: 5px;">Go to page:</label><input type="number" id="pageInput" ng-model="inputPage" min="1" max="{{Math.ceil(ToolList.count / ToolPaginator.pageSize)}}" ng-keypress="handlePageInput($event)" style="width: 60px;" /></div></div>',
		link: function(scope, element, attrs) {
			// reference the Query in the scope
			scope.Query = Query;
			// reference the ToolPaginator in the scope
			scope.ToolPaginator = ToolPaginator;

			// read current page from url
			if ($stateParams['page'] != null) {
				ToolPaginator.currentPage = parseInt($stateParams['page']);
			} else {
				ToolPaginator.currentPage = 1;
			}

			// when page changes, store the new page in the url and refresh the list of tools
			scope.pageChanged = function() {
				var params = $stateParams;
				$timeout( function() {
					// set the 'page' URL parameter according to currentPage
					params['page'] = ToolPaginator.currentPage != 1 ? ToolPaginator.currentPage : null;
					$state.transitionTo('search', params, { notify: false });
					ToolList.refresh();
				});
			}

			// Allow direct page navigation via input
            scope.handlePageInput = function(event) {
                if (event.key === 'Enter') { // Navigate on pressing Enter
                    if (
                        scope.inputPage >= 1 &&
                        scope.inputPage <= Math.ceil(ToolList.count / ToolPaginator.pageSize)
                    ) {
                        ToolPaginator.currentPage = scope.inputPage;
                        scope.pageChanged();
                    } else {
                        alert('Invalid page number.');
                    }
                }
            };

			// riddiculous hax, otherwise it keeps changing to 1
			var initializing = true;
			scope.$watch('ToolPaginator.currentPage', function(newVal, oldVal) {
				if (initializing) {
					if (newVal != oldVal && newVal == 1) {ToolPaginator.currentPage = oldVal};
					$timeout(function() { initializing = false; });
				}
			});

			// reset page to 1 when query changes
			scope.$watch('Query.current', function() {
				ToolPaginator.currentPage = 1;
			}, true);

		}
	}
}])

// inserts a link to a publication resolving page, depending on the type of publication
.directive("insertPublicationLink", function($compile){
	return {
		restrict: 'A',
		scope: {
			publication: '='
		},
		compile: function CompilingFunction($templateElement, $templateAttributes) {
			return function LinkingFunction($scope, $element, $attrs) {
				var html = '';
				// PUBMED
				if (/^\d{7,8}$/.test($scope.publication)) {
					html = '<span>PUBMED:</span> <a href="http://www.ncbi.nlm.nih.gov/pubmed/' + $scope.publication + '">' + $scope.publication + '</a>';
				// PMC
			} else if (/^PMC\d{6,8}$/.test($scope.publication)) {
				html = '<span>PMC:</span> <a href="http://www.ncbi.nlm.nih.gov/pmc/' + $scope.publication + '">' + $scope.publication + '</a>';
				// DOI
			} else if (/^(doi:)?\d{2}.\d{4}/.test($scope.publication)) {
				var publication = $scope.publication.replace('doi:','');
				html = '<span>DOI:</span> <a href="https://dx.doi.org/' + publication + '">' + publication + '</a>';
			}
			var e = $compile(html)($scope);
			$element.replaceWith(e);
		};
	}
}
})
// inserts a link to a publication resolving page, depending on the type of publication
.directive("insertPublicationLinkIcon", function($compile){
	return {
		restrict: 'A',
		scope: {
			publication: '='
		},
		compile: function CompilingFunction($templateElement, $templateAttributes) {
			return function LinkingFunction($scope, $element, $attrs) {
				var html = '';
				// PUBMED
				if (/^\d{7,8}$/.test($scope.publication)) {
					html = '<a href="http://www.ncbi.nlm.nih.gov/pubmed/' + $scope.publication + '"><i class="fa fa-external-link" aria-hidden="true" uib-tooltip="PUBMED" tooltip-append-to-body="true"></i></a>';
				// PMC
			} else if (/^PMC\d{6,8}$/.test($scope.publication)) {
				html = '<a href="http://www.ncbi.nlm.nih.gov/pmc/' + $scope.publication + '"><i class="fa fa-external-link" aria-hidden="true" uib-tooltip="PMC" tooltip-append-to-body="true"></i></a>';
				// DOI
			} else if (/^(doi:)?\d{2}.\d{4}/.test($scope.publication)) {
				var publication = $scope.publication.replace('doi:','');
				html = '<a href="https://dx.doi.org/' + publication + '"><i class="fa fa-external-link" aria-hidden="true" uib-tooltip="DOI" tooltip-append-to-body="true"></i></a>';
			}
			var e = $compile(html)($scope);
			$element.replaceWith(e);
		};
	}
}
})
// makes this element focused
.directive('focus', function () {
	return {
		restrict: 'A',
		link: function(scope, iElm, iAttrs, controller) {
			iElm[0].focus();
		}
	}
})
// creates an animated spinner
.directive('spinner', function() {
	return {
		restrict: 'A',
		replace: 'true',
		template: '<div class="adjust"><div class="spinner"></div></div>'

	}
})
// creates a resource not found message
.directive('resourceNotFoundDialog', function() {
	return {
		restrict: 'A',
		replace: 'true',
		template: '<div class="col-md-12 info-dialog-background info-dialog info-dialog-text">We\'re sorry but we couldn\'t find what you were looking for. You can try searching for the resource you need <a ui-sref="search()">here</a>.</div>'
	}
})
// creates an error message
.directive('errorDialog', function() {
	return {
		restrict: 'A',
		replace: true,
		template: function(elem, attr){
			return '<div class="col-md-offset-2 col-md-8 bs-callout bs-callout-danger" style="margin-top: 80px;"><h4><i class="fa fa-exclamation-circle" aria-hidden="true"></i> Error {{' + attr.errorcode + '}}</h4>{{' + attr.errormessage + '}}</div>'
		},
		transclude: true
	}
})
// make this element ignore pressing the 'Enter' key
.directive('ignoreEnter', function() {
	return function (scope, element, attrs) {
		element.bind("keydown keypress", function (event) {
			if (event.which === 13) {
				event.preventDefault();
			}
		});
	}
})
.directive('validateEditResourceField', function () {
	return {
		restrict: 'A',
		require: ['^form','ngModel'],
		link: function (scope, element, attrs, ctrls) {
			var ngForm = ctrls[0];
			var ngModel = ctrls[1];
			// Initialization - create the data path based on ng-model path.
			var dataPath = attrs.ngModel.replace("software.", "").replace("$parent.$index", attrs.parentIndex).replace("$index", attrs.index).replace("[", ".").replace("]", "").split(".");
			// Remove errors once values have been edited.
			ngModel.$parsers.push(function(value) {
				_.set(scope.registrationErrorPayload, dataPath, null);
				ngModel.errorMessages = [];
				ngModel.$setValidity('server_validation_passed', true);
				return value;
			});
			ngModel.$viewChangeListeners.push(function() {
				// Prevent non-mandatory fields from becoming mandatory,
				// by assigning empty strings to the keys in the object to be
				// sent to the server.
				var value = _.get(scope.software, dataPath);
				if (value === "") {
					_.unset(scope.software, dataPath);
				}
			});
			// Observe for changes in the server-side validation
			// of a resource appeared - i.e. user pressed validate in resource edit
			scope.$watch('registrationErrorPayload', function(date) {
				// Find the error and set the input validity based on the results.
				var error = _.result(scope.registrationErrorPayload, dataPath);
				if (_.isEmpty(error) == false) {
					// Error exist - server validation failed.
					ngModel.$setValidity('server_validation_passed', false);
					ngModel.errorMessages = error;
				}
				else {
					// Error does not exist - server validation passed.
					ngModel.$setValidity('server_validation_passed', true);
					ngModel.errorMessages = [];
				}
				// Find the error and set the form validity based on the results.
				var formError = extractFormErrors();
				// There are errors in the form.
				if (formError.length > 0) {
					ngForm.$setValidity('server_validation_passed', false);
					ngForm.errorMessages = _.union(ngForm.errorMessages, formError);
				}
				else {
					ngForm.$setValidity('server_validation_passed', true);
					ngForm.errorMessages = [];
				}
			});
			var extractFormErrors = function() {
				var formErrors = [];
				for (var i = 1; i < dataPath.length; i++) {
					var subDataPath = dataPath.slice(0,i);
					subDataPath.push("general_errors");
					var error = _.result(scope.registrationErrorPayload, subDataPath);
					if (_.isEmpty(error) == false) {
						formErrors = formErrors.concat(error);
					}
				}
				return formErrors;
			}
		}
	}
})
.directive("dividerLabel", function(){
	return {
		restrict: 'A',
		transclude: true,
		template: function(elem, attr){
			var callout = 'class="tool-page-diver-label"';
			return callout;
		},
		replace: true
	};
})
// creates an animated small spinner
.directive('smallSpinner', function() {
	return {
		restrict: 'A',
		replace: 'true',
		template: '<div style="text-align:center; color: #7f7f7f; font-size: 12px;"><i class="fa fa-circle-o-notch fa-spin"></i> Processing...</div>'
	}
})
.directive('largeSpinner', function() {
	return {
		restrict: 'A',
		replace: 'true',
		template: '<div style="text-align:center; color: #cccccc; font-size: 60px;"><i class="fa fa-circle-o-notch fa-spin"></i></div>'
	}
});



