'use strict';

var elixir_front = angular.module('elixir_front', [
	'elixir_front.filters',
	'elixir_front.services',
	'elixir_front.directives',
	'elixir_front.controllers',
	'ui.bootstrap',
	'ngCookies',
	'ngRoute',
	'ngSanitize',
	'ngAnimate',
	'ngResource',
	'ui.router',
	'angularBootstrapNavTree',
	'treeControl',
	'720kb.tooltips',
	'yaru22.angular-timeago',
	'angularDjangoRegistrationAuthApp',
	'ngTagsInput',
	'pasvaz.bindonce',
	'ui.grid',
	'ui.grid.resizeColumns',
	'ui.grid.autoResize',
	'ui.grid.saveState',
	'ui.grid.moveColumns',
	'chart.js',
	'ngMeta'
], function($rootScopeProvider) {})

// setting up router and states
.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {
	// default state
	$urlRouterProvider.when('', '/');
	// for any unmatched url, send to 404
	$urlRouterProvider.otherwise('/404');
	$stateProvider
	.state('404', {
		url: "/404",
		templateUrl: "partials/404.html",
		data: {
			meta: {
				'title': 'Page not found'
		},
			roles: []
		},
		resolve: {}
	})
	.state('home', {
		url: "/",
		templateUrl: "components/home/home.html",
		data: {
			meta: {
				'title': 'bio.tools · Bioinformatics Tools and Services Discovery Portal',
				'description': 'A registry of bioinformatics software resources including biological databases, analytical tools and data services',
				'titleSuffix': '',
				'og:title': 'bio.tools · Bioinformatics Tools and Services Discovery Portal',
				'og:description': 'A registry of bioinformatics software resources including biological databases, analytical tools and data services',
				'og:image': 'https://bio.tools/img/ELIXIR_logo_white_background_small.png'
			},
			roles: []
		},
		resolve: {}
	})
	.state('about', {
		url: "/about",
		templateUrl: "components/about/about.html",
		data: {
			meta: {
				'title': 'About',
				'description': 'A registry of bioinformatics software resources including biological databases, analytical tools and data services'
			},
			roles: []
		},
		resolve: {}
	})
	.state('schema', {
		url: "/schema",
		templateUrl: "partials/schema.html",
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('stats', {
		url: "/stats",
		templateUrl: "components/stats/stats.html",
		data: {
			meta: {
				'title': 'Stats',
				'description': 'bio.tools content statistics.'
			},
			roles: []
		},
		controller: "StatsController",
		resolve: {}
	})
	.state('search', {
		url: "/t?page&q&biotoolsID&name&topic&function&operation&input&inputDataFormat&inputDataType&output&outputDataFormat&outputDataType&homepage&description&version&accessibility&toolType&collectionID&maturity&operatingSystem&language&cost&license&documentation&link&download&publication&credit&owner&sort&ord&domain&topicID&operationID&dataType&dataTypeID&dataFormat&dataFormatID&inputID&inputDataTypeID&inputDataFormatID&outputID&outputDataTypeID&outputDataFormatID&creditName&creditTypeRole&creditTypeEntity&creditOrcidID&publicationID&publicationType&publicationVersion&linkType&documentationType&downloadType&downloadVersion&otherID&otherIDType&otherIDVersion&otherIDValue&elixirPlatform&elixirNode&elixirCommunity&creditGridID&creditRORID&creditFundRefID",
		templateUrl: "partials/search_results.html",
		data: {
			meta: {
				'title': 'bio.tools · Bioinformatics Tools and Services Discovery Portal',
				'description': 'A registry of bioinformatics software resources including biological databases, analytical tools and data services',
				'titleSuffix': '',
				'og:title': 'bio.tools · Bioinformatics Tools and Services Discovery Portal',
				'og:description': 'A registry of bioinformatics software resources including biological databases, analytical tools and data services',
				'og:image': 'https://bio.tools/img/ELIXIR_logo_white_background_small.png'
			},
			roles: []
		},
		controller: "SearchResultController"
	})
	.state('register', {
		url: "/register",
		templateUrl: "partials/toolEdit.html",
		data: {
			meta: {
				'title': 'Register new resource',
				'description': 'Register a tool or database in bio.tools.',
				'og:title': 'Register new resource',
				'og:description': 'Register a tool or database in bio.tools.'
		},
			roles: ['User']
		},
		controller: "ToolCreateController",
		resolve: {}
	})
	.state('edit-subdomain', {
		url: "/edit-subdomain/:id",
		templateUrl: "partials/subdomains/subdomainEdit.html",
		data: {
			meta: {
				'title': 'Edit subdomain',
				'og:title': 'Edit subdomain'
			},
			roles: ['User']
		},
		controller: "SubdomainController",
		resolve: {}
	})
	.state('admin-subdomain', {
		url: "/subdomain",
		templateUrl: "partials/subdomains/subdomainPage.html",
		data: {
			meta: {
				'title': 'Subdomain',
				'og:title': 'Subdomain'
			},
			roles: ['User']
		},
		controller: "SubdomainAdminController",
		resolve: {}
	})
	.state('login', {
		url: "/login",
		templateUrl: "partials/login.html",
		data: {
			meta: {
				'title': 'Log in',
				'description': 'Log in to bio.tools.',
				'og:title': 'Log in',
				'og:description': 'Log in to bio.tools.'
			},
			roles: []
		},
		controller: "LoginController",
		resolve: {}
	})
	.state('signup', {
		url: "/signup",
		templateUrl: "partials/signup.html",
		data: {
			meta: {
				'title': 'Sign up',
				'description': 'Sign up for bio.tools.',
				'og:title': 'Sign up',
				'og:description': 'Sign up for bio.tools.'
			},
			roles: []
		},
		controller: "SignupController"
	})
	.state('signup.success', {
		url: "/success",
		templateUrl: "partials/signupSuccess.html",
		data: {
			meta: {
				'title': 'Sign up success'
			},
			roles: []
		}
	})
	.state('signup.verify-email', {
		abstract: true,
		url: "/verify-email",
		template: "<ui-view/>",
		data: {
			meta: {
				'title': 'Verify email'
			},
			roles: []
		}
	})
	.state('signup.verify-email.success', {
		url: "/success",
		templateUrl: "partials/signupVerifyEmailSuccess.html",
		data: {
			meta: {
				'title': 'Verification success'
			},
			roles: []
		}
	})
	.state('signup.verify-email.key', {
		url: "/:key",
		templateUrl: "partials/signupVerifyEmailKey.html",
		data: {
			meta: {
				'title': 'Verify email'
			},
			roles: []
		},
		controller: "SignupVerifyEmailKeyController"
	})
	.state('reset-password', {
		url: "/reset-password",
		templateUrl: "partials/resetPassword.html",
		data: {
			meta: {
				'title': 'Reset password'
			},
			roles: []
		},
		controller: "ResetPasswordController"
	})
	.state('reset-password.confirm', {
		url: "/confirm?uid&token",
		templateUrl: "partials/resetPasswordConfirm.html",
		data: {
			meta: {
				'title': 'Reset password'
			},
			roles: []
		},
		controller: "ResetPasswordConfirmController"
	})
	.state('reset-password.confirm.success', {
		url: "/success",
		templateUrl: "partials/resetPasswordConfirmSuccess.html",
		data: {
			meta: {
				'title': 'Reset password success'
			},
			roles: []
		}
	})
	.state('profile', {
		url: "/profile",
		templateUrl: "components/profile/profile.html",
		data: {
			meta: {
				'title': 'My profile'
			},
			roles: []
		},
		controller: "ProfileController"
	})
	.state('subdomain', {
		url: "/t?:domain"
	})
	.state('requests', {
		url: "/requests",
		templateUrl: "partials/requests.html",
		data: {
			roles: []
		},
		controller: "RequestsController"
	})
	.state('workflows', {
		url: "/workflows",
		templateUrl: "partials/workflows/workflows.html",
		data: {
			roles: []
		},
		controller: "WorkflowController"
	})
	.state('tool-explicit', {
		url: "/tool/:id",
		templateUrl: "components/toolPage/toolPage.html",
		data: {
			roles: []
		},
		controller: "ToolPageController",
		resolve: {}
	})
	.state('tool-explicit-short', {
		url: "/t/:id",
		templateUrl: "components/toolPage/toolPage.html",
		data: {
			roles: []
		},
		controller: "ToolPageController",
		resolve: {}
	})
	.state('tool', {
		url: "/:id",
		templateUrl: "components/toolPage/toolPage.html",
		data: {
			roles: []
		},
		controller: "ToolPageController",
		resolve: {}
	})
	.state('tool.edit', {
		url: "/edit",
		templateUrl: "partials/toolEdit.html",
		data: {
			roles: ['User']
		},
		controller: "ToolUpdateController",
		resolve: {}
	})
	// redirects
	.state('governance', {
		url: '/governance',
		redirect: 'http://biotools.readthedocs.io/en/latest/governance.html',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('events', {
		url: '/events',
		redirect: 'https://docs.google.com/document/d/1K-6IG_7a-4amstSSOxYjjJ3uDUEg4-WGSSt9jvvO7Ik/edit#heading=h.twop51kvyu80',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('mail', {
		url: '/mail',
		redirect: 'http://elixirmail.cbs.dtu.dk/mailman/listinfo',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('faq', {
		url: '/faq',
		redirect: 'https://docs.google.com/document/d/1WdcY0WQJVdRHz0BAhII7s8gygxKRJaHZC4gOnAC1eqs/edit',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('apidoc', {
		url: '/apidoc',
		redirect: 'https://docs.google.com/document/d/1c1zridWLBNSrWcYyR2fnBfgjWfrUSrT7HJ6Ql6ZCkS4/edit#heading=h.9a2zbl9ka0z0',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('changelog', {
		url: '/changelog',
		redirect: 'https://docs.google.com/document/d/1C5KFu2t4OIAuUpx6dS7Djsa9y3zgicd8naOsAs9QPAY/edit#heading=h.eu5jkfa77et',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('helpdesk', {
		url: '/helpdesk',
		redirect: 'https://elixir-registry.atlassian.net/servicedesk/customer/portal/2/user/login?destination=portal%2F2',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('projects', {
		url: '/projects',
		redirect: 'https://docs.google.com/document/d/1QBIZHBzHxxmvSnOG3xK6t3SCeft5g4AH2rVICLRLmDw/edit#heading=h.a6i4b9p7xdw7',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
	.state('roadmap', {
		url: '/roadmap',
		redirect: 'https://docs.google.com/document/d/17iH72hmwVo205QVEkptv7GTMlqFojatIwMmxVOyuPy8/edit#heading=h.m1jhkecru8xq',
		external: true,
		data: {
			roles: []
		},
		resolve: {}
	})
}])

// enable HTML5 mode which removes the leading # from URL
.config(function($locationProvider) {
	$locationProvider.html5Mode(true).hashPrefix('!')
})

// default settings for tooltips
.config(function(tooltipsConfigProvider) {
	tooltipsConfigProvider.options({
		speed: 'fast',
		try: 0
	})
})

// make redirect states work
.run(function($rootScope, $window) {
	$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
		if (toState.external) {
			event.preventDefault();
			$window.open(toState.redirect, '_self');
		}
	});
})

// make ngMeta run and configure
.run(['ngMeta', function(ngMeta) { 
  ngMeta.init();
}])
.config(function(ngMetaProvider) {

    ngMetaProvider.useTitleSuffix(true);
    ngMetaProvider.setDefaultTitle('bio.tools');
    // ngMetaProvider.setDefaultTitleSuffix(' · bio.tools');
    // ngMetaProvider.setDefaultTag('author', 'John Smith');
})

// user authentication
.run(['$rootScope', '$state', '$timeout', 'User', 'djangoAuth', '$http', function($rootScope, $state, $timeout, User, djangoAuth, $http) {
	User.authenticated = false;

	// what happens on User login
	var logInCallback = function(){
		User.authenticated = true;
		// get user profile
		djangoAuth.profile().then(function (response) {
			User.current = response;
		});
	};

	// what happens on authentication errors
	var wrongAuthCallback = function() {
		delete $http.defaults.headers.common.Authorization;
		delete localStorage.token;
		User.authenticated = false;
		User.current = {};
	};

	// what happens on User logout
	var logOutCallback = function() {
		wrongAuthCallback();
		$state.go('home');
	}

	// get initial authentication status
	var authenticationPromise = djangoAuth.authenticationStatus(true).then(logInCallback, wrongAuthCallback);

	// set relevant callbacks for log in/out events
	$rootScope.$on('djangoAuth.logged_in', logInCallback);
	$rootScope.$on('djangoAuth.logged_out', logOutCallback);

	// checking authentication on state change
	$rootScope.$on('$stateChangeStart', function(event, toState, toStateParams, fromState, fromStateParams) {
		// save current state transitions
		if (toState.name != 'login') {
			$rootScope.toState = toState;
			$rootScope.toStateParams = toStateParams;
		}
		$rootScope.fromState = fromState;

		// pausing the state change, so that the user authentication has a chance to proceed before state change
		if (typeof toState.resolve == 'undefined') { toState.resolve = {} };
		toState.resolve.pauseStateChange = ['$q', function($q) {
				var defer = $q.defer();
				authenticationPromise.then(function () {
					if (!User.authenticated && _.includes(toState.data.roles, 'User')) {
						event.preventDefault();
						// save destination states to return to them on proper login
						$rootScope.returnToState = $rootScope.toState;
						$rootScope.returnToStateParams = $rootScope.toStateParams;
						// direct unauthenticated user to login
						$state.go('login');
					}
					defer.resolve();
				});
				return defer.promise;
			}
		]
	});
	// on error go to 404
	$rootScope.$on('$stateChangeError', function(event) {
		$state.go('404');
	});
}])

// filling in title and description meta attributes in header
.run(["$rootScope", "$timeout", "$state", function($rootScope, $timeout, $state) {
	function getTextValue(text) {
		return angular.isFunction(text) ? text() : text;
	}

	$rootScope.$on("$stateChangeSuccess", function() {
		var title = getTextValue($state.$current.locals.globals.$title);
		var description = getTextValue($state.$current.locals.globals.$description);
		if(title) {
			$timeout(function() {
				$rootScope.$title = title;
			});
		}
		if(description) {
			$timeout(function() {
				$rootScope.$description = description;
			});
		}
	});
}])
