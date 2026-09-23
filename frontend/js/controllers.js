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
        '$http',
        'Bridge',
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
            $uibModal,
            $http,
            Bridge
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
            $scope.bridge = { url: '', inProgress: false, message: null, raw: null, choices: null, active: false };

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

                        if (response && response.no_changes) {
                            progress.noChanges = true;
                            return;
                        }

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

            // metadata bridge (implementation in js/bridge.js, Bridge service)
            $scope.isGithubUrl = function (url) {
                return Bridge.isGithubUrl(url);
            };

            $scope.initBridgeUrl = function () {
                Bridge.prefillUrl($scope.software, $scope.bridge);
            };

            $scope.bridgeButtonClick = function () {
                Bridge.run(
                    $scope.bridge,
                    $scope.software,
                    $scope.software && $scope.software.biotoolsID
                );
            };

            // number of bridge suggestions with a pending (non-keep) action,
            // shown as a badge on the GitHub Bridge tab
            $scope.bridgeTabCount = function () {
                return ($scope.bridge.choices || []).filter(function (c) {
                    return c.action !== 'keep';
                }).length;
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
                        $scope.savingProgress.noChanges = false;
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
                    // DEBUG: auto-populate the bridge review tab once the
                    // tool is loaded (no-op unless DEBUG is enabled in bridge.js)
                    if (newVal && (newVal.biotoolsID || newVal.name)) {
                        Bridge.initDebug($scope.bridge, $scope.software);
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
                        if (
                            data.resultList &&
                            data.resultList.result &&
                            data.resultList.result.length > 0
                        ) {
                            var rec = data.resultList.result[0];
                            if (rec.doi) pub.doi = rec.doi;
                            if (rec.pmid) pub.pmid = rec.pmid;
                            if (rec.pmcid) pub.pmcid = rec.pmcid;
                            $scope.$apply();
                        }
                    })
                    .catch(function (err) {
                        /*  handle error */
                    });
            }

            $scope.onPublicationIdChange = function (idType, value, index) {
                if (value && value.trim() !== '') {
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

            $scope.licenseOptions = [
                { value: 'Freeware', text: 'Freeware' },
                { value: 'Proprietary', text: 'Proprietary' },
                { value: 'Other', text: 'Other' },
                { value: 'Not licensed', text: 'Not licensed' },
                { value: '0BSD', text: '0BSD' },
                { value: '3D-Slicer-1.0', text: '3D-Slicer-1.0' },
                { value: 'AAL', text: 'AAL' },
                { value: 'ADSL', text: 'ADSL' },
                { value: 'AFL-1.1', text: 'AFL-1.1' },
                { value: 'AFL-1.2', text: 'AFL-1.2' },
                { value: 'AFL-2.0', text: 'AFL-2.0' },
                { value: 'AFL-2.1', text: 'AFL-2.1' },
                { value: 'AFL-3.0', text: 'AFL-3.0' },
                { value: 'AGPL-1.0', text: 'AGPL-1.0' },
                { value: 'AGPL-1.0-only', text: 'AGPL-1.0-only' },
                { value: 'AGPL-1.0-or-later', text: 'AGPL-1.0-or-later' },
                { value: 'AGPL-3.0', text: 'AGPL-3.0' },
                { value: 'AGPL-3.0-only', text: 'AGPL-3.0-only' },
                { value: 'AGPL-3.0-or-later', text: 'AGPL-3.0-or-later' },
                { value: 'ALGLIB-Documentation', text: 'ALGLIB-Documentation' },
                { value: 'AMD-newlib', text: 'AMD-newlib' },
                { value: 'AMDPLPA', text: 'AMDPLPA' },
                { value: 'AML', text: 'AML' },
                { value: 'AML-glslang', text: 'AML-glslang' },
                { value: 'AMPAS', text: 'AMPAS' },
                { value: 'ANTLR-PD', text: 'ANTLR-PD' },
                { value: 'ANTLR-PD-fallback', text: 'ANTLR-PD-fallback' },
                { value: 'APAFML', text: 'APAFML' },
                { value: 'APL-1.0', text: 'APL-1.0' },
                { value: 'APSL-1.0', text: 'APSL-1.0' },
                { value: 'APSL-1.1', text: 'APSL-1.1' },
                { value: 'APSL-1.2', text: 'APSL-1.2' },
                { value: 'APSL-2.0', text: 'APSL-2.0' },
                { value: 'ASWF-Digital-Assets-1.0', text: 'ASWF-Digital-Assets-1.0' },
                { value: 'ASWF-Digital-Assets-1.1', text: 'ASWF-Digital-Assets-1.1' },
                { value: 'Abstyles', text: 'Abstyles' },
                { value: 'AdaCore-doc', text: 'AdaCore-doc' },
                { value: 'Adobe-2006', text: 'Adobe-2006' },
                { value: 'Adobe-Display-PostScript', text: 'Adobe-Display-PostScript' },
                { value: 'Adobe-Glyph', text: 'Adobe-Glyph' },
                { value: 'Adobe-Utopia', text: 'Adobe-Utopia' },
                { value: 'Advanced-Cryptics-Dictionary', text: 'Advanced-Cryptics-Dictionary' },
                { value: 'Afmparse', text: 'Afmparse' },
                { value: 'Aladdin', text: 'Aladdin' },
                { value: 'Apache-1.0', text: 'Apache-1.0' },
                { value: 'Apache-1.1', text: 'Apache-1.1' },
                { value: 'Apache-2.0', text: 'Apache-2.0' },
                { value: 'App-s2p', text: 'App-s2p' },
                { value: 'Arphic-1999', text: 'Arphic-1999' },
                { value: 'Artistic-1.0', text: 'Artistic-1.0' },
                { value: 'Artistic-1.0-Perl', text: 'Artistic-1.0-Perl' },
                { value: 'Artistic-1.0-cl8', text: 'Artistic-1.0-cl8' },
                { value: 'Artistic-2.0', text: 'Artistic-2.0' },
                { value: 'Artistic-dist', text: 'Artistic-dist' },
                { value: 'Aspell-RU', text: 'Aspell-RU' },
                { value: 'BOLA-1.1', text: 'BOLA-1.1' },
                { value: 'BSD-1-Clause', text: 'BSD-1-Clause' },
                { value: 'BSD-2-Clause', text: 'BSD-2-Clause' },
                { value: 'BSD-2-Clause-Darwin', text: 'BSD-2-Clause-Darwin' },
                { value: 'BSD-2-Clause-FreeBSD', text: 'BSD-2-Clause-FreeBSD' },
                { value: 'BSD-2-Clause-NetBSD', text: 'BSD-2-Clause-NetBSD' },
                { value: 'BSD-2-Clause-Patent', text: 'BSD-2-Clause-Patent' },
                { value: 'BSD-2-Clause-Views', text: 'BSD-2-Clause-Views' },
                { value: 'BSD-2-Clause-first-lines', text: 'BSD-2-Clause-first-lines' },
                { value: 'BSD-2-Clause-pkgconf-disclaimer', text: 'BSD-2-Clause-pkgconf-disclaimer' },
                { value: 'BSD-2-Clause-pos-unchanged', text: 'BSD-2-Clause-pos-unchanged' },
                { value: 'BSD-3-Clause', text: 'BSD-3-Clause' },
                { value: 'BSD-3-Clause-Attribution', text: 'BSD-3-Clause-Attribution' },
                { value: 'BSD-3-Clause-Clear', text: 'BSD-3-Clause-Clear' },
                { value: 'BSD-3-Clause-HP', text: 'BSD-3-Clause-HP' },
                { value: 'BSD-3-Clause-LBNL', text: 'BSD-3-Clause-LBNL' },
                { value: 'BSD-3-Clause-Modification', text: 'BSD-3-Clause-Modification' },
                { value: 'BSD-3-Clause-No-Military-License', text: 'BSD-3-Clause-No-Military-License' },
                { value: 'BSD-3-Clause-No-Nuclear-License', text: 'BSD-3-Clause-No-Nuclear-License' },
                { value: 'BSD-3-Clause-No-Nuclear-License-2014', text: 'BSD-3-Clause-No-Nuclear-License-2014' },
                { value: 'BSD-3-Clause-No-Nuclear-Warranty', text: 'BSD-3-Clause-No-Nuclear-Warranty' },
                { value: 'BSD-3-Clause-Open-MPI', text: 'BSD-3-Clause-Open-MPI' },
                { value: 'BSD-3-Clause-Sun', text: 'BSD-3-Clause-Sun' },
                { value: 'BSD-3-Clause-Tso', text: 'BSD-3-Clause-Tso' },
                { value: 'BSD-3-Clause-acpica', text: 'BSD-3-Clause-acpica' },
                { value: 'BSD-3-Clause-flex', text: 'BSD-3-Clause-flex' },
                { value: 'BSD-4-Clause', text: 'BSD-4-Clause' },
                { value: 'BSD-4-Clause-Shortened', text: 'BSD-4-Clause-Shortened' },
                { value: 'BSD-4-Clause-UC', text: 'BSD-4-Clause-UC' },
                { value: 'BSD-4.3RENO', text: 'BSD-4.3RENO' },
                { value: 'BSD-4.3TAHOE', text: 'BSD-4.3TAHOE' },
                { value: 'BSD-Advertising-Acknowledgement', text: 'BSD-Advertising-Acknowledgement' },
                { value: 'BSD-Attribution-HPND-disclaimer', text: 'BSD-Attribution-HPND-disclaimer' },
                { value: 'BSD-Inferno-Nettverk', text: 'BSD-Inferno-Nettverk' },
                { value: 'BSD-Mark-Modifications', text: 'BSD-Mark-Modifications' },
                { value: 'BSD-Protection', text: 'BSD-Protection' },
                { value: 'BSD-Source-Code', text: 'BSD-Source-Code' },
                { value: 'BSD-Source-Code-no-disclaimer', text: 'BSD-Source-Code-no-disclaimer' },
                { value: 'BSD-Source-beginning-file', text: 'BSD-Source-beginning-file' },
                { value: 'BSD-Systemics', text: 'BSD-Systemics' },
                { value: 'BSD-Systemics-W3Works', text: 'BSD-Systemics-W3Works' },
                { value: 'BSD-ask-to-endorse', text: 'BSD-ask-to-endorse' },
                { value: 'BSL-1.0', text: 'BSL-1.0' },
                { value: 'BUSL-1.1', text: 'BUSL-1.1' },
                { value: 'Baekmuk', text: 'Baekmuk' },
                { value: 'Bahyph', text: 'Bahyph' },
                { value: 'Barr', text: 'Barr' },
                { value: 'Beerware', text: 'Beerware' },
                { value: 'BitTorrent-1.0', text: 'BitTorrent-1.0' },
                { value: 'BitTorrent-1.1', text: 'BitTorrent-1.1' },
                { value: 'Bitstream-Charter', text: 'Bitstream-Charter' },
                { value: 'Bitstream-Vera', text: 'Bitstream-Vera' },
                { value: 'BlueOak-1.0.0', text: 'BlueOak-1.0.0' },
                { value: 'Boehm-GC', text: 'Boehm-GC' },
                { value: 'Boehm-GC-without-fee', text: 'Boehm-GC-without-fee' },
                { value: 'Borceux', text: 'Borceux' },
                { value: 'Brian-Gladman-2-Clause', text: 'Brian-Gladman-2-Clause' },
                { value: 'Brian-Gladman-3-Clause', text: 'Brian-Gladman-3-Clause' },
                { value: 'Brian-Gladman-3-Clause-no-conversion', text: 'Brian-Gladman-3-Clause-no-conversion' },
                { value: 'Buddy', text: 'Buddy' },
                { value: 'Bugroff', text: 'Bugroff' },
                { value: 'C-UDA-1.0', text: 'C-UDA-1.0' },
                { value: 'CAL-1.0', text: 'CAL-1.0' },
                { value: 'CAL-1.0-Combined-Work-Exception', text: 'CAL-1.0-Combined-Work-Exception' },
                { value: 'CAPEC-tou', text: 'CAPEC-tou' },
                { value: 'CATOSL-1.1', text: 'CATOSL-1.1' },
                { value: 'CC-BY-1.0', text: 'CC-BY-1.0' },
                { value: 'CC-BY-2.0', text: 'CC-BY-2.0' },
                { value: 'CC-BY-2.5', text: 'CC-BY-2.5' },
                { value: 'CC-BY-2.5-AU', text: 'CC-BY-2.5-AU' },
                { value: 'CC-BY-3.0', text: 'CC-BY-3.0' },
                { value: 'CC-BY-3.0-AT', text: 'CC-BY-3.0-AT' },
                { value: 'CC-BY-3.0-AU', text: 'CC-BY-3.0-AU' },
                { value: 'CC-BY-3.0-DE', text: 'CC-BY-3.0-DE' },
                { value: 'CC-BY-3.0-IGO', text: 'CC-BY-3.0-IGO' },
                { value: 'CC-BY-3.0-NL', text: 'CC-BY-3.0-NL' },
                { value: 'CC-BY-3.0-US', text: 'CC-BY-3.0-US' },
                { value: 'CC-BY-4.0', text: 'CC-BY-4.0' },
                { value: 'CC-BY-NC-1.0', text: 'CC-BY-NC-1.0' },
                { value: 'CC-BY-NC-2.0', text: 'CC-BY-NC-2.0' },
                { value: 'CC-BY-NC-2.5', text: 'CC-BY-NC-2.5' },
                { value: 'CC-BY-NC-3.0', text: 'CC-BY-NC-3.0' },
                { value: 'CC-BY-NC-3.0-DE', text: 'CC-BY-NC-3.0-DE' },
                { value: 'CC-BY-NC-3.0-IGO', text: 'CC-BY-NC-3.0-IGO' },
                { value: 'CC-BY-NC-4.0', text: 'CC-BY-NC-4.0' },
                { value: 'CC-BY-NC-ND-1.0', text: 'CC-BY-NC-ND-1.0' },
                { value: 'CC-BY-NC-ND-2.0', text: 'CC-BY-NC-ND-2.0' },
                { value: 'CC-BY-NC-ND-2.5', text: 'CC-BY-NC-ND-2.5' },
                { value: 'CC-BY-NC-ND-3.0', text: 'CC-BY-NC-ND-3.0' },
                { value: 'CC-BY-NC-ND-3.0-DE', text: 'CC-BY-NC-ND-3.0-DE' },
                { value: 'CC-BY-NC-ND-3.0-IGO', text: 'CC-BY-NC-ND-3.0-IGO' },
                { value: 'CC-BY-NC-ND-4.0', text: 'CC-BY-NC-ND-4.0' },
                { value: 'CC-BY-NC-SA-1.0', text: 'CC-BY-NC-SA-1.0' },
                { value: 'CC-BY-NC-SA-2.0', text: 'CC-BY-NC-SA-2.0' },
                { value: 'CC-BY-NC-SA-2.0-DE', text: 'CC-BY-NC-SA-2.0-DE' },
                { value: 'CC-BY-NC-SA-2.0-FR', text: 'CC-BY-NC-SA-2.0-FR' },
                { value: 'CC-BY-NC-SA-2.0-UK', text: 'CC-BY-NC-SA-2.0-UK' },
                { value: 'CC-BY-NC-SA-2.5', text: 'CC-BY-NC-SA-2.5' },
                { value: 'CC-BY-NC-SA-3.0', text: 'CC-BY-NC-SA-3.0' },
                { value: 'CC-BY-NC-SA-3.0-DE', text: 'CC-BY-NC-SA-3.0-DE' },
                { value: 'CC-BY-NC-SA-3.0-IGO', text: 'CC-BY-NC-SA-3.0-IGO' },
                { value: 'CC-BY-NC-SA-4.0', text: 'CC-BY-NC-SA-4.0' },
                { value: 'CC-BY-ND-1.0', text: 'CC-BY-ND-1.0' },
                { value: 'CC-BY-ND-2.0', text: 'CC-BY-ND-2.0' },
                { value: 'CC-BY-ND-2.5', text: 'CC-BY-ND-2.5' },
                { value: 'CC-BY-ND-3.0', text: 'CC-BY-ND-3.0' },
                { value: 'CC-BY-ND-3.0-DE', text: 'CC-BY-ND-3.0-DE' },
                { value: 'CC-BY-ND-4.0', text: 'CC-BY-ND-4.0' },
                { value: 'CC-BY-SA-1.0', text: 'CC-BY-SA-1.0' },
                { value: 'CC-BY-SA-2.0', text: 'CC-BY-SA-2.0' },
                { value: 'CC-BY-SA-2.0-UK', text: 'CC-BY-SA-2.0-UK' },
                { value: 'CC-BY-SA-2.1-JP', text: 'CC-BY-SA-2.1-JP' },
                { value: 'CC-BY-SA-2.5', text: 'CC-BY-SA-2.5' },
                { value: 'CC-BY-SA-3.0', text: 'CC-BY-SA-3.0' },
                { value: 'CC-BY-SA-3.0-AT', text: 'CC-BY-SA-3.0-AT' },
                { value: 'CC-BY-SA-3.0-DE', text: 'CC-BY-SA-3.0-DE' },
                { value: 'CC-BY-SA-3.0-IGO', text: 'CC-BY-SA-3.0-IGO' },
                { value: 'CC-BY-SA-4.0', text: 'CC-BY-SA-4.0' },
                { value: 'CC-PDDC', text: 'CC-PDDC' },
                { value: 'CC-PDM-1.0', text: 'CC-PDM-1.0' },
                { value: 'CC-SA-1.0', text: 'CC-SA-1.0' },
                { value: 'CC0-1.0', text: 'CC0-1.0' },
                { value: 'CDDL-1.0', text: 'CDDL-1.0' },
                { value: 'CDDL-1.1', text: 'CDDL-1.1' },
                { value: 'CDL-1.0', text: 'CDL-1.0' },
                { value: 'CDLA-Permissive-1.0', text: 'CDLA-Permissive-1.0' },
                { value: 'CDLA-Permissive-2.0', text: 'CDLA-Permissive-2.0' },
                { value: 'CDLA-Sharing-1.0', text: 'CDLA-Sharing-1.0' },
                { value: 'CECILL-1.0', text: 'CECILL-1.0' },
                { value: 'CECILL-1.1', text: 'CECILL-1.1' },
                { value: 'CECILL-2.0', text: 'CECILL-2.0' },
                { value: 'CECILL-2.1', text: 'CECILL-2.1' },
                { value: 'CECILL-B', text: 'CECILL-B' },
                { value: 'CECILL-C', text: 'CECILL-C' },
                { value: 'CERN-OHL-1.1', text: 'CERN-OHL-1.1' },
                { value: 'CERN-OHL-1.2', text: 'CERN-OHL-1.2' },
                { value: 'CERN-OHL-P-2.0', text: 'CERN-OHL-P-2.0' },
                { value: 'CERN-OHL-S-2.0', text: 'CERN-OHL-S-2.0' },
                { value: 'CERN-OHL-W-2.0', text: 'CERN-OHL-W-2.0' },
                { value: 'CFITSIO', text: 'CFITSIO' },
                { value: 'CMU-Mach', text: 'CMU-Mach' },
                { value: 'CMU-Mach-nodoc', text: 'CMU-Mach-nodoc' },
                { value: 'CNRI-Jython', text: 'CNRI-Jython' },
                { value: 'CNRI-Python', text: 'CNRI-Python' },
                { value: 'CNRI-Python-GPL-Compatible', text: 'CNRI-Python-GPL-Compatible' },
                { value: 'COIL-1.0', text: 'COIL-1.0' },
                { value: 'CPAL-1.0', text: 'CPAL-1.0' },
                { value: 'CPL-1.0', text: 'CPL-1.0' },
                { value: 'CPOL-1.02', text: 'CPOL-1.02' },
                { value: 'CUA-OPL-1.0', text: 'CUA-OPL-1.0' },
                { value: 'Caldera', text: 'Caldera' },
                { value: 'Caldera-no-preamble', text: 'Caldera-no-preamble' },
                { value: 'Catharon', text: 'Catharon' },
                { value: 'ClArtistic', text: 'ClArtistic' },
                { value: 'Clips', text: 'Clips' },
                { value: 'Community-Spec-1.0', text: 'Community-Spec-1.0' },
                { value: 'Condor-1.1', text: 'Condor-1.1' },
                { value: 'Cornell-Lossless-JPEG', text: 'Cornell-Lossless-JPEG' },
                { value: 'Cronyx', text: 'Cronyx' },
                { value: 'Crossword', text: 'Crossword' },
                { value: 'CryptoSwift', text: 'CryptoSwift' },
                { value: 'CrystalStacker', text: 'CrystalStacker' },
                { value: 'Cube', text: 'Cube' },
                { value: 'D-FSL-1.0', text: 'D-FSL-1.0' },
                { value: 'DEC-3-Clause', text: 'DEC-3-Clause' },
                { value: 'DL-DE-BY-2.0', text: 'DL-DE-BY-2.0' },
                { value: 'DL-DE-ZERO-2.0', text: 'DL-DE-ZERO-2.0' },
                { value: 'DOC', text: 'DOC' },
                { value: 'DRL-1.0', text: 'DRL-1.0' },
                { value: 'DRL-1.1', text: 'DRL-1.1' },
                { value: 'DSDP', text: 'DSDP' },
                { value: 'DocBook-DTD', text: 'DocBook-DTD' },
                { value: 'DocBook-Schema', text: 'DocBook-Schema' },
                { value: 'DocBook-Stylesheet', text: 'DocBook-Stylesheet' },
                { value: 'DocBook-XML', text: 'DocBook-XML' },
                { value: 'Dotseqn', text: 'Dotseqn' },
                { value: 'ECL-1.0', text: 'ECL-1.0' },
                { value: 'ECL-2.0', text: 'ECL-2.0' },
                { value: 'EFL-1.0', text: 'EFL-1.0' },
                { value: 'EFL-2.0', text: 'EFL-2.0' },
                { value: 'EPICS', text: 'EPICS' },
                { value: 'EPL-1.0', text: 'EPL-1.0' },
                { value: 'EPL-2.0', text: 'EPL-2.0' },
                { value: 'ESA-PL-permissive-2.4', text: 'ESA-PL-permissive-2.4' },
                { value: 'ESA-PL-strong-copyleft-2.4', text: 'ESA-PL-strong-copyleft-2.4' },
                { value: 'ESA-PL-weak-copyleft-2.4', text: 'ESA-PL-weak-copyleft-2.4' },
                { value: 'EUDatagrid', text: 'EUDatagrid' },
                { value: 'EUPL-1.0', text: 'EUPL-1.0' },
                { value: 'EUPL-1.1', text: 'EUPL-1.1' },
                { value: 'EUPL-1.2', text: 'EUPL-1.2' },
                { value: 'Elastic-2.0', text: 'Elastic-2.0' },
                { value: 'Entessa', text: 'Entessa' },
                { value: 'ErlPL-1.1', text: 'ErlPL-1.1' },
                { value: 'Eurosym', text: 'Eurosym' },
                { value: 'FBM', text: 'FBM' },
                { value: 'FDK-AAC', text: 'FDK-AAC' },
                { value: 'FDK-MPEG-H', text: 'FDK-MPEG-H' },
                { value: 'FSFAP', text: 'FSFAP' },
                { value: 'FSFAP-no-warranty-disclaimer', text: 'FSFAP-no-warranty-disclaimer' },
                { value: 'FSFUL', text: 'FSFUL' },
                { value: 'FSFULLR', text: 'FSFULLR' },
                { value: 'FSFULLRSD', text: 'FSFULLRSD' },
                { value: 'FSFULLRWD', text: 'FSFULLRWD' },
                { value: 'FSL-1.1-ALv2', text: 'FSL-1.1-ALv2' },
                { value: 'FSL-1.1-MIT', text: 'FSL-1.1-MIT' },
                { value: 'FTL', text: 'FTL' },
                { value: 'Fair', text: 'Fair' },
                { value: 'Ferguson-Twofish', text: 'Ferguson-Twofish' },
                { value: 'Frameworx-1.0', text: 'Frameworx-1.0' },
                { value: 'FreeBSD-DOC', text: 'FreeBSD-DOC' },
                { value: 'FreeImage', text: 'FreeImage' },
                { value: 'Furuseth', text: 'Furuseth' },
                { value: 'GCR-docs', text: 'GCR-docs' },
                { value: 'GD', text: 'GD' },
                { value: 'GFDL-1.1', text: 'GFDL-1.1' },
                { value: 'GFDL-1.1-invariants-only', text: 'GFDL-1.1-invariants-only' },
                { value: 'GFDL-1.1-invariants-or-later', text: 'GFDL-1.1-invariants-or-later' },
                { value: 'GFDL-1.1-no-invariants-only', text: 'GFDL-1.1-no-invariants-only' },
                { value: 'GFDL-1.1-no-invariants-or-later', text: 'GFDL-1.1-no-invariants-or-later' },
                { value: 'GFDL-1.1-only', text: 'GFDL-1.1-only' },
                { value: 'GFDL-1.1-or-later', text: 'GFDL-1.1-or-later' },
                { value: 'GFDL-1.2', text: 'GFDL-1.2' },
                { value: 'GFDL-1.2-invariants-only', text: 'GFDL-1.2-invariants-only' },
                { value: 'GFDL-1.2-invariants-or-later', text: 'GFDL-1.2-invariants-or-later' },
                { value: 'GFDL-1.2-no-invariants-only', text: 'GFDL-1.2-no-invariants-only' },
                { value: 'GFDL-1.2-no-invariants-or-later', text: 'GFDL-1.2-no-invariants-or-later' },
                { value: 'GFDL-1.2-only', text: 'GFDL-1.2-only' },
                { value: 'GFDL-1.2-or-later', text: 'GFDL-1.2-or-later' },
                { value: 'GFDL-1.3', text: 'GFDL-1.3' },
                { value: 'GFDL-1.3-invariants-only', text: 'GFDL-1.3-invariants-only' },
                { value: 'GFDL-1.3-invariants-or-later', text: 'GFDL-1.3-invariants-or-later' },
                { value: 'GFDL-1.3-no-invariants-only', text: 'GFDL-1.3-no-invariants-only' },
                { value: 'GFDL-1.3-no-invariants-or-later', text: 'GFDL-1.3-no-invariants-or-later' },
                { value: 'GFDL-1.3-only', text: 'GFDL-1.3-only' },
                { value: 'GFDL-1.3-or-later', text: 'GFDL-1.3-or-later' },
                { value: 'GL2PS', text: 'GL2PS' },
                { value: 'GLWTPL', text: 'GLWTPL' },
                { value: 'GPL-1.0', text: 'GPL-1.0' },
                { value: 'GPL-1.0-only', text: 'GPL-1.0-only' },
                { value: 'GPL-1.0-or-later', text: 'GPL-1.0-or-later' },
                { value: 'GPL-2.0', text: 'GPL-2.0' },
                { value: 'GPL-2.0-only', text: 'GPL-2.0-only' },
                { value: 'GPL-2.0-or-later', text: 'GPL-2.0-or-later' },
                { value: 'GPL-3.0', text: 'GPL-3.0' },
                { value: 'GPL-3.0-only', text: 'GPL-3.0-only' },
                { value: 'GPL-3.0-or-later', text: 'GPL-3.0-or-later' },
                { value: 'Game-Programming-Gems', text: 'Game-Programming-Gems' },
                { value: 'Giftware', text: 'Giftware' },
                { value: 'Glide', text: 'Glide' },
                { value: 'Glulxe', text: 'Glulxe' },
                { value: 'Graphics-Gems', text: 'Graphics-Gems' },
                { value: 'Gutmann', text: 'Gutmann' },
                { value: 'HDF5', text: 'HDF5' },
                { value: 'HIDAPI', text: 'HIDAPI' },
                { value: 'HP-1986', text: 'HP-1986' },
                { value: 'HP-1989', text: 'HP-1989' },
                { value: 'HPND', text: 'HPND' },
                { value: 'HPND-DEC', text: 'HPND-DEC' },
                { value: 'HPND-Fenneberg-Livingston', text: 'HPND-Fenneberg-Livingston' },
                { value: 'HPND-INRIA-IMAG', text: 'HPND-INRIA-IMAG' },
                { value: 'HPND-Intel', text: 'HPND-Intel' },
                { value: 'HPND-Kevlin-Henney', text: 'HPND-Kevlin-Henney' },
                { value: 'HPND-MIT-disclaimer', text: 'HPND-MIT-disclaimer' },
                { value: 'HPND-Markus-Kuhn', text: 'HPND-Markus-Kuhn' },
                { value: 'HPND-Netrek', text: 'HPND-Netrek' },
                { value: 'HPND-Pbmplus', text: 'HPND-Pbmplus' },
                { value: 'HPND-SMC', text: 'HPND-SMC' },
                { value: 'HPND-UC', text: 'HPND-UC' },
                { value: 'HPND-UC-export-US', text: 'HPND-UC-export-US' },
                { value: 'HPND-doc', text: 'HPND-doc' },
                { value: 'HPND-doc-sell', text: 'HPND-doc-sell' },
                { value: 'HPND-export-US', text: 'HPND-export-US' },
                { value: 'HPND-export-US-acknowledgement', text: 'HPND-export-US-acknowledgement' },
                { value: 'HPND-export-US-modify', text: 'HPND-export-US-modify' },
                { value: 'HPND-export2-US', text: 'HPND-export2-US' },
                { value: 'HPND-merchantability-variant', text: 'HPND-merchantability-variant' },
                { value: 'HPND-sell-MIT-disclaimer-xserver', text: 'HPND-sell-MIT-disclaimer-xserver' },
                { value: 'HPND-sell-regexpr', text: 'HPND-sell-regexpr' },
                { value: 'HPND-sell-variant', text: 'HPND-sell-variant' },
                { value: 'HPND-sell-variant-MIT-disclaimer', text: 'HPND-sell-variant-MIT-disclaimer' },
                { value: 'HPND-sell-variant-MIT-disclaimer-rev', text: 'HPND-sell-variant-MIT-disclaimer-rev' },
                { value: 'HPND-sell-variant-critical-systems', text: 'HPND-sell-variant-critical-systems' },
                { value: 'HTMLTIDY', text: 'HTMLTIDY' },
                { value: 'HaskellReport', text: 'HaskellReport' },
                { value: 'Hippocratic-2.1', text: 'Hippocratic-2.1' },
                { value: 'IBM-pibs', text: 'IBM-pibs' },
                { value: 'ICU', text: 'ICU' },
                { value: 'IEC-Code-Components-EULA', text: 'IEC-Code-Components-EULA' },
                { value: 'IJG', text: 'IJG' },
                { value: 'IJG-short', text: 'IJG-short' },
                { value: 'IPA', text: 'IPA' },
                { value: 'IPL-1.0', text: 'IPL-1.0' },
                { value: 'ISC', text: 'ISC' },
                { value: 'ISC-Veillard', text: 'ISC-Veillard' },
                { value: 'ISO-permission', text: 'ISO-permission' },
                { value: 'ImageMagick', text: 'ImageMagick' },
                { value: 'Imlib2', text: 'Imlib2' },
                { value: 'Info-ZIP', text: 'Info-ZIP' },
                { value: 'Informatica', text: 'Informatica' },
                { value: 'Inner-Net-2.0', text: 'Inner-Net-2.0' },
                { value: 'InnoSetup', text: 'InnoSetup' },
                { value: 'Intel', text: 'Intel' },
                { value: 'Intel-ACPI', text: 'Intel-ACPI' },
                { value: 'Interbase-1.0', text: 'Interbase-1.0' },
                { value: 'JPL-image', text: 'JPL-image' },
                { value: 'JPNIC', text: 'JPNIC' },
                { value: 'JSON', text: 'JSON' },
                { value: 'Jam', text: 'Jam' },
                { value: 'JasPer-2.0', text: 'JasPer-2.0' },
                { value: 'Kastrup', text: 'Kastrup' },
                { value: 'Kazlib', text: 'Kazlib' },
                { value: 'Knuth-CTAN', text: 'Knuth-CTAN' },
                { value: 'LAL-1.2', text: 'LAL-1.2' },
                { value: 'LAL-1.3', text: 'LAL-1.3' },
                { value: 'LGPL-2.0', text: 'LGPL-2.0' },
                { value: 'LGPL-2.0-only', text: 'LGPL-2.0-only' },
                { value: 'LGPL-2.0-or-later', text: 'LGPL-2.0-or-later' },
                { value: 'LGPL-2.1', text: 'LGPL-2.1' },
                { value: 'LGPL-2.1-only', text: 'LGPL-2.1-only' },
                { value: 'LGPL-2.1-or-later', text: 'LGPL-2.1-or-later' },
                { value: 'LGPL-3.0', text: 'LGPL-3.0' },
                { value: 'LGPL-3.0-only', text: 'LGPL-3.0-only' },
                { value: 'LGPL-3.0-or-later', text: 'LGPL-3.0-or-later' },
                { value: 'LGPLLR', text: 'LGPLLR' },
                { value: 'LOOP', text: 'LOOP' },
                { value: 'LPD-document', text: 'LPD-document' },
                { value: 'LPL-1.0', text: 'LPL-1.0' },
                { value: 'LPL-1.02', text: 'LPL-1.02' },
                { value: 'LPPL-1.0', text: 'LPPL-1.0' },
                { value: 'LPPL-1.1', text: 'LPPL-1.1' },
                { value: 'LPPL-1.2', text: 'LPPL-1.2' },
                { value: 'LPPL-1.3a', text: 'LPPL-1.3a' },
                { value: 'LPPL-1.3c', text: 'LPPL-1.3c' },
                { value: 'LZMA-SDK-9.11-to-9.20', text: 'LZMA-SDK-9.11-to-9.20' },
                { value: 'LZMA-SDK-9.22', text: 'LZMA-SDK-9.22' },
                { value: 'Latex2e', text: 'Latex2e' },
                { value: 'Latex2e-translated-notice', text: 'Latex2e-translated-notice' },
                { value: 'Leptonica', text: 'Leptonica' },
                { value: 'LiLiQ-P-1.1', text: 'LiLiQ-P-1.1' },
                { value: 'LiLiQ-R-1.1', text: 'LiLiQ-R-1.1' },
                { value: 'LiLiQ-Rplus-1.1', text: 'LiLiQ-Rplus-1.1' },
                { value: 'Libpng', text: 'Libpng' },
                { value: 'Linux-OpenIB', text: 'Linux-OpenIB' },
                { value: 'Linux-man-pages-1-para', text: 'Linux-man-pages-1-para' },
                { value: 'Linux-man-pages-copyleft', text: 'Linux-man-pages-copyleft' },
                { value: 'Linux-man-pages-copyleft-2-para', text: 'Linux-man-pages-copyleft-2-para' },
                { value: 'Linux-man-pages-copyleft-var', text: 'Linux-man-pages-copyleft-var' },
                { value: 'Lucida-Bitmap-Fonts', text: 'Lucida-Bitmap-Fonts' },
                { value: 'MIPS', text: 'MIPS' },
                { value: 'MIT', text: 'MIT' },
                { value: 'MIT-0', text: 'MIT-0' },
                { value: 'MIT-CMU', text: 'MIT-CMU' },
                { value: 'MIT-Click', text: 'MIT-Click' },
                { value: 'MIT-Festival', text: 'MIT-Festival' },
                { value: 'MIT-Khronos-old', text: 'MIT-Khronos-old' },
                { value: 'MIT-Modern-Variant', text: 'MIT-Modern-Variant' },
                { value: 'MIT-STK', text: 'MIT-STK' },
                { value: 'MIT-Wu', text: 'MIT-Wu' },
                { value: 'MIT-advertising', text: 'MIT-advertising' },
                { value: 'MIT-enna', text: 'MIT-enna' },
                { value: 'MIT-feh', text: 'MIT-feh' },
                { value: 'MIT-open-group', text: 'MIT-open-group' },
                { value: 'MIT-testregex', text: 'MIT-testregex' },
                { value: 'MITNFA', text: 'MITNFA' },
                { value: 'MMIXware', text: 'MMIXware' },
                { value: 'MMPL-1.0.1', text: 'MMPL-1.0.1' },
                { value: 'MPEG-SSG', text: 'MPEG-SSG' },
                { value: 'MPL-1.0', text: 'MPL-1.0' },
                { value: 'MPL-1.1', text: 'MPL-1.1' },
                { value: 'MPL-2.0', text: 'MPL-2.0' },
                { value: 'MPL-2.0-no-copyleft-exception', text: 'MPL-2.0-no-copyleft-exception' },
                { value: 'MS-LPL', text: 'MS-LPL' },
                { value: 'MS-PL', text: 'MS-PL' },
                { value: 'MS-RL', text: 'MS-RL' },
                { value: 'MTLL', text: 'MTLL' },
                { value: 'MVT-1.1', text: 'MVT-1.1' },
                { value: 'Mackerras-3-Clause', text: 'Mackerras-3-Clause' },
                { value: 'Mackerras-3-Clause-acknowledgment', text: 'Mackerras-3-Clause-acknowledgment' },
                { value: 'MakeIndex', text: 'MakeIndex' },
                { value: 'Martin-Birgmeier', text: 'Martin-Birgmeier' },
                { value: 'McPhee-slideshow', text: 'McPhee-slideshow' },
                { value: 'Minpack', text: 'Minpack' },
                { value: 'MirOS', text: 'MirOS' },
                { value: 'Motosoto', text: 'Motosoto' },
                { value: 'MulanPSL-1.0', text: 'MulanPSL-1.0' },
                { value: 'MulanPSL-2.0', text: 'MulanPSL-2.0' },
                { value: 'Multics', text: 'Multics' },
                { value: 'Mup', text: 'Mup' },
                { value: 'NAIST-2003', text: 'NAIST-2003' },
                { value: 'NASA-1.3', text: 'NASA-1.3' },
                { value: 'NBPL-1.0', text: 'NBPL-1.0' },
                { value: 'NCBI-PD', text: 'NCBI-PD' },
                { value: 'NCGL-UK-2.0', text: 'NCGL-UK-2.0' },
                { value: 'NCL', text: 'NCL' },
                { value: 'NCSA', text: 'NCSA' },
                { value: 'NGPL', text: 'NGPL' },
                { value: 'NICTA-1.0', text: 'NICTA-1.0' },
                { value: 'NIST-PD', text: 'NIST-PD' },
                { value: 'NIST-PD-TNT', text: 'NIST-PD-TNT' },
                { value: 'NIST-PD-fallback', text: 'NIST-PD-fallback' },
                { value: 'NIST-Software', text: 'NIST-Software' },
                { value: 'NLOD-1.0', text: 'NLOD-1.0' },
                { value: 'NLOD-2.0', text: 'NLOD-2.0' },
                { value: 'NLPL', text: 'NLPL' },
                { value: 'NOSL', text: 'NOSL' },
                { value: 'NPL-1.0', text: 'NPL-1.0' },
                { value: 'NPL-1.1', text: 'NPL-1.1' },
                { value: 'NPOSL-3.0', text: 'NPOSL-3.0' },
                { value: 'NRL', text: 'NRL' },
                { value: 'NTIA-PD', text: 'NTIA-PD' },
                { value: 'NTP', text: 'NTP' },
                { value: 'NTP-0', text: 'NTP-0' },
                { value: 'Naumen', text: 'Naumen' },
                { value: 'Net-SNMP', text: 'Net-SNMP' },
                { value: 'NetCDF', text: 'NetCDF' },
                { value: 'Newsletr', text: 'Newsletr' },
                { value: 'Nokia', text: 'Nokia' },
                { value: 'Noweb', text: 'Noweb' },
                { value: 'Nunit', text: 'Nunit' },
                { value: 'O-UDA-1.0', text: 'O-UDA-1.0' },
                { value: 'OAR', text: 'OAR' },
                { value: 'OCCT-PL', text: 'OCCT-PL' },
                { value: 'OCLC-2.0', text: 'OCLC-2.0' },
                { value: 'ODC-By-1.0', text: 'ODC-By-1.0' },
                { value: 'ODbL-1.0', text: 'ODbL-1.0' },
                { value: 'OFFIS', text: 'OFFIS' },
                { value: 'OFL-1.0', text: 'OFL-1.0' },
                { value: 'OFL-1.0-RFN', text: 'OFL-1.0-RFN' },
                { value: 'OFL-1.0-no-RFN', text: 'OFL-1.0-no-RFN' },
                { value: 'OFL-1.1', text: 'OFL-1.1' },
                { value: 'OFL-1.1-RFN', text: 'OFL-1.1-RFN' },
                { value: 'OFL-1.1-no-RFN', text: 'OFL-1.1-no-RFN' },
                { value: 'OGC-1.0', text: 'OGC-1.0' },
                { value: 'OGDL-Taiwan-1.0', text: 'OGDL-Taiwan-1.0' },
                { value: 'OGL-Canada-2.0', text: 'OGL-Canada-2.0' },
                { value: 'OGL-UK-1.0', text: 'OGL-UK-1.0' },
                { value: 'OGL-UK-2.0', text: 'OGL-UK-2.0' },
                { value: 'OGL-UK-3.0', text: 'OGL-UK-3.0' },
                { value: 'OGTSL', text: 'OGTSL' },
                { value: 'OLDAP-1.1', text: 'OLDAP-1.1' },
                { value: 'OLDAP-1.2', text: 'OLDAP-1.2' },
                { value: 'OLDAP-1.3', text: 'OLDAP-1.3' },
                { value: 'OLDAP-1.4', text: 'OLDAP-1.4' },
                { value: 'OLDAP-2.0', text: 'OLDAP-2.0' },
                { value: 'OLDAP-2.0.1', text: 'OLDAP-2.0.1' },
                { value: 'OLDAP-2.1', text: 'OLDAP-2.1' },
                { value: 'OLDAP-2.2', text: 'OLDAP-2.2' },
                { value: 'OLDAP-2.2.1', text: 'OLDAP-2.2.1' },
                { value: 'OLDAP-2.2.2', text: 'OLDAP-2.2.2' },
                { value: 'OLDAP-2.3', text: 'OLDAP-2.3' },
                { value: 'OLDAP-2.4', text: 'OLDAP-2.4' },
                { value: 'OLDAP-2.5', text: 'OLDAP-2.5' },
                { value: 'OLDAP-2.6', text: 'OLDAP-2.6' },
                { value: 'OLDAP-2.7', text: 'OLDAP-2.7' },
                { value: 'OLDAP-2.8', text: 'OLDAP-2.8' },
                { value: 'OLFL-1.3', text: 'OLFL-1.3' },
                { value: 'OML', text: 'OML' },
                { value: 'OPL-1.0', text: 'OPL-1.0' },
                { value: 'OPL-UK-3.0', text: 'OPL-UK-3.0' },
                { value: 'OPUBL-1.0', text: 'OPUBL-1.0' },
                { value: 'OSC-1.0', text: 'OSC-1.0' },
                { value: 'OSET-PL-2.1', text: 'OSET-PL-2.1' },
                { value: 'OSL-1.0', text: 'OSL-1.0' },
                { value: 'OSL-1.1', text: 'OSL-1.1' },
                { value: 'OSL-2.0', text: 'OSL-2.0' },
                { value: 'OSL-2.1', text: 'OSL-2.1' },
                { value: 'OSL-3.0', text: 'OSL-3.0' },
                { value: 'OSSP', text: 'OSSP' },
                { value: 'OpenMDW-1.0', text: 'OpenMDW-1.0' },
                { value: 'OpenPBS-2.3', text: 'OpenPBS-2.3' },
                { value: 'OpenSSL', text: 'OpenSSL' },
                { value: 'OpenSSL-standalone', text: 'OpenSSL-standalone' },
                { value: 'OpenVision', text: 'OpenVision' },
                { value: 'PADL', text: 'PADL' },
                { value: 'PDDL-1.0', text: 'PDDL-1.0' },
                { value: 'PHP-3.0', text: 'PHP-3.0' },
                { value: 'PHP-3.01', text: 'PHP-3.01' },
                { value: 'PPL', text: 'PPL' },
                { value: 'PSF-2.0', text: 'PSF-2.0' },
                { value: 'ParaType-Free-Font-1.3', text: 'ParaType-Free-Font-1.3' },
                { value: 'Parity-6.0.0', text: 'Parity-6.0.0' },
                { value: 'Parity-7.0.0', text: 'Parity-7.0.0' },
                { value: 'Pixar', text: 'Pixar' },
                { value: 'Plexus', text: 'Plexus' },
                { value: 'PolyForm-Noncommercial-1.0.0', text: 'PolyForm-Noncommercial-1.0.0' },
                { value: 'PolyForm-Small-Business-1.0.0', text: 'PolyForm-Small-Business-1.0.0' },
                { value: 'PostgreSQL', text: 'PostgreSQL' },
                { value: 'Python-2.0', text: 'Python-2.0' },
                { value: 'Python-2.0.1', text: 'Python-2.0.1' },
                { value: 'QPL-1.0', text: 'QPL-1.0' },
                { value: 'QPL-1.0-INRIA-2004', text: 'QPL-1.0-INRIA-2004' },
                { value: 'Qhull', text: 'Qhull' },
                { value: 'RHeCos-1.1', text: 'RHeCos-1.1' },
                { value: 'RPL-1.1', text: 'RPL-1.1' },
                { value: 'RPL-1.5', text: 'RPL-1.5' },
                { value: 'RPSL-1.0', text: 'RPSL-1.0' },
                { value: 'RSA-MD', text: 'RSA-MD' },
                { value: 'RSCPL', text: 'RSCPL' },
                { value: 'Rdisc', text: 'Rdisc' },
                { value: 'Ruby', text: 'Ruby' },
                { value: 'Ruby-pty', text: 'Ruby-pty' },
                { value: 'SAX-PD', text: 'SAX-PD' },
                { value: 'SAX-PD-2.0', text: 'SAX-PD-2.0' },
                { value: 'SCEA', text: 'SCEA' },
                { value: 'SGI-B-1.0', text: 'SGI-B-1.0' },
                { value: 'SGI-B-1.1', text: 'SGI-B-1.1' },
                { value: 'SGI-B-2.0', text: 'SGI-B-2.0' },
                { value: 'SGI-OpenGL', text: 'SGI-OpenGL' },
                { value: 'SGMLUG-PM', text: 'SGMLUG-PM' },
                { value: 'SGP4', text: 'SGP4' },
                { value: 'SHL-0.5', text: 'SHL-0.5' },
                { value: 'SHL-0.51', text: 'SHL-0.51' },
                { value: 'SISSL', text: 'SISSL' },
                { value: 'SISSL-1.2', text: 'SISSL-1.2' },
                { value: 'SL', text: 'SL' },
                { value: 'SMAIL-GPL', text: 'SMAIL-GPL' },
                { value: 'SMLNJ', text: 'SMLNJ' },
                { value: 'SMPPL', text: 'SMPPL' },
                { value: 'SNIA', text: 'SNIA' },
                { value: 'SOFA', text: 'SOFA' },
                { value: 'SPL-1.0', text: 'SPL-1.0' },
                { value: 'SSH-OpenSSH', text: 'SSH-OpenSSH' },
                { value: 'SSH-short', text: 'SSH-short' },
                { value: 'SSLeay-standalone', text: 'SSLeay-standalone' },
                { value: 'SSPL-1.0', text: 'SSPL-1.0' },
                { value: 'SUL-1.0', text: 'SUL-1.0' },
                { value: 'SWL', text: 'SWL' },
                { value: 'Saxpath', text: 'Saxpath' },
                { value: 'SchemeReport', text: 'SchemeReport' },
                { value: 'Sendmail', text: 'Sendmail' },
                { value: 'Sendmail-8.23', text: 'Sendmail-8.23' },
                { value: 'Sendmail-Open-Source-1.1', text: 'Sendmail-Open-Source-1.1' },
                { value: 'SimPL-2.0', text: 'SimPL-2.0' },
                { value: 'Sleepycat', text: 'Sleepycat' },
                { value: 'Soundex', text: 'Soundex' },
                { value: 'Spencer-86', text: 'Spencer-86' },
                { value: 'Spencer-94', text: 'Spencer-94' },
                { value: 'Spencer-99', text: 'Spencer-99' },
                { value: 'SugarCRM-1.1.3', text: 'SugarCRM-1.1.3' },
                { value: 'Sun-PPP', text: 'Sun-PPP' },
                { value: 'Sun-PPP-2000', text: 'Sun-PPP-2000' },
                { value: 'SunPro', text: 'SunPro' },
                { value: 'Symlinks', text: 'Symlinks' },
                { value: 'TAPR-OHL-1.0', text: 'TAPR-OHL-1.0' },
                { value: 'TCL', text: 'TCL' },
                { value: 'TCP-wrappers', text: 'TCP-wrappers' },
                { value: 'TGPPL-1.0', text: 'TGPPL-1.0' },
                { value: 'TMate', text: 'TMate' },
                { value: 'TORQUE-1.1', text: 'TORQUE-1.1' },
                { value: 'TOSL', text: 'TOSL' },
                { value: 'TPDL', text: 'TPDL' },
                { value: 'TPL-1.0', text: 'TPL-1.0' },
                { value: 'TTWL', text: 'TTWL' },
                { value: 'TTYP0', text: 'TTYP0' },
                { value: 'TU-Berlin-1.0', text: 'TU-Berlin-1.0' },
                { value: 'TU-Berlin-2.0', text: 'TU-Berlin-2.0' },
                { value: 'TekHVC', text: 'TekHVC' },
                { value: 'TermReadKey', text: 'TermReadKey' },
                { value: 'ThirdEye', text: 'ThirdEye' },
                { value: 'TrustedQSL', text: 'TrustedQSL' },
                { value: 'UCAR', text: 'UCAR' },
                { value: 'UCL-1.0', text: 'UCL-1.0' },
                { value: 'UMich-Merit', text: 'UMich-Merit' },
                { value: 'UPL-1.0', text: 'UPL-1.0' },
                { value: 'URT-RLE', text: 'URT-RLE' },
                { value: 'Ubuntu-font-1.0', text: 'Ubuntu-font-1.0' },
                { value: 'UnRAR', text: 'UnRAR' },
                { value: 'Unicode-3.0', text: 'Unicode-3.0' },
                { value: 'Unicode-DFS-2015', text: 'Unicode-DFS-2015' },
                { value: 'Unicode-DFS-2016', text: 'Unicode-DFS-2016' },
                { value: 'Unicode-TOU', text: 'Unicode-TOU' },
                { value: 'UnixCrypt', text: 'UnixCrypt' },
                { value: 'Unlicense', text: 'Unlicense' },
                { value: 'Unlicense-libtelnet', text: 'Unlicense-libtelnet' },
                { value: 'Unlicense-libwhirlpool', text: 'Unlicense-libwhirlpool' },
                { value: 'VOSTROM', text: 'VOSTROM' },
                { value: 'VSL-1.0', text: 'VSL-1.0' },
                { value: 'Vim', text: 'Vim' },
                { value: 'Vixie-Cron', text: 'Vixie-Cron' },
                { value: 'W3C', text: 'W3C' },
                { value: 'W3C-19980720', text: 'W3C-19980720' },
                { value: 'W3C-20150513', text: 'W3C-20150513' },
                { value: 'WTFNMFPL', text: 'WTFNMFPL' },
                { value: 'WTFPL', text: 'WTFPL' },
                { value: 'Watcom-1.0', text: 'Watcom-1.0' },
                { value: 'Widget-Workshop', text: 'Widget-Workshop' },
                { value: 'WordNet', text: 'WordNet' },
                { value: 'Wsuipa', text: 'Wsuipa' },
                { value: 'X11', text: 'X11' },
                { value: 'X11-distribute-modifications-variant', text: 'X11-distribute-modifications-variant' },
                { value: 'X11-no-permit-persons', text: 'X11-no-permit-persons' },
                { value: 'X11-swapped', text: 'X11-swapped' },
                { value: 'XFree86-1.1', text: 'XFree86-1.1' },
                { value: 'XSkat', text: 'XSkat' },
                { value: 'Xdebug-1.03', text: 'Xdebug-1.03' },
                { value: 'Xerox', text: 'Xerox' },
                { value: 'Xfig', text: 'Xfig' },
                { value: 'Xnet', text: 'Xnet' },
                { value: 'YPL-1.0', text: 'YPL-1.0' },
                { value: 'YPL-1.1', text: 'YPL-1.1' },
                { value: 'ZPL-1.1', text: 'ZPL-1.1' },
                { value: 'ZPL-2.0', text: 'ZPL-2.0' },
                { value: 'ZPL-2.1', text: 'ZPL-2.1' },
                { value: 'Zed', text: 'Zed' },
                { value: 'Zeeff', text: 'Zeeff' },
                { value: 'Zend-2.0', text: 'Zend-2.0' },
                { value: 'Zimbra-1.3', text: 'Zimbra-1.3' },
                { value: 'Zimbra-1.4', text: 'Zimbra-1.4' },
                { value: 'Zlib', text: 'Zlib' },
                { value: 'any-OSI', text: 'any-OSI' },
                { value: 'any-OSI-perl-modules', text: 'any-OSI-perl-modules' },
                { value: 'atc-game', text: 'atc-game' },
                { value: 'bcrypt-Solar-Designer', text: 'bcrypt-Solar-Designer' },
                { value: 'blessing', text: 'blessing' },
                { value: 'bzip2-1.0.5', text: 'bzip2-1.0.5' },
                { value: 'bzip2-1.0.6', text: 'bzip2-1.0.6' },
                { value: 'check-cvs', text: 'check-cvs' },
                { value: 'checkmk', text: 'checkmk' },
                { value: 'copyleft-next-0.3.0', text: 'copyleft-next-0.3.0' },
                { value: 'copyleft-next-0.3.1', text: 'copyleft-next-0.3.1' },
                { value: 'curl', text: 'curl' },
                { value: 'cve-tou', text: 'cve-tou' },
                { value: 'diffmark', text: 'diffmark' },
                { value: 'dtoa', text: 'dtoa' },
                { value: 'dvipdfm', text: 'dvipdfm' },
                { value: 'eGenix', text: 'eGenix' },
                { value: 'etalab-2.0', text: 'etalab-2.0' },
                { value: 'fwlw', text: 'fwlw' },
                { value: 'gSOAP-1.3b', text: 'gSOAP-1.3b' },
                { value: 'generic-xts', text: 'generic-xts' },
                { value: 'gnuplot', text: 'gnuplot' },
                { value: 'gtkbook', text: 'gtkbook' },
                { value: 'hdparm', text: 'hdparm' },
                { value: 'hyphen-bulgarian', text: 'hyphen-bulgarian' },
                { value: 'iMatix', text: 'iMatix' },
                { value: 'jove', text: 'jove' },
                { value: 'libpng-1.6.35', text: 'libpng-1.6.35' },
                { value: 'libpng-2.0', text: 'libpng-2.0' },
                { value: 'libselinux-1.0', text: 'libselinux-1.0' },
                { value: 'libtiff', text: 'libtiff' },
                { value: 'libutil-David-Nugent', text: 'libutil-David-Nugent' },
                { value: 'lsof', text: 'lsof' },
                { value: 'magaz', text: 'magaz' },
                { value: 'mailprio', text: 'mailprio' },
                { value: 'man2html', text: 'man2html' },
                { value: 'metamail', text: 'metamail' },
                { value: 'mpi-permissive', text: 'mpi-permissive' },
                { value: 'mpich2', text: 'mpich2' },
                { value: 'mplus', text: 'mplus' },
                { value: 'ngrep', text: 'ngrep' },
                { value: 'pkgconf', text: 'pkgconf' },
                { value: 'pnmstitch', text: 'pnmstitch' },
                { value: 'psfrag', text: 'psfrag' },
                { value: 'psutils', text: 'psutils' },
                { value: 'python-ldap', text: 'python-ldap' },
                { value: 'radvd', text: 'radvd' },
                { value: 'snprintf', text: 'snprintf' },
                { value: 'softSurfer', text: 'softSurfer' },
                { value: 'ssh-keyscan', text: 'ssh-keyscan' },
                { value: 'swrule', text: 'swrule' },
                { value: 'threeparttable', text: 'threeparttable' },
                { value: 'ulem', text: 'ulem' },
                { value: 'w3m', text: 'w3m' },
                { value: 'wwl', text: 'wwl' },
                { value: 'xinetd', text: 'xinetd' },
                { value: 'xkeyboard-config-Zinoviev', text: 'xkeyboard-config-Zinoviev' },
                { value: 'xlock', text: 'xlock' },
                { value: 'xpp', text: 'xpp' },
                { value: 'xzoom', text: 'xzoom' },
                { value: 'zlib-acknowledgement', text: 'zlib-acknowledgement' }
            ];

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
    .controller('OrcidCallbackController', [
        '$scope',
        '$state',
        'djangoAuth',
        '$location',
        'OrcidAuth',
        function ($scope, $state, djangoAuth, $location, OrcidAuth) {
            var code = $location.search().code;
            const stateParams = $location.search().state;

            const stateCheck = OrcidAuth.consumeState(stateParams);
            if (!stateCheck.ok) {
                $scope.loginErrors = 'ORCID authentication failed: invalid state parameter';
                return;
            }

            function goAfterAuth() {
                if (stateCheck.payload && stateCheck.payload.name) {
                    $state.go(stateCheck.payload.name, stateCheck.payload.params || {});
                } else {
                    $state.go('search');
                }
            }

            // if user is authenticated call djangoAuth.orcidConnect
            if (djangoAuth.authenticated) {
                djangoAuth.orcidConnect(code).then(
                    function () {
                        $state.go('profile');
                    },
                    function () {
                        $scope.loginErrors = 'ORCID connection failed';
                    }
                );
            } else {
                djangoAuth.orcidLogin(code).then(
                    function () {
                        goAfterAuth();
                    },
                    function () {
                        var error_description = $location.search().error_description;
                        $scope.loginErrors = error_description || 'ORCID login failed';
                    }
                );
            }
        },
    ])
    .controller('LoginController', [
        '$scope',
        '$state',
        'djangoAuth',
        '$rootScope',
        'OrcidAuth',
        function ($scope, $state, djangoAuth, $rootScope, OrcidAuth) {
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

            $scope.orcidLoginButtonClick = function () {
                OrcidAuth.start();
            };
        },
    ])
    .controller('SignupController', [
        '$scope',
        '$state',
        'djangoAuth',
        '$rootScope',
        '$timeout',
        'OrcidAuth',
        function ($scope, $state, djangoAuth, $rootScope, $timeout, OrcidAuth) {
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

            $scope.orcidSignupButtonClick = function () {
                OrcidAuth.start();
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
