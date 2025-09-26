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
	$scope.openChangePasswordModal = function() {
        $uibModal.open({
            templateUrl: 'components/profile/changePasswordModal.html',
            controller: 'ChangePasswordController'
        });
    };

	$scope.orcidConnect = function() {
		console.log('Connecting to ORCID');
        var client_id = 'APP-A964UH0MDGR37RWY';
		var redirect_uri = 'http://127.0.0.1/orcid/callback/';

		console.log('Redirecting to ORCID');
		window.location.href = 'https://sandbox.orcid.org/oauth/authorize?client_id=' + client_id + '&response_type=code&scope=/authenticate&redirect_uri=' + redirect_uri;
	};

	$scope.githubConnect = function() {
		console.log('Connecting to GitHub');
		var client_id = 'Ov23liQxjwvSvDR3gUzX';
		var redirect_uri = 'http://127.0.0.1/github/callback/';

		console.log('Redirecting to GitHub');
		window.location.href = 'https://github.com/login/oauth/authorize?client_id=' + client_id + '&redirect_uri=' + redirect_uri;
	};
}]);