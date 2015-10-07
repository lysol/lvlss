App.controller('lvlss.loginController', ['$scope', 'socket', '$location', function($scope, socket, $location) {

    $scope.username = '';
    $scope.signingIn = false;
    $scope.signinError = '';

    $scope.signIn = function() {
        if (!$scope.signingIn) {
            // $scope.signingIn = true;

            if ($scope.username.length > 0) {
                socket.emit('login', { username: $scope.username });
            }
        }
    }

    socket.on('login-success', function(evt, data) {
        $scope.signingIn = false;
        $scope.signinError = '';
        $location.path('/game');
    });

    socket.on('login-error', function(evt, data) {
        $scope.signingIn = false;
        $scope.signinError = data.error;
    });

}])