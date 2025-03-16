angular.module('elixir_front')
.controller('ChangePasswordController', ['$scope', '$uibModalInstance', 'djangoAuth', function($scope, $uibModalInstance, djangoAuth) {

    $scope.submitPassword = function() {
		var token = localStorage.getItem("authToken");  // Store and retrieve auth token securely
        var oldPassword = $scope.oldPassword;
        var newPassword1 = $scope.newPassword;
        var newPassword2 = $scope.confirmPassword;
        
        djangoAuth.changePassword(oldPassword, newPassword1, newPassword2)
            .then(function(response) {
                alert('Password updated successfully!');
                $uibModalInstance.close();
            })
            .catch(function(error) {
                console.error("error: ", error);
                let firstKey = Object.keys(error)[0]; // First error key (old_password, new_password2...)
                alert('Failed to update password: ' + error[firstKey][0]);
            });
    };
}]);