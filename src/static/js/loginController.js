App.controller('lvlss.loginController', ['$scope', 'socket', '$location', function($scope, socket, $location) {

    $scope.username = '';
    $scope.signingIn = false;
    $scope.signinError = '';

    $scope.signIn = function() {
        if (!$scope.signingIn) {
            $scope.signingIn = true;

            if ($scope.username.length > 0) {
                socket.emit('cmd', {command: 'login', args: [$scope.username]});
            }
        }
    }

    socket.on('login-success', function(data) {
        $scope.signingIn = false;
        $scope.signinError = '';
        $location.path('/game');
    });

    socket.on('login-error', function(data) {
        $scope.signingIn = false;
        $scope.signinError = data.error;
    });

}])