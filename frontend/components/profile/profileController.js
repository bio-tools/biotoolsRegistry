angular.module('elixir_front')
.controller('ProfileController', ['$scope', '$state', 'djangoAuth', 'DisownToolService', 'User', '$uibModal', 'AppConfig', function($scope, $state, djangoAuth, DisownToolService, User, $uibModal, AppConfig) {
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
	$scope.openChangePasswordModal = function() {
        $uibModal.open({
            templateUrl: 'components/profile/changePasswordModal.html',
            controller: 'ChangePasswordController'
        });
    };

	$scope.orcidConnect = function() {
        var client_id = AppConfig.ORCID_CLIENT_ID;
		var redirect_uri = AppConfig.ORCID_REDIRECT_URI;

		window.location.href = 'https://sandbox.orcid.org/oauth/authorize?client_id=' + client_id + '&response_type=code&scope=/authenticate&redirect_uri=' + redirect_uri;
	};

	$scope.githubConnect = function() {
		var client_id = AppConfig.GITHUB_CLIENT_ID;
		var redirect_uri = AppConfig.GITHUB_REDIRECT_URI;

		window.location.href = 'https://github.com/login/oauth/authorize?client_id=' + client_id + '&redirect_uri=' + redirect_uri;
	};

	$scope.disconnectSocial = function(provider, id) {
		if (!confirm("Are you sure you want to disconnect your " + provider + " account?")){
			return;
		}
		djangoAuth.disconnectSocial(id)
		.then(function(response) {
			console.log($scope.profile.socialAccounts);
			// Remove the disconnected account from the profile.socialAccounts array
			$scope.profile.socialAccounts = $scope.profile.socialAccounts.filter(function(account) {
				return account.id !== id;
			});
			console.log("Successfully disconnected " + provider + " account.");
			console.log($scope.profile.socialAccounts);
		}, function(error) {
			alert("Failed to disconnect your " + provider + " account. Please try again later.");
		});
	};

	// check if social accounts are connected
	$scope.hasGithubAccount = function() {
		if (!$scope.profile.socialAccounts) return false;
		return $scope.profile.socialAccounts.some(function(account) {
			return account.provider === 'github';
		});
	};

	$scope.hasOrcidAccount = function() {
		if (!$scope.profile.socialAccounts) return false;
		return $scope.profile.socialAccounts.some(function(account) {
			return account.provider === 'orcid';
		});
	};
}]);