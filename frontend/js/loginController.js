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

		console.log('Redirecting to ORCID');
		window.location.href = 'https://sandbox.orcid.org/oauth/authorize?client_id=' + client_id + '&response_type=code&scope=/authenticate&redirect_uri=' + redirect_uri;
	}

	vm.githubLoginPressed = function() {
		var client_id = AppConfig.GITHUB_CLIENT_ID;
		var redirect_uri = AppConfig.GITHUB_REDIRECT_URI;
		var scope = AppConfig.GITHUB_SCOPE;

		console.log('Redirecting to GitHub');
		window.location.href = 'https://github.com/login/oauth/authorize?client_id=' + client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scope;
	}
}
