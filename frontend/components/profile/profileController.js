// Use the existing djangoAuth service from djangoAuth.js to avoid duplication
angular.module('elixir_front')
.controller('ProfileController', ['$scope', '$state', 'djangoAuth', 'DisownToolService', 'User', '$uibModal', function($scope, $state, djangoAuth, DisownToolService, User, $uibModal) {
    $scope.profile = {};
    $scope.loading = true;
    $scope.User = User;
    djangoAuth.profile()
    .then(function (response) {
        $scope.profile = response;
        $scope.loading = false;
    }, function (response) {
        $scope.loading = false;
    });

    $scope.disownEntry = function(entry) {
        if (!confirm("Are you sure you want to disown this resource?")){
            return;
        }
        DisownToolService.disown({id: entry.id, version: entry.versionId}, function(response) {
            $scope.profile.resources = _.difference($scope.profile.resources, [entry]);
        }, function(response) {
            alert("Failed to disown " + entry.name + ". Please check your connection and try again later.");
        });
    };

    $scope.openChangeEmailModal = function() {
        $uibModal.open({
            templateUrl: 'components/profile/changeEmailModal.html',
            controller: 'ChangeEmailController'
        });
    };

    $scope.openChangePasswordModal = function() {
        $uibModal.open({
            templateUrl: 'components/profile/changePasswordModal.html',
            controller: 'ChangePasswordController'
        });
    };
}]);