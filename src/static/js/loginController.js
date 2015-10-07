var loginController = function($scope, socket, $location) {
    var self = this;
    this.username = '';
    this.signingIn = false;
    this.signinError = '';
    this.socket = socket;

    $scope.$on('login-success', function(evt, data) {
        self.signingIn = false;
        self.signinError = '';
        $location.path('/game');
    });

    $scope.$on('login-error', function(evt, data) {
        self.signingIn = false;
        self.signinError = data.error;
    });

};

loginController.prototype.signIn = function() {
    if (!this.signingIn) {
        // this.signingIn = true;

        if (this.username.length > 0) {
            this.socket.emit('login', { username: this.username });
        }
    }
};

App.controller('lvlss.loginController', ['$scope', 'socket', '$location', loginController]);
