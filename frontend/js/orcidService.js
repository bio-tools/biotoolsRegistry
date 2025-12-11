(function() {
  'use strict';

  angular.module('elixir_front')
  .service('OrcidAuth', ['AppConfig', '$window', '$rootScope', function(AppConfig, $window, $rootScope) {

    function randomState() {
      try {
        var arr = new Uint8Array(16);
        ($window.crypto || $window.msCrypto).getRandomValues(arr);
        return Array.prototype.map.call(arr, function(b){ return ('00' + b.toString(16)).slice(-2); }).join('');
      } catch (e) {
        return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
      }
    }

    function saveState(stateToken) {
      // Persist state + intended return route
      sessionStorage.setItem('orcid_oauth_state', stateToken);

      var payload = null;
      if ($rootScope.toState && $rootScope.toState.name &&
          !/signup/.test($rootScope.toState.name) &&
          !/reset-password/.test($rootScope.toState.name)) {
        payload = { name: $rootScope.toState.name, params: $rootScope.toStateParams || {} };
      }
      sessionStorage.setItem('orcid_oauth_state_payload', JSON.stringify(payload));
    }

    function buildAuthorizeUrl(stateToken) {
      var base = AppConfig.ORCID_BASE_URL || 'https://orcid.org';
      var params = new URLSearchParams({
        client_id: AppConfig.ORCID_CLIENT_ID || '',
        response_type: 'code',
        scope: '/authenticate',
        redirect_uri: AppConfig.ORCID_REDIRECT_URI || '',
        state: stateToken
      });
      return base.replace(/\/+$/,'') + '/oauth/authorize?' + params.toString();
    }

    this.start = function() {
      var state = randomState();
      saveState(state);
      var url = buildAuthorizeUrl(state);
      $window.location.replace(url);
    };

    this.consumeState = function(received) {
      var expected = sessionStorage.getItem('orcid_oauth_state');
      var payload = sessionStorage.getItem('orcid_oauth_state_payload');

      // cleanup
      sessionStorage.removeItem('orcid_oauth_state');
      sessionStorage.removeItem('orcid_oauth_state_payload');

      return {
        ok: !!received && received === expected,
        payload: payload ? JSON.parse(payload) : null
      };
    };
  }]);
})();