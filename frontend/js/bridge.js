'use strict';

/* GitHub metadata bridge service */

angular
    .module('elixir_front.bridge', [])
    .factory('Bridge', [
        '$http',
        function ($http) {
            // fields the bridge may never touch
            var BRIDGE_FORBIDDEN = [
                'biotoolsID',
                'owner',
                'additionDate',
                'lastUpdate',
                'validated',
                'homepage_status',
                'elixir_badge',
                'editPermission',
            ];

            // registry of fields the bridge may suggest: how to compare, label and merge them
            var BRIDGE_FIELD_DEFS = [
                // Summary
                { key: 'name', label: 'Tool name', kind: 'scalar', tab: 'Summary' },
                { key: 'description', label: 'Description', kind: 'scalar', tab: 'Summary' },
                { key: 'homepage', label: 'Homepage', kind: 'scalar', tab: 'Summary' },
                {
                    key: 'version', label: 'Version(s)', kind: 'list', tab: 'Summary',
                    dedupeKey: function (v) { return String(v); },
                    itemLabel: function (v) { return String(v); },
                },
                // Labels
                { key: 'license', label: 'License', kind: 'scalar', tab: 'Labels' },
                {
                    key: 'collectionID', label: 'Collection', kind: 'list', tab: 'Labels',
                    dedupeKey: function (v) { return v; },
                    itemLabel: function (v) { return v; },
                },
                {
                    key: 'topic', label: 'Topic', kind: 'list', tab: 'Labels',
                    dedupeKey: function (v) { return v.uri; },
                    itemLabel: function (v) { return v.term; },
                },
                {
                    key: 'operatingSystem', label: 'Platform (OS)', kind: 'list', tab: 'Labels',
                    dedupeKey: function (v) { return v; },
                    itemLabel: function (v) { return v; },
                },
                {
                    key: 'language', label: 'Language', kind: 'list', tab: 'Labels',
                    dedupeKey: function (v) { return v; },
                    itemLabel: function (v) { return v; },
                },
                // Function: whole blocks are the unit of comparison;
                // the label summarises operations, inputs and outputs
                {
                    key: 'function', label: 'Function', kind: 'list', tab: 'Function',
                    dedupeKey: function (v) {
                        // same operations = same function for dedupe purposes
                        var ops = (v.operation || []).map(function (op) { return op.uri; }).sort().join(',');
                        return ops;
                    },
                    itemLabel: function (v) { return functionBlockLabel(v); },
                },
                // Links / Download / Documentation
                {
                    key: 'link', label: 'Links', kind: 'list', tab: 'Links',
                    dedupeKey: function (v) { return ((v.type && v.type[0]) || '') + '|' + (v.url || ''); },
                    itemLabel: function (v) {
                        return ((v.type && v.type[0]) || v.type || 'Other') + ' — ' + (v.url || '');
                    },
                },
                {
                    key: 'download', label: 'Downloads', kind: 'list', tab: 'Download',
                    dedupeKey: function (v) { return ((v.type && v.type[0]) || '') + '|' + (v.url || ''); },
                    itemLabel: function (v) {
                        return ((v.type && v.type[0]) || v.type || 'Other') + ' — ' + (v.url || '');
                    },
                },
                {
                    key: 'documentation', label: 'Documentation', kind: 'list', tab: 'Documentation',
                    dedupeKey: function (v) { return ((v.type && v.type[0]) || '') + '|' + (v.url || ''); },
                    itemLabel: function (v) {
                        return ((v.type && v.type[0]) || v.type || 'Other') + ' — ' + (v.url || '');
                    },
                },
                // Publications
                {
                    key: 'publication', label: 'Publications', kind: 'list', tab: 'Publications',
                    dedupeKey: function (v) { return (v.doi || '') + '|' + (v.pmid || '') + '|' + (v.pmcid || ''); },
                    itemLabel: function (v) {
                        var id = v.doi || v.pmid || v.pmcid || '?';
                        return (v.type && v.type[0] || 'Other') + ' — ' + id;
                    },
                },
                // Credits
                {
                    key: 'credit', label: 'Credits', kind: 'list', tab: 'Credits',
                    dedupeKey: function (v) { return (v.name || '') + '|' + (v.typeEntity || ''); },
                    itemLabel: function (v) { return (v.name || '?') + ' (' + (v.typeEntity || '?') + ')'; },
                },
            ];

            function isGithubUrl(url) {
                return /github\.com\/[^\/]+\/[^\/]+/.test(url || '');
            }
            
            // readable one-line summary of a function block:
            // operations, plus inputs/outputs when present
            function functionBlockLabel(fn) {
                if (!fn) return '(empty function)';
                var parts = [];

                var ops = (fn.operation || []).map(function (op) { return op.term || op.uri; });
                if (ops.length) parts.push('Operations: ' + ops.join(', '));

                var inputs = [];
                (fn.input || []).forEach(function (inp) {
                    if (inp.data && (inp.data.term || inp.data.uri)) {
                        inputs.push(inp.data.term || inp.data.uri);
                    }
                });
                if (inputs.length) parts.push('Inputs: ' + inputs.join(', '));

                var outputs = [];
                (fn.output || []).forEach(function (out) {
                    if (out.data && (out.data.term || out.data.uri)) {
                        outputs.push(out.data.term || out.data.uri);
                    }
                });
                if (outputs.length) parts.push('Outputs: ' + outputs.join(', '));

                return parts.length ? parts.join(' · ') : '(unnamed function)';
            }

            // build choice objects comparing bridge output with current values
            function buildChoices(bridgeData, software) {
                var choices = [];

                BRIDGE_FIELD_DEFS.forEach(function (def) {
                    if (BRIDGE_FORBIDDEN.indexOf(def.key) !== -1) return;
                    if (!(def.key in bridgeData)) return;
                    var suggested = bridgeData[def.key];
                    if (suggested === undefined || suggested === null) return;

                    if (def.kind === 'scalar') {
                        var current = software ? software[def.key] : undefined;
                        choices.push({
                            field: def.key, label: def.label, kind: 'scalar', tab: def.tab,
                            current: current || '',
                            suggested: suggested,
                            // empty current value: replace as default
                            action: current ? 'keep' : 'replace',
                        });
                    } else {
                        var currentList = Array.isArray(software && software[def.key]) ? software[def.key] : [];
                        var suggestedList = Array.isArray(suggested) ? suggested : [suggested];

                        // build merged item list, deduplicating exact matches
                        var seen = {};
                        var items = [];
                        currentList.forEach(function (item) {
                            seen[def.dedupeKey(item)] = true;
                            items.push({ source: 'current', item: item, checked: true, duplicate: false });
                        });
                        suggestedList.forEach(function (item) {
                            var k = def.dedupeKey(item);
                            var dup = !!seen[k];
                            if (!dup) seen[k] = true;
                            items.push({ source: 'suggested', item: item, checked: !dup, duplicate: dup });
                        });

                        choices.push({
                            field: def.key, label: def.label, kind: 'list', tab: def.tab,
                            current: currentList,
                            suggested: suggestedList,
                            items: items,
                            itemLabel: def.itemLabel,
                            // protect curated data on edit
                            action: currentList.length ? 'keep' : 'replace',
                        });
                    }
                });

                return choices;
            }

            // re-sync the "current" side of the choices with the live
            // software model, preserving the user's selections; called when
            // the review tab is shown so edits made in other tabs are reflected
            function syncChoices(choices, software) {
                var defsByKey = {};
                BRIDGE_FIELD_DEFS.forEach(function (def) {
                    defsByKey[def.key] = def;
                });

                choices.forEach(function (choice) {
                    var def = defsByKey[choice.field];
                    if (!def) return;

                    if (def.kind === 'scalar') {
                        choice.current = (software && software[def.key]) || '';
                        return;
                    }

                    var currentList = Array.isArray(software && software[def.key])
                        ? software[def.key]
                        : [];

                    // remember the user's checkbox state by dedupe key so it
                    // survives the rebuild for items that still exist
                    var previous = {};
                    choice.items.forEach(function (i) {
                        previous[def.dedupeKey(i.item)] = i.checked;
                    });

                    var seen = {};
                    var items = [];
                    currentList.forEach(function (item) {
                        var k = def.dedupeKey(item);
                        seen[k] = true;
                        items.push({
                            source: 'current',
                            item: item,
                            checked: k in previous ? previous[k] : true,
                            duplicate: false,
                        });
                    });
                    choice.suggested.forEach(function (item) {
                        var k = def.dedupeKey(item);
                        var dup = !!seen[k];
                        if (!dup) seen[k] = true;
                        items.push({
                            source: 'suggested',
                            item: item,
                            checked: k in previous ? previous[k] : !dup,
                            duplicate: dup,
                        });
                    });

                    choice.current = currentList;
                    choice.items = items;
                });

                return choices;
            }

            // apply the user's choices onto the software model
            function applyChoices(choices, software) {
                var applied = 0;
                choices.forEach(function (choice) {
                    if (choice.kind === 'scalar') {
                        if (choice.action === 'replace') {
                            software[choice.field] = choice.suggested;
                            applied++;
                        }
                        return;
                    }
                    // list fields: every action is a checkbox selection now
                    var isDefault;
                    if (choice.action === 'keep') {
                        // default keep = all current items checked, no suggested
                        isDefault = choice.items.every(function (i) {
                            return i.checked === (i.source === 'current' || i.duplicate);
                        });
                    } else if (choice.action === 'replace') {
                        // default replace = all suggested items checked, no current
                        isDefault = choice.items.every(function (i) {
                            return i.checked === (i.source === 'suggested' || i.duplicate);
                        });
                    }
                    if (choice.action == 'keep' && isDefault) {
                        return; // unchanged from the default for this action
                    }

                    var merged = choice.items
                        .filter(function (i) { return i.checked; })
                        .map(function (i) { return i.item; });
                    applied++;
                    if (merged.length) {
                        software[choice.field] = merged;
                    } else {
                        delete software[choice.field];
                    }
                });
                return applied;
            }

            // internal: process bridge data into choices and store them for
            function processResults(bridge, software, data) {
                // the bridge may return the tool entry as a JSON string
                if (typeof data === 'string') {
                    try {
                        data = JSON.parse(data);
                    } catch (e) {
                        bridge.inProgress = false;
                        bridge.message = 'The bridge returned data that could not be parsed.';
                        return;
                    }
                }
                bridge.raw = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                bridge.inProgress = false;

                // gather choices and keep them in shared state so the
                // review tab can render them; they persist until the
                // user applies or discards them or runs the bridge again
                var choices = buildChoices(data, software);
                if (!choices.length) {
                    bridge.choices = null;
                    bridge.message = 'The bridge returned no suggestions to review.';
                    return;
                }
                bridge.choices = choices;
                bridge.message =
                    'Bridge results ready — review them in the "GitHub Bridge" tab.';
                bridge.active = true;
            }

            // run the bridge, store the choices for review in the bridge tab
            function run(bridge, software, biotoolsID, onMessage) {
                var match = (bridge.url || '').match(/github\.com\/([^\/]+)\/([^\/]+)/);

                if (!match) {
                    alert('Invalid GitHub URL. Please provide a valid GitHub repository URL.');
                    return;
                }
                var owner = match[1];
                var repo = match[2].replace(/\.git$/, ''); // Remove .git if present

                var params = {
                    owner: owner,
                    repo: repo,
                };

                if (biotoolsID) {
                    params.biotoolsID = biotoolsID;
                }

                bridge.inProgress = true;
                bridge.message = null;

                return $http.post('/github-to-biotools', params).then(
                    function (response) {
                        processResults(bridge, software, response.data);
                    },
                    function (response) {
                        bridge.inProgress = false;
                        alert(
                            'Bridge failed: ' +
                                (response.data && response.data.detail
                                    ? response.data.detail
                                    : 'Unknown error')
                        );
                    }
                );
            }

            // discard the current bridge results
            function discard(bridge) {
                bridge.choices = null;
                bridge.active = false;
                bridge.message = 'Bridge results discarded.';
            }

            // apply the currently selected choices and clear the results
            function apply(bridge, software) {
                if (!bridge.choices) return 0;
                var applied = applyChoices(bridge.choices, software);
                bridge.choices = null;
                bridge.active = false;
                bridge.message = 'Applied ' + applied + ' field(s) from GitHub.';
                return applied;
            }

            return {
                isGithubUrl: isGithubUrl,
                buildChoices: buildChoices,
                applyChoices: applyChoices,
                sync: syncChoices,
                run: run,
                apply: apply,
                discard: discard,
            };
        },
    ])
    .controller('BridgeReviewCtrl', [
        '$scope',
        '$uibModal',
        'Bridge',
        function ($scope, $uibModal, Bridge) {
            var vm = this;

            // (re)build choice groups by tab, preserving registry order;
            // rebuilt whenever bridge.choices changes (the tab content is
            // rendered before the bridge has run, so groups must react)
            $scope.$watch(
                function () {
                    return $scope.bridge.choices;
                },
                function (choices) {
                    vm.groups = [];
                    var groupIndex = {};
                    (choices || []).forEach(function (choice) {
                        if (!groupIndex[choice.tab]) {
                            groupIndex[choice.tab] = { label: choice.tab, choices: [] };
                            vm.groups.push(groupIndex[choice.tab]);
                        }
                        groupIndex[choice.tab].choices.push(choice);
                    });
                }
            );

            // when the review tab becomes active, refresh the "current"
            // side of the choices against the live software model so edits
            // made in the other tabs are reflected here (selections survive)
            $scope.$watch('bridge.active', function (active) {
                if (active && $scope.bridge.choices && $scope.software) {
                    Bridge.sync($scope.bridge.choices, $scope.software);
                }
            });

            vm.keepAll = function () {
                ($scope.bridge.choices || []).forEach(function (choice) {
                    choice.action = 'keep';
                });
            };

            // compute a preview object of the fields that would change
            // and their new values, used by the confirmation modal
            vm.getChanges = function () {
                var changes = {};
                ($scope.bridge.choices || []).forEach(function (choice) {
                    var value;
                    if (choice.kind === 'scalar') {
                        if (choice.action !== 'replace') return; // keep
                        value = choice.suggested;
                    } else {
                        if (choice.action === 'keep') {
                            // keep is only a change if checkboxes deviate
                            var isDefault = choice.items.every(function (i) {
                                return i.checked === (i.source === 'current' || i.duplicate);
                            });
                            if (isDefault) return;
                        }
                        value = choice.items
                            .filter(function (i) { return i.checked; })
                            .map(function (i) { return i.item; });
                    }
                    changes[choice.field] = value;
                });
                return changes;
            };

            vm.apply = function () {
                var changes = vm.getChanges();
                if (!Object.keys(changes).length) {
                    Bridge.apply($scope.bridge, $scope.software);
                    return;
                }

                var modalInstance = $uibModal.open({
                    templateUrl: 'partials/tool_edit/toolEditBridgeConfirm.html',
                    controllerAs: 'vm',
                    size: 'lg',
                    controller: [
                        '$uibModalInstance',
                        'changes',
                        function ($uibModalInstance, changes) {
                            var vm = this;
                            vm.changesJson = angular.toJson(changes, 2);
                            vm.count = Object.keys(changes).length;
                            vm.confirm = function () {
                                $uibModalInstance.close(true);
                            };
                            vm.cancel = function () {
                                $uibModalInstance.dismiss('cancel');
                            };
                        },
                    ],
                    resolve: {
                        changes: function () {
                            return changes;
                        },
                    },
                });

                modalInstance.result.then(
                    function () {
                        Bridge.apply($scope.bridge, $scope.software);
                    },
                    function () {
                        // dismissed — do not apply
                    }
                );
            };

            vm.discard = function () {
                Bridge.discard($scope.bridge);
            };

            vm.hasChanges = function (group) {
                return group.choices.some(function (c) {
                    return c.action !== 'keep';
                });
            };

            // reset checkbox selections to the defaults of the chosen action;
            // called when a list field's radio changes
            vm.actionChanged = function (choice) {
                choice.items.forEach(function (i) {
                    if (choice.action === 'keep') {
                        i.checked = i.source === 'current' || i.duplicate;
                    } else if (choice.action === 'replace') {
                        i.checked = i.source === 'suggested' || i.duplicate;
                    }
                    // merge: leave the user's current selection untouched
                });
            };

            // a readable preview of what a choice will produce
            vm.getResult = function (choice) {
                if (choice.kind === 'scalar') {
                    return choice.action === 'replace' ? choice.suggested : choice.current;
                }
                return choice.items
                    .filter(function (i) { return i.checked; })
                    .map(function (i) { return i.item; });
            };
        },
    ]);
