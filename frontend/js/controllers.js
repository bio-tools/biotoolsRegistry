'use strict';

/* Controllers */

angular
    .module('elixir_front.controllers', [])
    .controller('ToolGridController', [
        '$scope',
        '$timeout',
        'ToolList',
        'ToolTableDataSource',
        function ($scope, $timeout, ToolList, ToolTableDataSource) {
            $scope.ToolList = ToolList;
            $scope.savedStateExists = function () {
                return localStorage.getItem('gridState') ? true : false;
            };
            $scope.saveState = function () {
                var state = $scope.gridApi.saveState.save();
                localStorage.setItem('gridState', JSON.stringify(state));
            };
            $scope.restoreState = function () {
                $timeout(function () {
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
                columnDefs: ToolTableDataSource.columnsDescription(
                    $scope.savedStateExists() == true
                        ? []
                        : [
                              'Name',
                              'Description',
                              'Homepage',
                              'Credits',
                              'Operation',
                              'Topic',
                              'Input',
                              'Output',
                          ]
                ),
                rowHeight: 135,
                enableGridMenu: true,
                onRegisterApi: function (gridApi) {
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
                },
            };
            $scope.tableHeight = function () {
                return {
                    height:
                        Math.min($scope.ToolList.count, 4) * $scope.gridOptions.rowHeight +
                        33 +
                        'px',
                };
            };
        },
    ])
    .controller('ToolGridCellController', [
        '$scope',
        function ($scope) {
            $scope.init = function (columnName, rowIndex) {
                $scope.columnName = columnName;
                $scope.rowIndex = rowIndex;
            };
            $scope.RowIdentifier = function () {
                return $scope.columnName + $scope.rowIndex;
            };
            $scope.RowName = function () {
                return $scope.columnName;
            };
            $scope.RowHeight = function () {
                var element = document.getElementById($scope.RowIdentifier());
                return element ? element.offsetHeight : 0;
            };
            $scope.DefaultRowHeight = function () {
                return 135;
            };
            $scope.CellWidth = function () {
                return document.getElementById($scope.RowIdentifier()).offsetWidth;
            };
            $scope.CellStyle = function () {
                return {
                    width: CellWidthDescription(),
                    'background-color': CellColorDescription(),
                };
            };
            function CellWidthDescription() {
                return $scope.CellWidth() + 2 + 'px';
            }
            function CellColorDescription() {
                return $scope.rowIndex % 2 != 0 ? '#f8f8f8' : 'white';
            }
        },
    ])
    .controller('SearchResultController', [
        '$scope',
        '$state',
        'ToolList',
        'ToolTableDataSource',
        'DisplayModeSelector',
        'Domain',
        function ($scope, $state, ToolList, ToolTableDataSource, DisplayModeSelector, Domain) {
            function quoteQueryStringValue(v) {
                return '"' + v + '"';
            }

            function stripEdam(t) {
                return t.replace('http://edamontology.org/', '');
            }

            $scope.topicNameClicked = function (topic) {
                //$state.go('search', {'topic': topic.term}, {reload: true});
                $state.transitionTo(
                    'search',
                    { topicID: quoteQueryStringValue(stripEdam(topic.uri)) },
                    {
                        reload: true,
                        inherit: false,
                        notify: true,
                    }
                );
            };

            $scope.operationNameClicked = function (operation) {
                //$state.go('search', {'topic': topic.term}, {reload: true});
                $state.transitionTo(
                    'search',
                    { operationID: quoteQueryStringValue(stripEdam(operation.uri)) },
                    {
                        reload: true,
                        inherit: false,
                        notify: true,
                    }
                );
            };
            $scope.collectionNameClicked = function (collection) {
                //$state.go('search', {'topic': topic.term}, {reload: true});
                $state.transitionTo(
                    'search',
                    { collectionID: quoteQueryStringValue(collection) },
                    {
                        reload: true,
                        inherit: false,
                        notify: true,
                    }
                );
            };

            $scope.shouldLicenseBeALink = function (license) {
                return !_.includes(['Freeware', 'Proprietary', 'Other', 'Not licensed'], license);
            };

            $scope.getFlatOperations = function (functions) {
                var operations = {};
                for (var i = 0; i < functions.length; i++) {
                    for (var j = 0; j < functions[i].operation.length; j++) {
                        var o = functions[i].operation[j];
                        operations[o.term] = o;
                    }
                }

                var arr = Object.keys(operations);
                var r = [];
                for (var i = 0; i < arr.length; i++) {
                    r.push(operations[arr[i]]);
                }

                return r;
            };

            $scope.Domain = Domain;
            $scope.ToolTableDataSource = ToolTableDataSource;
            $scope.ToolList = ToolList;
            $scope.DisplayModeSelector = DisplayModeSelector;
            // Get data initially
            ToolList.refresh();
        },
    ])
    .controller('AlertsController', [
        '$scope',
        'Alert',
        'EnvironmentChecker',
        function ($scope, Alert, EnvironmentChecker) {
            $scope.Alert = Alert;
            $scope.dev_alert = false;

            // check if the current setup id dev or prod.
            EnvironmentChecker.getEnvironment().then(function (data) {
                if (data == 'Development') {
                    $scope.dev_alert = true;
                }
            });

            // check if welcome message was disabled for this user
            if ('welcome_message' in localStorage) {
                $scope.welcome_message = localStorage.welcome_message === 'true';
            } else {
                $scope.welcome_message = true;
            }

            $scope.closeWelcomeMessageButtonClick = function () {
                $scope.welcome_message = false;
                localStorage.welcome_message = false;
            };
        },
    ])
    .controller('ToolEditController', [
        '$scope',
        '$controller',
        '$state',
        '$stateParams',
        'Ontology',
        'Attribute',
        'CheckUserEditingRights',
        'User',
        '$timeout',
        'UsedTerms',
        '$q',
        '$uibModal',
        function (
            $scope,
            $controller,
            $state,
            $stateParams,
            Ontology,
            Attribute,
            CheckUserEditingRights,
            User,
            $timeout,
            UsedTerms,
            $q,
            $uibModal
        ) {
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

            // Populate from external URL or query param on load
            $timeout(function () {
                // Populate from external URL or query param ---
                //  - ?json_url=https://example.com/tool.json
                //  - ?json=<urlencoded JSON or base64-encoded JSON>
                var search = $location.search();
                if (search.json_url) {
                    $http.get(search.json_url).then(
                        function (resp) {
                            if (resp.data) {
                                // ensure digest cycle completes
                                $timeout(function () {
                                    $scope.software = resp.data;
                                }, 0);
                            }
                        },
                        function (err) {
                            // ignore
                        }
                    );
                } else if (search.json) {
                    var raw = search.json;
                    try {
                        // try decodeURIComponent first
                        var decoded = decodeURIComponent(raw);
                        var parsed = JSON.parse(decoded);

                        $timeout(function () {
                            $scope.software = parsed;
                        }, 0);
                    } catch (e1) {
                        try {
                            // fallback: base64
                            var decodedB64 = atob(raw);
                            var parsed = JSON.parse(decodedB64);

                            $timeout(function () {
                                $scope.software = parsed;
                            }, 0);
                        } catch (e2) {
                            // ignore
                        }
                    }
                }
            }, 100);

            // for storing validation and saving progess
            ($scope.validationProgress = {}),
                ($scope.savingProgress = {}),
                ($scope.deletingProgress = {});

            $scope.initializePermissions = function () {
                $scope.canEditTool = false;
                $scope.canEditToolPermissions = false;
                // Owner can edit anything.
                if (!_.isEmpty($scope.software)) {
                    if ($scope.software.owner == $scope.User.getUsername()) {
                        $scope.canEditTool = true;
                        $scope.canEditToolPermissions = true;
                    } else if ($scope.software.editPermission != undefined) {
                        $scope.canEditTool = $scope.CheckUserEditingRights.canEdit($scope.software);
                        $scope.canEditToolPermissions = false;
                        delete $scope.software.editPermission;
                    }
                }
            };

            // handle sending the resource to either validation or saving endpoints
            $scope.sendResource = function (service, progress, isRemoval, action) {
                progress.success = false;
                progress.error = false;
                progress.inProgress = true;
                $scope.registrationErrorPayload = null;

                service(
                    $stateParams,
                    $scope.software,
                    function (response) {
                        // handle success
                        progress.inProgress = false;
                        progress.success = true;
                        if (isRemoval) {
                            alert('Resource removed succesfully.');
                            $state.go('search');
                        }

                        if (action == 'create') {
                            $state.go('tool.edit', { id: response.biotoolsID });
                        }
                    },
                    function (response) {
                        // handle error
                        progress.error = true;
                        progress.inProgress = false;
                        $scope.registrationErrorPayload = response.data;
                    }
                );
            };

            // modals
            $scope.openModal = function (edam, type, suggestions) {
                var ontoMap = {
                    data: $scope.EDAM_data,
                    format: $scope.EDAM_format,
                    operation: $scope.EDAM_operation,
                };
                var onto = ontoMap[type] || $scope.EDAM_data;

                var modalInstance = $uibModal.open({
                    templateUrl: 'partials/tool_edit/toolEditEdamModal.html',
                    controllerAs: 'vm',
                    controller: [
                        '$uibModalInstance',
                        'edam',
                        'onto',
                        'type',
                        'suggestions',
                        EdamModalCtrl,
                    ],
                    resolve: {
                        edam: function () {
                            return edam;
                        },
                        onto: function () {
                            return onto;
                        },
                        type: function () {
                            return type;
                        },
                        suggestions: function () {
                            return suggestions;
                        },
                    },
                });

                modalInstance.result.then(
                    function (updatedEdam) {
                        angular.copy(updatedEdam, edam);
                    },
                    function () {}
                );

                return modalInstance.result;
            };

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
                    return (
                        typeof word === 'string' && word.indexOf('http://edamontology.org/') !== -1
                    );
                });

                if (type === 'operation') return null; // No recommendations for operations

                var ontoMap = {
                    format: $scope.EDAM_data,
                    input: $scope.EDAM_operation,
                    output: $scope.EDAM_operation,
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
                    format: $scope.EDAM_format,
                    output: $scope.EDAM_data,
                    input: $scope.EDAM_data,
                };
                var onto = ontoMap[type];

                return suggestions.map(function (element) {
                    var edamObj = $scope.findObjectByUri(onto, element);
                    return {
                        uri: element,
                        term: edamObj ? edamObj.text : '',
                    };
                });
            }

            $scope.addWithModal = function (type, edam) {
                var pickerTypeMap = {
                    input: 'data',
                    output: 'data',
                    format: 'format',
                    function: 'operation',
                    operation: 'operation',
                };
                var pickertype = pickerTypeMap[type] || '';

                var suggestions = $scope.recommend_terms(edam, type);

                var modalPromise = $scope.openModal({}, pickertype, suggestions);

                modalPromise.then(
                    function (newEdam) {
                        handleModalResult(type, edam, newEdam);
                    },
                    function () {}
                );
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
            $scope.$watch(
                'software',
                function (newVal, oldVal) {
                    if (newVal !== oldVal) {
                        $scope.savingProgress.success = false;
                        $scope.validationProgress.success = false;
                    }
                },
                true
            );

            // used terms (biotoolsID) for searching in relations
            function getBiotoolsIDs() {
                var d = $q.defer();
                var params = {
                    usedTermName: 'biotoolsID',
                };
                UsedTerms.get(params, function (response) {
                    d.resolve(response.data);
                });
                return d.promise;
            }

            $scope.loadBiotoolsIDs = function (query) {
                return getBiotoolsIDs().then(function (list) {
                    return list
                        .filter(function (str) {
                            return str.toLowerCase().includes(query.toLowerCase());
                        })
                        .slice(0, 50)
                        .sort();
                });
            };

            // used terms (collectionID) for searching in collections
            function getCollectionIDs() {
                var d = $q.defer();
                var params = {
                    usedTermName: 'collectionID',
                };
                UsedTerms.get(params, function (response) {
                    d.resolve(response.data);
                });
                return d.promise;
            }

            $scope.loadCollectionIDs = function (query) {
                return getCollectionIDs().then(function (list) {
                    return list
                        .filter(function (str) {
                            return str.toLowerCase().includes(query.toLowerCase());
                        })
                        .slice(0, 10)
                        .sort();
                });
            };

            // used terms (credit names) for searching in credits
            function getCreditNames() {
                var d = $q.defer();
                var params = {
                    usedTermName: 'credit',
                };
                UsedTerms.get(params, function (response) {
                    d.resolve(response.data);
                });
                return d.promise;
            }

            $scope.loadCreditNames = function (query) {
                return getCreditNames().then(function (list) {
                    return list
                        .filter(function (str) {
                            return str.toLowerCase().includes(query.toLowerCase());
                        })
                        .slice(0, 10)
                        .sort();
                });
            };

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
            };

            $scope.addObjectClick = function (_what, _parent, _where) {
                _parent[_where] = {};
                _parent[_where][_what] = {};
            };

            $scope.removeObjectClick = function (_what, _parent, _where) {
                var message = _parent[_what][_index].term
                    ? `Are you sure you want to remove ${_parent[_what][_index].term}?`
                    : 'Are you sure you want to remove this element?';

                if (confirm(message)) {
                    if (_parent[_where][_what]) {
                        delete _parent[_where][_what];
                    }
                    if (Object.keys(_parent[_where]).length === 0) {
                        delete _parent[_where];
                    }
                }
            };

            // remove attribute or list entry
            $scope.removeButtonClick = function (_what, _parent, _index, _event) {
                var message = _parent[_what][_index].term
                    ? `Are you sure you want to remove ${_parent[_what][_index].term}?`
                    : 'Are you sure you want to remove this element?';

                if (_parent[_what][_index] ? confirm(message) : true) {
                    // remove jstree if exists
                    if (_event) {
                        $(_event.target).closest('div').find('.jstree').jstree('destroy').remove();
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

            $scope.moveItem = function (key, index, direction) {
                var array = $scope.software[key];
                var newIndex = index + direction;
                if (newIndex < 0 || newIndex >= array.length) return;
                // Swap the elements
                var temp = array[newIndex];
                array[newIndex] = array[index];
                array[index] = temp;
            };

            // create connections between entries
            $scope.errorConnections = {
                name: ['id'],
            };

            // reset error on change
            $scope.resetError = function (_what, _parent, _index) {
                // select appropriate error type handling
                if (_index != undefined && _index >= 0) {
                    $scope.resetListError(_what, _parent, _index);
                } else {
                    // remove all connected error warnings
                    var whatConnections = $scope.errorConnections[_what];
                    if (whatConnections) {
                        whatConnections.forEach(function (connection) {
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
            };

            $scope.resetListError = function (_what, _parent, _index) {
                if (_parent[_what] && _parent[_what][_index]) {
                    _parent[_what][_index] = {};
                }
            };

            $scope.isString = function (value) {
                if (typeof value === 'string') {
                    return true;
                } else {
                    return false;
                }
            };

            // get ontology objects for the various widgets
            Ontology.get({ name: 'EDAM_topic' }, function (response) {
                $scope.EDAM_topic = response.data.children;
            });
            Ontology.get({ name: 'EDAM_data' }, function (response) {
                $scope.EDAM_data = response.data.children;
            });
            Ontology.get({ name: 'EDAM_format' }, function (response) {
                $scope.EDAM_format = response.data.children;
            });
            Ontology.get({ name: 'EDAM_operation' }, function (response) {
                $scope.EDAM_operation = response.data.children;
            });

            // populate the JSON edit textarea
            $scope.$watch(
                'software',
                function (newVal, oldVal) {
                    $scope.jsonEdit.model = angular.toJson($scope.software, 2);
                    // Check permissions
                    if ($scope.canEditTool == false) {
                        $scope.initializePermissions();
                    }
                },
                true
            );

            // parse the edited JSON for errors
            $scope.jsonEdit = {};
            var initializing = true;
            $scope.$watch('jsonEdit.model', function (newVal, oldVal) {
                if (!initializing) {
                    try {
                        $scope.software = angular.fromJson($scope.jsonEdit.model);
                        $scope.jsonEdit.error = null;
                    } catch (exp) {
                        $scope.jsonEdit.error = exp.message;
                    }
                } else {
                    initializing = false;
                }
            });

            // download JSON from the editor
            $scope.downloadTool = function (_pretty) {
                var hiddenElement = document.createElement('a');
                if (_pretty) {
                    hiddenElement.href =
                        'data:attachment/json,' + encodeURI(angular.toJson($scope.software, 2));
                } else {
                    hiddenElement.href =
                        'data:attachment/json,' + encodeURI(angular.toJson($scope.software));
                }
                hiddenElement.target = '_blank';
                hiddenElement.download =
                    ($scope.software.name ? $scope.software.name : 'resource') + '.json';
                document.body.appendChild(hiddenElement);
                hiddenElement.click();
            };

            // settings for the EDAM tree widget
            $scope.treeOptions = {
                nodeChildren: 'children',
                dirSelectable: true,
            };

            // set term and uri when picked from EDAM widget
            $scope.ontologyOnSelect = function (_object, _index, _node) {
                // if _object[_index] is not an object, make it one
                if (!(_object[_index] === Object(_object[_index]))) {
                    _object[_index] = {};
                }
                _object[_index].term = _node.text;
                _object[_index].uri = _node.data.uri;
            };

            // fetch data from Europe PMC and update the publication object
            function fetchEuropePMCData(pub, id_type, identifier) {
                var params = [];

                if (id_type == 'doi') params.push('query=DOI:' + identifier);
                else if (id_type == 'pmid') params.push('query=EXT_ID:' + identifier);
                else if (id_type == 'pmcid') params.push('query=PMC:' + identifier);
                else return;

                var url =
                    'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' +
                    params.join('&') +
                    '&format=json';
                fetch(url)
                    .then(function (response) {
                        return response.json();
                    })
                    .then(function (data) {
                        console.log('Europe PMC data fetched:', data);
                        if (
                            data.resultList &&
                            data.resultList.result &&
                            data.resultList.result.length > 0
                        ) {
                            var rec = data.resultList.result[0];
                            console.log('Europe PMC record:', rec);
                            if (rec.doi) pub.doi = rec.doi;
                            if (rec.pmid) pub.pmid = rec.pmid;
                            if (rec.pmcid) pub.pmcid = rec.pmcid;
                            console.log('Updated publication:', pub);
                            $scope.$apply();
                        }
                    })
                    .catch(function (err) {
                        /*  handle error */
                    });
            }

            $scope.onPublicationIdChange = function (idType, value, index) {
                if (value && value.trim() !== '') {
                    console.log('Publication ID changed:', idType, value, 'at index:', index);
                    fetchEuropePMCData($scope.software.publication[index], idType, value.trim());
                }
            };

            $scope.latestOptions = [
                { value: 1, text: 'Yes' },
                { value: 0, text: 'No' },
            ];

            $scope.contactRoleOptions = [
                { value: 'General', text: 'General' },
                { value: 'Developer', text: 'Developer' },
                { value: 'Technical', text: 'Technical' },
                { value: 'Scientific', text: 'Scientific' },
                { value: 'Helpdesk', text: 'Helpdesk' },
                { value: 'Maintainer', text: 'Maintainer' },
            ];

            $scope.licenseOptions = (function () {
                var new_licenses = [
                    '0BSD',
                    'AAL',
                    'ADSL',
                    'AFL-1.1',
                    'AFL-1.2',
                    'AFL-2.0',
                    'AFL-2.1',
                    'AFL-3.0',
                    'AGPL-1.0',
                    'AGPL-3.0',
                    'AMDPLPA',
                    'AML',
                    'AMPAS',
                    'ANTLR-PD',
                    'APAFML',
                    'APL-1.0',
                    'APSL-1.0',
                    'APSL-1.1',
                    'APSL-1.2',
                    'APSL-2.0',
                    'Abstyles',
                    'Adobe-2006',
                    'Adobe-Glyph',
                    'Afmparse',
                    'Aladdin',
                    'Apache-1.0',
                    'Apache-1.1',
                    'Apache-2.0',
                    'Artistic-1.0',
                    'Artistic-1.0-Perl',
                    'Artistic-1.0-cl8',
                    'Artistic-2.0',
                    'BSD-2-Clause',
                    'BSD-2-Clause-FreeBSD',
                    'BSD-2-Clause-NetBSD',
                    'BSD-3-Clause',
                    'BSD-3-Clause-Attribution',
                    'BSD-3-Clause-Clear',
                    'BSD-3-Clause-LBNL',
                    'BSD-3-Clause-No-Nuclear-License',
                    'BSD-3-Clause-No-Nuclear-License-2014',
                    'BSD-3-Clause-No-Nuclear-Warranty',
                    'BSD-4-Clause',
                    'BSD-4-Clause-UC',
                    'BSD-Protection',
                    'BSD-Source-Code',
                    'BSL-1.0',
                    'Bahyph',
                    'Barr',
                    'Beerware',
                    'BitTorrent-1.0',
                    'BitTorrent-1.1',
                    'Borceux',
                    'CATOSL-1.1',
                    'CC-BY-1.0',
                    'CC-BY-2.0',
                    'CC-BY-2.5',
                    'CC-BY-3.0',
                    'CC-BY-4.0',
                    'CC-BY-NC-1.0',
                    'CC-BY-NC-2.0',
                    'CC-BY-NC-2.5',
                    'CC-BY-NC-3.0',
                    'CC-BY-NC-4.0',
                    'CC-BY-NC-ND-1.0',
                    'CC-BY-NC-ND-2.0',
                    'CC-BY-NC-ND-2.5',
                    'CC-BY-NC-ND-3.0',
                    'CC-BY-NC-ND-4.0',
                    'CC-BY-NC-SA-1.0',
                    'CC-BY-NC-SA-2.0',
                    'CC-BY-NC-SA-2.5',
                    'CC-BY-NC-SA-3.0',
                    'CC-BY-NC-SA-4.0',
                    'CC-BY-ND-1.0',
                    'CC-BY-ND-2.0',
                    'CC-BY-ND-2.5',
                    'CC-BY-ND-3.0',
                    'CC-BY-ND-4.0',
                    'CC-BY-SA-1.0',
                    'CC-BY-SA-2.0',
                    'CC-BY-SA-2.5',
                    'CC-BY-SA-3.0',
                    'CC-BY-SA-4.0',
                    'CC0-1.0',
                    'CDDL-1.0',
                    'CDDL-1.1',
                    'CECILL-1.0',
                    'CECILL-1.1',
                    'CECILL-2.0',
                    'CECILL-2.1',
                    'CECILL-B',
                    'CECILL-C',
                    'CNRI-Jython',
                    'CNRI-Python',
                    'CNRI-Python-GPL-Compatible',
                    'CPAL-1.0',
                    'CPL-1.0',
                    'CPOL-1.02',
                    'CUA-OPL-1.0',
                    'Caldera',
                    'ClArtistic',
                    'Condor-1.1',
                    'Crossword',
                    'CrystalStacker',
                    'Cube',
                    'D-FSL-1.0',
                    'DOC',
                    'DSDP',
                    'Dotseqn',
                    'ECL-1.0',
                    'ECL-2.0',
                    'EFL-1.0',
                    'EFL-2.0',
                    'EPL-1.0',
                    'EPL-2.0',
                    'EUDatagrid',
                    'EUPL-1.0',
                    'EUPL-1.1',
                    'Entessa',
                    'ErlPL-1.1',
                    'Eurosym',
                    'FSFAP',
                    'FSFUL',
                    'FSFULLR',
                    'FTL',
                    'Fair',
                    'Frameworx-1.0',
                    'FreeImage',
                    'GFDL-1.1',
                    'GFDL-1.2',
                    'GFDL-1.3',
                    'GL2PS',
                    'GPL-1.0',
                    'GPL-2.0',
                    'GPL-3.0',
                    'Giftware',
                    'Glide',
                    'Glulxe',
                    'HPND',
                    'HaskellReport',
                    'IBM-pibs',
                    'ICU',
                    'IJG',
                    'IPA',
                    'IPL-1.0',
                    'ISC',
                    'ImageMagick',
                    'Imlib2',
                    'Info-ZIP',
                    'Intel',
                    'Intel-ACPI',
                    'Interbase-1.0',
                    'JSON',
                    'JasPer-2.0',
                    'LAL-1.2',
                    'LAL-1.3',
                    'LGPL-2.0',
                    'LGPL-2.1',
                    'LGPL-3.0',
                    'LGPLLR',
                    'LPL-1.0',
                    'LPL-1.02',
                    'LPPL-1.0',
                    'LPPL-1.1',
                    'LPPL-1.2',
                    'LPPL-1.3a',
                    'LPPL-1.3c',
                    'Latex2e',
                    'Leptonica',
                    'LiLiQ-P-1.1',
                    'LiLiQ-R-1.1',
                    'LiLiQ-Rplus-1.1',
                    'Libpng',
                    'MIT',
                    'MIT-CMU',
                    'MIT-advertising',
                    'MIT-enna',
                    'MIT-feh',
                    'MITNFA',
                    'MPL-1.0',
                    'MPL-1.1',
                    'MPL-2.0',
                    'MPL-2.0-no-copyleft-exception',
                    'MS-PL',
                    'MS-RL',
                    'MTLL',
                    'MakeIndex',
                    'MirOS',
                    'Motosoto',
                    'Multics',
                    'Mup',
                    'NASA-1.3',
                    'NBPL-1.0',
                    'NCSA',
                    'NGPL',
                    'NLOD-1.0',
                    'NLPL',
                    'NOSL',
                    'NPL-1.0',
                    'NPL-1.1',
                    'NPOSL-3.0',
                    'NRL',
                    'NTP',
                    'Naumen',
                    'NetCDF',
                    'Newsletr',
                    'Nokia',
                    'Noweb',
                    'Nunit',
                    'OCCT-PL',
                    'OCLC-2.0',
                    'ODbL-1.0',
                    'OFL-1.0',
                    'OFL-1.1',
                    'OGTSL',
                    'OLDAP-1.1',
                    'OLDAP-1.2',
                    'OLDAP-1.3',
                    'OLDAP-1.4',
                    'OLDAP-2.0',
                    'OLDAP-2.0.1',
                    'OLDAP-2.1',
                    'OLDAP-2.2',
                    'OLDAP-2.2.1',
                    'OLDAP-2.2.2',
                    'OLDAP-2.3',
                    'OLDAP-2.4',
                    'OLDAP-2.5',
                    'OLDAP-2.6',
                    'OLDAP-2.7',
                    'OLDAP-2.8',
                    'OML',
                    'OPL-1.0',
                    'OSET-PL-2.1',
                    'OSL-1.0',
                    'OSL-1.1',
                    'OSL-2.0',
                    'OSL-2.1',
                    'OSL-3.0',
                    'OpenSSL',
                    'PDDL-1.0',
                    'PHP-3.0',
                    'PHP-3.01',
                    'Plexus',
                    'PostgreSQL',
                    'Python-2.0',
                    'QPL-1.0',
                    'Qhull',
                    'RHeCos-1.1',
                    'RPL-1.1',
                    'RPL-1.5',
                    'RPSL-1.0',
                    'RSA-MD',
                    'RSCPL',
                    'Rdisc',
                    'Ruby',
                    'SAX-PD',
                    'SCEA',
                    'SGI-B-1.0',
                    'SGI-B-1.1',
                    'SGI-B-2.0',
                    'SISSL',
                    'SISSL-1.2',
                    'SMLNJ',
                    'SMPPL',
                    'SNIA',
                    'SPL-1.0',
                    'SWL',
                    'Saxpath',
                    'Sendmail',
                    'SimPL-2.0',
                    'Sleepycat',
                    'Spencer-86',
                    'Spencer-94',
                    'Spencer-99',
                    'SugarCRM-1.1.3',
                    'TCL',
                    'TMate',
                    'TORQUE-1.1',
                    'TOSL',
                    'UPL-1.0',
                    'Unicode-TOU',
                    'Unlicense',
                    'VOSTROM',
                    'VSL-1.0',
                    'Vim',
                    'W3C',
                    'W3C-19980720',
                    'WTFPL',
                    'Watcom-1.0',
                    'Wsuipa',
                    'X11',
                    'XFree86-1.1',
                    'XSkat',
                    'Xerox',
                    'Xnet',
                    'YPL-1.0',
                    'YPL-1.1',
                    'ZPL-1.1',
                    'ZPL-2.0',
                    'ZPL-2.1',
                    'Zed',
                    'Zend-2.0',
                    'Zimbra-1.3',
                    'Zimbra-1.4',
                    'Zlib',
                    'bzip2-1.0.5',
                    'bzip2-1.0.6',
                    'curl',
                    'diffmark',
                    'dvipdfm',
                    'eGenix',
                    'gSOAP-1.3b',
                    'gnuplot',
                    'iMatix',
                    'libtiff',
                    'mpich2',
                    'psfrag',
                    'psutils',
                    'xinetd',
                    'xpp',
                    'zlib-acknowledgement',
                    'AGPL-1.0-or-later',
                    'AGPL-3.0-or-later',
                    'ANTLR-PD-fallback',
                    'blessing',
                    'BlueOak-1.0.0',
                    'BSD-1-Clause',
                    'BSD-2-Clause-Patent',
                    'BSD-2-Clause-Views',
                    'BSD-3-Clause-Modification',
                    'BSD-3-Clause-No-Military-License',
                    'BSD-3-Clause-Open-MPI',
                    'BSD-4-Clause-Shortened',
                    'BUSL-1.1',
                    'CAL-1.0',
                    'CAL-1.0-Combined-Work-Exception',
                    'CC-BY-3.0-AT',
                    'CC-BY-3.0-US',
                    'CC-BY-NC-ND-3.0-IGO',
                    'CC-BY-SA-2.0-UK',
                    'CC-BY-SA-2.1-JP',
                    'CC-BY-SA-3.0-AT',
                    'CC-PDDC',
                    'CDL-1.0',
                    'CDLA-Permissive-1.0',
                    'CDLA-Sharing-1.0',
                    'CERN-OHL-1.1',
                    'CERN-OHL-1.2',
                    'CERN-OHL-P-2.0',
                    'CERN-OHL-S-2.0',
                    'CERN-OHL-W-2.0',
                    'copyleft-next-0.3.0',
                    'copyleft-next-0.3.1',
                    'C-UDA-1.0',
                    'DRL-1.0',
                    'EPICS',
                    'EPL-2.0',
                    'etalab-2.0',
                    'EUPL-1.2',
                    'FreeBSD-DOC',
                    'GD',
                    'GFDL-1.1-invariants-only',
                    'GFDL-1.1-invariants-or-later',
                    'GFDL-1.1-no-invariants-only',
                    'GFDL-1.1-no-invariants-or-later',
                    'GFDL-1.1-or-later',
                    'GFDL-1.2-invariants-only',
                    'GFDL-1.2-invariants-or-later',
                    'GFDL-1.2-no-invariants-only',
                    'GFDL-1.2-no-invariants-or-later',
                    'GFDL-1.2-or-later',
                    'GFDL-1.3-invariants-only',
                    'GFDL-1.3-invariants-or-later',
                    'GFDL-1.3-no-invariants-only',
                    'GFDL-1.3-no-invariants-or-later',
                    'GFDL-1.3-or-later',
                    'GLWTPL',
                    'GPL-1.0-or-later',
                    'GPL-2.0-or-later',
                    'GPL-3.0-or-later',
                    'Hippocratic-2.1',
                    'HPND-sell-variant',
                    'HTMLTIDY',
                    'JPNIC',
                    'LGPL-2.0-or-later',
                    'LGPL-2.1-or-later',
                    'LGPL-3.0-or-later',
                    'libpng-2.0',
                    'libselinux-1.0',
                    'Linux-OpenIB',
                    'MIT-0',
                    'MIT-Modern-Variant',
                    'MIT-open-group',
                    'MulanPSL-1.0',
                    'MulanPSL-2.0',
                    'NAIST-2003',
                    'NCGL-UK-2.0',
                    'Net-SNMP',
                    'NIST-PD',
                    'NIST-PD-fallback',
                    'ODC-By-1.0',
                    'OFL-1.0-no-RFN',
                    'OFL-1.0-RFN',
                    'OFL-1.1-no-RFN',
                    'OFL-1.1-RFN',
                    'OGC-1.0',
                    'OGDL-Taiwan-1.0',
                    'OGL-Canada-2.0',
                    'OGL-UK-1.0',
                    'OGL-UK-2.0',
                    'OGL-UK-3.0',
                    'O-UDA-1.0',
                    'Parity-6.0.0',
                    'Parity-7.0.0',
                    'PolyForm-Noncommercial-1.0.0',
                    'PolyForm-Small-Business-1.0.0',
                    'PSF-2.0',
                    'Sendmail-8.23',
                    'SHL-0.5',
                    'SHL-0.51',
                    'SSH-OpenSSH',
                    'SSH-short',
                    'SSPL-1.0',
                    'TAPR-OHL-1.0',
                    'TCP-wrappers',
                    'TU-Berlin-1.0',
                    'TU-Berlin-2.0',
                    'UCL-1.0',
                    'Unicode-DFS-2015',
                    'Unicode-DFS-2016',
                    'Proprietary',
                    'Other',
                    'Not licensed',
                    'Freeware',
                ];
                return new_licenses.map(function (l) {
                    return { value: l, text: l };
                });
            })();
            $scope.costOptions = [
                { value: 'Free of charge', text: 'Free of charge' },
                {
                    value: 'Free of charge (with restrictions)',
                    text: 'Free of charge (with restrictions)',
                },
                { value: 'Commercial', text: 'Commercial' },
            ];

            $scope.languageOptions = [
                { value: 'ActionScript', text: 'ActionScript' },
                { value: 'Ada', text: 'Ada' },
                { value: 'AppleScript', text: 'AppleScript' },
                { value: 'Assembly language', text: 'Assembly language' },
                { value: 'AWK', text: 'AWK' },
                { value: 'Bash', text: 'Bash' },
                { value: 'C', text: 'C' },
                { value: 'C#', text: 'C#' },
                { value: 'C++', text: 'C++' },
                { value: 'Clojure', text: 'Clojure' },
                { value: 'COBOL', text: 'COBOL' },
                { value: 'ColdFusion', text: 'ColdFusion' },
                { value: 'Cython', text: 'Cython' },
                { value: 'CUDA', text: 'CUDA' },
                { value: 'CWL', text: 'CWL' },
                { value: 'D', text: 'D' },
                { value: 'Delphi', text: 'Delphi' },
                { value: 'Dylan', text: 'Dylan' },
                { value: 'Eiffel', text: 'Eiffel' },
                { value: 'Elm', text: 'Elm' },
                { value: 'F#', text: 'F#' },
                { value: 'Forth', text: 'Forth' },
                { value: 'Fortran', text: 'Fortran' },
                { value: 'Go', text: 'Go' },
                { value: 'Groovy', text: 'Groovy' },
                { value: 'Haskell', text: 'Haskell' },
                { value: 'Java', text: 'Java' },
                { value: 'JavaScript', text: 'JavaScript' },
                { value: 'JSP', text: 'JSP' },
                { value: 'Julia', text: 'Julia' },
                { value: 'Jython', text: 'Jython' },
                { value: 'Kotlin', text: 'Kotlin' },
                { value: 'LabVIEW', text: 'LabVIEW' },
                { value: 'Lisp', text: 'Lisp' },
                { value: 'Lua', text: 'Lua' },
                { value: 'Maple', text: 'Maple' },
                { value: 'Mathematica', text: 'Mathematica' },
                { value: 'MATLAB', text: 'MATLAB' },
                { value: 'MLXTRAN', text: 'MLXTRAN' },
                { value: 'NMTRAN', text: 'NMTRAN' },
                { value: 'OCaml', text: 'OCaml' },
                { value: 'Pascal', text: 'Pascal' },
                { value: 'Perl', text: 'Perl' },
                { value: 'PHP', text: 'PHP' },
                { value: 'Prolog', text: 'Prolog' },
                { value: 'PyMOL', text: 'PyMOL' },
                { value: 'Python', text: 'Python' },
                { value: 'Q#', text: 'Q#' },
                { value: 'QCL', text: 'QCL' },
                { value: 'R', text: 'R' },
                { value: 'Racket', text: 'Racket' },
                { value: 'REXX', text: 'REXX' },
                { value: 'Ruby', text: 'Ruby' },
                { value: 'Rust', text: 'Rust' },
                { value: 'SAS', text: 'SAS' },
                { value: 'Scala', text: 'Scala' },
                { value: 'Scheme', text: 'Scheme' },
                { value: 'Shell', text: 'Shell' },
                { value: 'Smalltalk', text: 'Smalltalk' },
                { value: 'SQL', text: 'SQL' },
                { value: 'Swift', text: 'Swift' },
                { value: 'Turing', text: 'Turing' },
                { value: 'TypeScript', text: 'TypeScript' },
                { value: 'Verilog', text: 'Verilog' },
                { value: 'VHDL', text: 'VHDL' },
                { value: 'Visual Basic', text: 'Visual Basic' },
                { value: 'XAML', text: 'XAML' },
                { value: 'Other', text: 'Other' },
            ];

            $scope.platformOptions = [
                { value: 'Mac', text: 'Mac' },
                { value: 'Linux', text: 'Linux' },
                { value: 'Windows', text: 'Windows' },
                { value: 'Android', text: 'Android' },
                { value: 'iOS', text: 'iOS' },
            ];

            $scope.accessibilityOptions = [
                { value: 'Open access', text: 'Open access' },
                {
                    value: 'Open access (with restrictions)',
                    text: 'Open access (with restrictions)',
                },
                { value: 'Restricted access', text: 'Restricted access' },
            ];

            $scope.maturityOptions = [
                { value: 'Emerging', text: 'Emerging' },
                { value: 'Mature', text: 'Mature' },
                { value: 'Legacy', text: 'Legacy' },
            ];

            $scope.toolTypeOptions = [
                { value: 'Bioinformatics portal', text: 'Bioinformatics portal' },
                { value: 'Command-line tool', text: 'Command-line tool' },
                { value: 'Database portal', text: 'Database portal' },
                { value: 'Desktop application', text: 'Desktop application' },
                { value: 'Library', text: 'Library' },
                { value: 'Mobile application', text: 'Mobile application' },
                { value: 'Ontology', text: 'Ontology' },
                { value: 'Plug-in', text: 'Plug-in' },
                { value: 'Script', text: 'Script' },
                { value: 'SPARQL endpoint', text: 'SPARQL endpoint' },
                { value: 'Suite', text: 'Suite' },
                { value: 'Web application', text: 'Web application' },
                { value: 'Web API', text: 'Web API' },
                { value: 'Web service', text: 'Web service' },
                { value: 'Workbench', text: 'Workbench' },
                { value: 'Workflow', text: 'Workflow' },
            ];

            $scope.linkTypeOptions = [
                { value: 'Discussion forum', text: 'Discussion forum' },
                { value: 'Galaxy service', text: 'Galaxy service' },
                { value: 'Helpdesk', text: 'Helpdesk' },
                { value: 'Issue tracker', text: 'Issue tracker' },
                { value: 'Mailing list', text: 'Mailing list' },
                { value: 'Mirror', text: 'Mirror' },
                { value: 'Repository', text: 'Repository' },
                { value: 'Service', text: 'Service' },
                { value: 'Social media', text: 'Social media' },
                { value: 'Software catalogue', text: 'Software catalogue' },
                { value: 'Technical monitoring', text: 'Technical monitoring' },
                { value: 'Other', text: 'Other' },
            ];

            $scope.downloadTypeOptions = [
                { value: 'Downloads page', text: 'Downloads page' },
                { value: 'API specification', text: 'API specification' },
                { value: 'Biological data', text: 'Biological data' },
                { value: 'Binaries', text: 'Binaries' },
                { value: 'Command-line specification', text: 'Command-line specification' },
                { value: 'Container file', text: 'Container file' },
                { value: 'Icon', text: 'Icon' },
                { value: 'Screenshot', text: 'Screenshot' },
                { value: 'Software package', text: 'Software package' },
                { value: 'Source code', text: 'Source code' },
                { value: 'Test data', text: 'Test data' },
                { value: 'Test script', text: 'Test script' },
                { value: 'Tool wrapper (CWL)', text: 'Tool wrapper (CWL)' },
                { value: 'Tool wrapper (Galaxy)', text: 'Tool wrapper (Galaxy)' },
                { value: 'Tool wrapper (Taverna)', text: 'Tool wrapper (Taverna)' },
                { value: 'Tool wrapper (Other)', text: 'Tool wrapper (Other)' },
                { value: 'VM Image', text: 'VM Image' },
                { value: 'Other', text: 'Other' },
            ];

            $scope.documentationTypeOptions = [
                { value: 'API documentation', text: 'API documentation' },
                { value: 'Citation instructions', text: 'Citation instructions' },
                { value: 'Code of conduct', text: 'Code of conduct' },
                { value: 'Command-line options', text: 'Command-line options' },
                { value: 'Contributions policy', text: 'Contributions policy' },
                { value: 'FAQ', text: 'FAQ' },
                { value: 'General', text: 'General' },
                { value: 'Governance', text: 'Governance' },
                { value: 'Installation instructions', text: 'Installation instructions' },
                { value: 'Quick start guide', text: 'Quick start guide' },
                { value: 'Release notes', text: 'Release notes' },
                { value: 'Terms of use', text: 'Terms of use' },
                { value: 'Training material', text: 'Training material' },
                { value: 'User manual', text: 'User manual' },
                { value: 'Other', text: 'Other' },
            ];

            $scope.publicationTypeOptions = [
                { value: 'Primary', text: 'Primary' },
                { value: 'Benchmarking study', text: 'Benchmarking study' },
                { value: 'Method', text: 'Method' },
                { value: 'Usage', text: 'Usage' },
                { value: 'Review', text: 'Review' },
                { value: 'Preprint', text: 'Preprint' },
                { value: 'Other', text: 'Other' },
            ];

            $scope.entityTypeOptions = [
                { value: 'Person', text: 'Person' },
                { value: 'Project', text: 'Project' },
                { value: 'Division', text: 'Division' },
                { value: 'Institute', text: 'Institute' },
                { value: 'Consortium', text: 'Consortium' },
                { value: 'Funding agency', text: 'Funding agency' },
            ];

            $scope.roleTypeOptions = [
                { value: 'Primary contact', text: 'Primary contact' },
                { value: 'Contributor', text: 'Contributor' },
                { value: 'Developer', text: 'Developer' },
                { value: 'Documentor', text: 'Documentor' },
                { value: 'Maintainer', text: 'Maintainer' },
                { value: 'Provider', text: 'Provider' },
                { value: 'Support', text: 'Support' },
            ];

            $scope.elixirPlatformOptions = [
                { value: 'Data', text: 'Data' },
                { value: 'Tools', text: 'Tools' },
                { value: 'Compute', text: 'Compute' },
                { value: 'Interoperability', text: 'Interoperability' },
                { value: 'Training', text: 'Training' },
            ];

            $scope.elixirNodeOptions = [
                { value: 'Belgium', text: 'Belgium' },
                { value: 'Czech Republic', text: 'Czech Republic' },
                { value: 'Denmark', text: 'Denmark' },
                { value: 'EMBL', text: 'EMBL' },
                { value: 'Estonia', text: 'Estonia' },
                { value: 'Finland', text: 'Finland' },
                { value: 'France', text: 'France' },
                { value: 'Germany', text: 'Germany' },
                { value: 'Greece', text: 'Greece' },
                { value: 'Hungary', text: 'Hungary' },
                { value: 'Ireland', text: 'Ireland' },
                { value: 'Israel', text: 'Israel' },
                { value: 'Italy', text: 'Italy' },
                { value: 'Luxembourg', text: 'Luxembourg' },
                { value: 'Netherlands', text: 'Netherlands' },
                { value: 'Norway', text: 'Norway' },
                { value: 'Portugal', text: 'Portugal' },
                { value: 'Slovenia', text: 'Slovenia' },
                { value: 'Spain', text: 'Spain' },
                { value: 'Sweden', text: 'Sweden' },
                { value: 'Switzerland', text: 'Switzerland' },
                { value: 'UK', text: 'UK' },
            ];

            $scope.elixirCommunityOptions = [
                { value: '3D-BioInfo', text: '3D-BioInfo', link: '3d-bioinfo' },
                { value: 'Biodiversity', text: 'Biodiversity', link: 'biodiversity' },
                { value: 'Cancer Data', text: 'Cancer Data', link: 'cancer-data' },
                { value: 'Federated Human Data', text: 'Federated Human Data', link: 'human-data' },
                {
                    value: 'Food and Nutrition',
                    text: 'Food and Nutrition',
                    link: 'food-and-nutrition',
                },
                { value: 'Galaxy', text: 'Galaxy', link: 'galaxy' },
                {
                    value: 'Human Copy Number Variation',
                    text: 'Human Copy Number Variation',
                    link: 'hcnv',
                },
                {
                    value: 'Intrinsically Disordered Proteins',
                    text: 'Intrinsically Disordered Proteins',
                    link: 'intrinsically-disordered-proteins',
                },
                {
                    value: 'Marine Metagenomics',
                    text: 'Marine Metagenomics',
                    link: 'marine-metagenomics',
                },
                { value: 'Metabolomics', text: 'Metabolomics', link: 'metabolomics' },
                {
                    value: 'Microbial Biotechnology',
                    text: 'Microbial Biotechnology',
                    link: 'microbial-biotechnology',
                },
                { value: 'Microbiome', text: 'Microbiome', link: 'microbiome' },
                { value: 'Plant Sciences', text: 'Plant Sciences', link: 'plant-sciences' },
                { value: 'Proteomics', text: 'Proteomics', link: 'proteomics' },
                { value: 'Rare Diseases', text: 'Rare Diseases', link: 'rare-diseases' },
                {
                    value: 'Research Data Management',
                    text: 'Research Data Management',
                    link: 'research-data-management',
                },
                {
                    value: 'Single-cell Omics',
                    text: 'Single-cell Omics',
                    link: 'single-cell-omics',
                },
                { value: 'Systems Biology', text: 'Systems Biology', link: 'systems-biology' },
                { value: 'Toxicology', text: 'Toxicology', link: 'toxicology' },
            ];

            $scope.otherIdTypeOptions = [
                { value: 'doi', text: 'doi' },
                { value: 'rrid', text: 'rrid' },
                { value: 'cpe', text: 'cpe' },
            ];

            $scope.relationTypeOptions = [
                { value: 'isNewVersionOf', text: 'isNewVersionOf' },
                { value: 'hasNewVersion', text: 'hasNewVersion' },
                { value: 'uses', text: 'uses' },
                { value: 'usedBy', text: 'usedBy' },
                { value: 'includes', text: 'includes' },
                { value: 'includedIn', text: 'includedIn' },
            ];

            $scope.confidenceOptions = [
                { value: 'tool', text: 'tool' },
                { value: 'high', text: 'high' },
                { value: 'medium', text: 'medium' },
                { value: 'low', text: 'low' },
                { value: 'very low', text: 'very low' },
            ];

            $scope.$watch(
                'software',
                function () {
                    angular.forEach($scope.software, function (value, key) {
                        if (value === null || value === '') {
                            delete $scope.software[key];
                        }
                    });
                },
                true
            );
        },
    ])
    .controller('ToolUpdateController', [
        '$scope',
        '$controller',
        '$timeout',
        '$state',
        '$stateParams',
        'Tool',
        'ToolUpdateValidator',
        'CommunityCollection',
        function (
            $scope,
            $controller,
            $timeout,
            $state,
            $stateParams,
            Tool,
            ToolUpdateValidator,
            CommunityCollection
        ) {
            // inherit common controller
            $controller('ToolEditController', { $scope: $scope });

            // sets which controller is in use, so the HTML can adapt
            $scope.controller = 'update';

            // set the ID to not autoupdate when name is changed
            $scope.autoUpdateId = false;
            $scope.CommunityCollection = CommunityCollection;
            $scope.validateButtonClick = function () {
                $timeout(function () {
                    $scope.sendResource(
                        ToolUpdateValidator.update,
                        $scope.validationProgress,
                        false,
                        'update-validate'
                    );
                }, 100);
            };

            $scope.registerButtonClick = function () {
                $timeout(function () {
                    if (confirm('Are you sure you want to update the resource? ')) {
                        $scope.sendResource(Tool.update, $scope.savingProgress, false, 'update');
                    }
                }, 100);
            };

            $scope.deleteButtonClick = function () {
                $timeout(function () {
                    if (confirm('Are you sure you want to remove the resource? ')) {
                        if (
                            confirm(
                                'This will remove the resource and cannot be undone. Are you sure you want to continue? '
                            )
                        ) {
                            $scope.sendResource(
                                Tool.remove,
                                $scope.deletingProgress,
                                true,
                                'delete'
                            );
                        }
                    }
                }, 100);
            };

            $scope.naviagateToTool = function (biotoolsID) {
                $timeout(function () {
                    if (
                        confirm(
                            'Make sure you save before navigating away! Are you sure you want to leave? '
                        )
                    ) {
                        $state.go('tool', { id: biotoolsID }, { reload: true });
                    }
                }, 100);
            };

            // when a tool is being updated, display the current URL
            // $scope.$watch('software', function() {
            // 	$scope.setURL();
            // })
        },
    ])
    .controller('ToolCreateController', [
        '$scope',
        '$controller',
        '$timeout',
        'ToolListConnection',
        'ToolCreateValidator',
        'User',
        '$stateParams',
        'CommunityCollection',
        function (
            $scope,
            $controller,
            $timeout,
            ToolListConnection,
            ToolCreateValidator,
            User,
            $stateParams,
            CommunityCollection
        ) {
            // inherit common controller
            $controller('ToolEditController', { $scope: $scope });
            $scope.orderby = 'text';
            // sets which controller is in use, so the HTML can adapt
            $scope.controller = 'create';

            // initially set the ID to change automatically when name is modified
            $scope.biotoolsIDDisabled = true;
            $scope.editIdButtonText = 'Edit ID';
            $scope.CommunityCollection = CommunityCollection;
            // remove or replace all URL unsafe characters and set software.id
            $scope.makeIdURLSafe = function (value) {
                if (typeof value != 'undefined' && $scope.biotoolsIDDisabled) {
                    $scope.software.biotoolsID = value
                        .replace(/[^a-zA-Z0-9_~ .-]*/g, '')
                        .replace(/[ ]+/g, '_')
                        .toLowerCase();
                } else if ($scope.biotoolsIDDisabled) {
                    $scope.software.biotoolsID = '';
                }
            };

            $scope.editIdToggleButtonClick = function () {
                $scope.biotoolsIDDisabled = !$scope.biotoolsIDDisabled;
                $scope.makeIdURLSafe($scope.software.name);

                if ($scope.biotoolsIDDisabled) {
                    $scope.editIdButtonText = 'Edit ID';
                } else {
                    $scope.editIdButtonText = 'From Name';
                }
            };

            $scope.validateButtonClick = function () {
                $timeout(function () {
                    $scope.sendResource(
                        ToolCreateValidator.save,
                        $scope.validationProgress,
                        false,
                        'create-validate'
                    );
                }, 100);
            };

            $scope.registerButtonClick = function () {
                if (
                    confirm(
                        'Are you sure you want to save the resource?\nOnce saved the tool ID cannot be changed!'
                    )
                ) {
                    $timeout(function () {
                        $scope.sendResource(
                            ToolListConnection.save,
                            $scope.savingProgress,
                            false,
                            'create'
                        );
                    }, 100);
                }
            };

            // TODO: needs to keep it DRY and in a service
            // function to clean all nulls from tool gotten from API
            function cleanNulls(object) {
                for (var key in object) {
                    if (object[key] == null) {
                        delete object[key];
                    } else if (object[key].constructor === Array) {
                        if (object[key].length == 0) {
                            delete object[key];
                        } else {
                            for (var i in object[key]) {
                                cleanNulls(object[key][i]);
                            }
                        }
                    } else if (typeof object[key] === 'object') {
                        cleanNulls(object[key]);
                    }
                }
            }

            if (typeof $stateParams.newVersionOf !== 'undefined') {
                $scope.newVersion = true;
                $scope.software = ToolLatest.get(
                    { id: $stateParams.newVersionOf },
                    function (response) {
                        // success handler
                        cleanNulls($scope.software);
                        $scope.software.version = null;
                    },
                    function (response) {
                        // error handler
                        if (response.status == 404) {
                            $scope.notFound = true;
                        }
                    }
                );
            } else {
                $scope.newVersion = false;
                // create the 'empty' software object
                $timeout(function () {
                    $scope.software = {
                        owner: $scope.User.getUsername(),
                        name: '',
                        description: '',
                        homepage: '',
                    };
                }, 100);
            }
        },
    ])
    .controller('LoginController', [
        '$scope',
        '$state',
        'djangoAuth',
        '$rootScope',
        function ($scope, $state, djangoAuth, $rootScope) {
            $scope.credentials = {};

            $scope.loginButtonClick = function () {
                djangoAuth.login($scope.credentials.username, $scope.credentials.password).then(
                    function (response) {
                        // go to states set before redirection to login
                        if (
                            typeof $rootScope.toState == 'undefined' ||
                            /signup/.test($rootScope.toState.name) ||
                            /reset-password/.test($rootScope.toState.name)
                        ) {
                            $state.go('search');
                        } else {
                            $state.go($rootScope.toState.name, $rootScope.toStateParams);
                        }
                    },
                    function (response) {
                        $scope.loginErrors = response.general_errors;
                    }
                );
            };

            // clean errors when credentials are changed
            $scope.$watch(
                'credentials',
                function () {
                    if ($scope.loginErrors) {
                        $scope.loginErrors.pop();
                        delete $scope.loginErrors;
                    }
                },
                true
            );
        },
    ])
    .controller('SignupController', [
        '$scope',
        '$state',
        'djangoAuth',
        '$rootScope',
        '$timeout',
        function ($scope, $state, djangoAuth, $rootScope, $timeout) {
            $scope.credentials = {};
            $scope.error_message = {};
            $scope.error_message.username = '';
            $scope.error_message.email = '';
            $scope.error_message.creation = '';

            // check if username is taken
            var initializing_username = true;
            $scope.$watch('credentials.username', function (newValue, oldValue, scope) {
                if (!initializing_username) {
                    $scope.error_message.username = '';
                    djangoAuth.register($scope.credentials.username, null, null, null, null).then(
                        function (response) {
                            // success never happens since parameters are missing
                        },
                        function (response) {
                            if (response.hasOwnProperty('username')) {
                                $scope.error_message.username = 'Username is already taken.';
                            }
                        }
                    );
                } else {
                    initializing_username = false;
                }
            });

            // check if email is taken
            var initializing_email = true;
            $scope.$watch('credentials.email', function (newValue, oldValue, scope) {
                if (!initializing_email) {
                    $scope.error_message.email = '';
                    djangoAuth.register(null, null, null, $scope.credentials.email, null).then(
                        function (response) {
                            // success never happens since parameters are missing
                        },
                        function (response) {
                            if (response.hasOwnProperty('email')) {
                                $scope.error_message.email = 'Email is invalid or already taken.';
                            }
                        }
                    );
                } else {
                    initializing_email = false;
                }
            });

            $scope.signupButtonClick = function () {
                $scope.loading = true;
                $timeout(function () {
                    djangoAuth
                        .register(
                            $scope.credentials.username,
                            $scope.credentials.password,
                            $scope.credentials.password,
                            $scope.credentials.email,
                            null
                        )
                        .then(
                            function (response) {
                                $state.go('signup.success');
                                $scope.loading = false;
                            },
                            function (response) {
                                $scope.error_message.email = response.email.join();
                                $scope.error_message.username = response.username.join();
                                $scope.error_message.creation = response.message;
                                $scope.loading = false;
                            }
                        );
                }, 100);
            };
        },
    ])
    .controller('SignupVerifyEmailKeyController', [
        '$scope',
        '$state',
        '$stateParams',
        'djangoAuth',
        function ($scope, $state, $stateParams, djangoAuth) {
            $scope.error_message = '';

            djangoAuth.verify($stateParams.key).then(
                function (response) {
                    $state.go('signup.verify-email.success');
                },
                function (response) {
                    $scope.error_message = response.message;
                }
            );
        },
    ])
    .controller('ResetPasswordController', [
        '$scope',
        '$state',
        '$stateParams',
        'djangoAuth',
        function ($scope, $state, $stateParams, djangoAuth) {
            $scope.credentials = {};
            $scope.error_message = '';
            $scope.success_message = '';

            $scope.loading = false;
            $scope.resetButtonClick = function () {
                $scope.error_message = '';
                $scope.success_message = '';
                $scope.loading = true;
                djangoAuth.resetPassword($scope.credentials.email).then(
                    function (response) {
                        $scope.success_message =
                            'If this email is linked to an account, a reset link will be sent.';
                        $scope.loading = false;
                    },
                    function (response) {
                        $scope.error_message = response;
                        $scope.loading = false;
                    }
                );
            };
        },
    ])
    .controller('ResetPasswordConfirmController', [
        '$scope',
        '$state',
        '$stateParams',
        'djangoAuth',
        function ($scope, $state, $stateParams, djangoAuth) {
            $scope.credentials = {};
            $scope.error_message = false;
            var uid = $stateParams.uid;
            var token = $stateParams.token;

            $scope.loading = false;
            $scope.resetButtonClick = function () {
                $scope.error_message = false;
                $scope.loading = true;
                djangoAuth
                    .confirmReset(
                        uid,
                        token,
                        $scope.credentials.password,
                        $scope.credentials.password
                    )
                    .then(
                        function (response) {
                            $state.go('reset-password.confirm.success');
                            $scope.loading = false;
                        },
                        function (response) {
                            $scope.error_message = true;
                            $scope.loading = false;
                        }
                    );
            };
        },
    ]);

function EdamModalCtrl($uibModalInstance, edam, onto, type, suggestions) {
    var vm = this;
    vm.data = angular.copy(edam);
    vm.onto = onto;
    vm.self = $uibModalInstance;
    vm.type = type;
    vm.suggestions = suggestions;

    vm.saveData = function () {
        if (isEmptyObject(vm.data)) {
            $uibModalInstance.dismiss('cancel');
            return;
        }
        $uibModalInstance.close(vm.data);
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
        $uibModalInstance.dismiss('cancel');
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
