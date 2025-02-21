angular.module('elixir_front')
.controller('ChangePasswordController', ['$scope', '$uibModalInstance', 'djangoAuth', function($scope, $uibModalInstance, djangoAuth) {
    $scope.passwordData = {};
    $scope.submitPassword = function() {
        if ($scope.passwordData.newPassword !== $scope.passwordData.confirmPassword) {
            alert('Passwords do not match!');
            return;
        }
        djangoAuth.changePassword(
            $scope.passwordData.currentPassword,
            $scope.passwordData.newPassword,
            $scope.passwordData.confirmPassword
        ).then(function(response) {
            alert('Password updated successfully!');
            $uibModalInstance.close();
        }, function(error) {
            alert('Failed to update password: ' + (error.data.message || error.statusText));
        });
    };
}]);