// PermissionsController w/ self-contained user picker
angular
    .module('elixir_front.controllers')
    .controller('PermissionsController', [
        '$scope',
        '$http',
        'User',
        function ($scope, $http, User) {
            $scope.User = User;

            // ---------------------------------------------------------------
            // Edit permission model handling
            // ---------------------------------------------------------------

            // Make sure a usable editPermission object always exists.
            // ToolEditController's initializePermissions() deletes it for
            // non-owners (e.g. superusers), so guard against that here.
            function ensureEditPermission() {
                if (!$scope.software) {
                    $scope.software = {};
                }
                if (!$scope.software.editPermission) {
                    $scope.software.editPermission = { type: 'private', authors: [] };
                }
                if (!$scope.software.editPermission.authors) {
                    $scope.software.editPermission.authors = [];
                }
            }
            ensureEditPermission();

            // Re-check whenever the software object is replaced from the API
            // (e.g. tool data arrives after the tab was already rendered).
            $scope.$watch('software.editPermission', function (newVal) {
                if (newVal === undefined) {
                    ensureEditPermission();
                }
            });

            $scope.setPermissionType = function (type) {
                ensureEditPermission();
                $scope.software.editPermission.type = type;
            };

            $scope.removeAuthor = function (index) {
                ensureEditPermission();
                $scope.software.editPermission.authors.splice(index, 1);
            };

            $scope.isSoftwareOwner = function () {
                return $scope.software && $scope.software.owner === User.getUsername();
            };

            // ---------------------------------------------------------------
            // User search / picker
            // ---------------------------------------------------------------

            $scope.userSearch = {
                query: '',
                results: [],
                loading: false,
                error: false,
                showDropdown: false,
                highlighted: -1,
            };

            var searchRequest = null;

            $scope.searchUsers = function () {
                var query = ($scope.userSearch.query || '').trim();

                if (query.length < 2) {
                    $scope.userSearch.results = [];
                    $scope.userSearch.showDropdown = false;
                    $scope.userSearch.highlighted = -1;
                    return;
                }

                $scope.userSearch.loading = true;
                $scope.userSearch.error = false;

                // Abort any in-flight request so stale responses can't
                // overwrite fresh ones.
                if (searchRequest) {
                    searchRequest.resolve();
                }

                var canceler = ($scope.userSearch._canceler =
                    $scope.userSearch._canceler || null);
                searchRequest = null;

                $http
                    .get('/api/user-list', { params: { term: query } })
                    .then(
                        function (response) {
                            // Ignore stale responses
                            if ($scope.userSearch.query.trim() !== query) {
                                return;
                            }
                            $scope.userSearch.loading = false;
                            var authors =
                                $scope.software.editPermission &&
                                $scope.software.editPermission.authors;
                            var excluded = authors || [];
                            $scope.userSearch.results = _
                                .map(response.data, function (obj) {
                                    return obj.username;
                                })
                                .filter(function (username) {
                                    return excluded.indexOf(username) === -1;
                                })
                                .slice(0, 10);
                            $scope.userSearch.showDropdown =
                                $scope.userSearch.results.length > 0;
                            $scope.userSearch.highlighted =
                                $scope.userSearch.results.length > 0 ? 0 : -1;
                        },
                        function () {
                            $scope.userSearch.loading = false;
                            $scope.userSearch.error = true;
                            $scope.userSearch.results = [];
                            $scope.userSearch.showDropdown = false;
                        }
                    );
            };

            $scope.selectUser = function (username) {
                if (!username) {
                    return;
                }
                ensureEditPermission();

                if ($scope.software.editPermission.authors.indexOf(username) === -1) {
                    $scope.software.editPermission.authors.push(username);
                }

                // Reset the search box.
                $scope.userSearch.query = '';
                $scope.userSearch.results = [];
                $scope.userSearch.showDropdown = false;
                $scope.userSearch.highlighted = -1;
            };

            // Keyboard navigation: arrow up/down + enter, escape closes.
            $scope.userSearchKeydown = function ($event) {
                var s = $scope.userSearch;

                switch ($event.keyCode) {
                    case 40: // down
                        if (s.results.length) {
                            s.highlighted = (s.highlighted + 1) % s.results.length;
                            $event.preventDefault();
                        }
                        break;
                    case 38: // up
                        if (s.results.length) {
                            s.highlighted =
                                s.highlighted <= 0
                                    ? s.results.length - 1
                                    : s.highlighted - 1;
                            $event.preventDefault();
                        }
                        break;
                    case 13: // enter
                        if (s.showDropdown && s.highlighted >= 0) {
                            $scope.selectUser(s.results[s.highlighted]);
                            $event.preventDefault();
                        }
                        break;
                    case 27: // escape
                        s.showDropdown = false;
                        break;
                }
            };

            $scope.hideDropdown = function () {
                // Delay so a click on an item registers before hiding.
                $scope.userSearch.showDropdown = false;
            };

            $scope.showDropdown = function () {
                if ($scope.userSearch.results.length > 0) {
                    $scope.userSearch.showDropdown = true;
                }
            };
        },
    ]);
