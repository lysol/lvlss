var loginController = function($scope, socket, $location) {
    var self = this;
    this.username = '';
    this.loggingIn = false;
    this.loginError = '';
    this.socket = socket;

    $scope.$on('login-success', function(evt, data) {
        self.loggingIn = false;
        self.loginError = '';
        $location.path('/game');
    });

    $scope.$on('login-failure', function(evt, data) {
        self.loggingIn = false;
        self.loginError = data.error;
    });

};

loginController.prototype.signIn = function() {
    if (!this.loggingIn) {
        // this.loggingIn = true;

        if (this.username.length > 0) {
            this.socket.emit('login', { username: this.username });
        }
    }
};

App.controller('lvlss.loginController', ['$scope', 'socket', '$location', loginController]);
