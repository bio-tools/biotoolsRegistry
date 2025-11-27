// Controllers
angular.module('elixir_front.controllers').controller('LoginMangerController', ['$scope', '$uibModal', '$rootScope', '$state', function($scope, $uibModal, $rootScope, $state) {
	var vm = this;

	vm.openLoginModal = function() {
		$uibModal.open({
			templateUrl: 'partials/modals/loginModal.html',
			controller: ['$uibModalInstance', 'djangoAuth', '$rootScope', '$state', 'AppConfig', LoginModalController],
			controllerAs: 'vm',
			windowClass: 'login-modal-window'
		});
	};
}]);

function LoginModalController($uibModalInstance, djangoAuth, $rootScope, $state, AppConfig) {
	var vm = this;
	vm.error = {};

	vm.loginButtonPressed = function(username, password) {
		vm.error.username = "";
		vm.error.password = "";
		vm.error.general = [];
		if (!username && !password) {
			vm.error.username = "Username is required";
			vm.error.password = "Password is required";
			vm.error.general = ["Username and password are required"];
		}
		else if (!username) {
			vm.error.username = "Username is required";
			vm.error.general = ["Username is required"];
		}
		else if (!password) {
			vm.error.password = "Password is required";
			vm.error.general = ["Password is required"];
		}
		else {
			djangoAuth.login(username, password).then(function (response) {
			// go to states set before redirection to login
			if(typeof $rootScope.toState == 'undefined' || /signup/.test($rootScope.toState.name) || /reset-password/.test($rootScope.toState.name)) {
				$state.go('search');
			} else {
				$state.go($rootScope.toState.name, $rootScope.toStateParams);
			}
			$uibModalInstance.close();
		}, function (response) {
			vm.error.general = response.general_errors;
		});
		}
	}

	vm.registerButtonPressed = function() {
		$uibModalInstance.close();
		$state.go('signup');
	}

	vm.forgotButtonPressed = function() {
		$uibModalInstance.close();
		$state.go('reset-password');
	}

	vm.orcidLoginPressed = function() {
		var client_id = AppConfig.ORCID_CLIENT_ID;
		var redirect_uri = AppConfig.ORCID_REDIRECT_URI;
		var orcid_base_url = AppConfig.ORCID_BASE_URL;

		window.location.href = orcid_base_url + '/oauth/authorize?client_id=' + client_id + '&response_type=code&scope=/authenticate&redirect_uri=' + redirect_uri;
	}
}
