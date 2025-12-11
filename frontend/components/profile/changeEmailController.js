angular.module('elixir_front')
.controller('ChangeEmailController', ['$scope', '$uibModalInstance', 'djangoAuth', function($scope, $uibModalInstance, djangoAuth) {
    $scope.submitEmail = function() {
        djangoAuth.updateProfile({email: $scope.newEmail})
        .then(function(response) {
            alert('Email updated successfully!');
            $uibModalInstance.close(response);
        }, function(error) {
            alert('Failed to update email: ' + error.email);
        });
    };
}]);