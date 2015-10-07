var App = angular.module('lvlss', [
    'ui.router',
    'btford.socket-io'
])
    .run([
        '$rootScope',
        '$state',
        '$stateParams',
        function ($rootScope, $state, $stateParams) {
            $rootScope.$state = $state;
            $rootScope.$stateParams = $stateParams;
        }])

    .config([
        '$stateProvider', '$urlRouterProvider',
        function($stateProvider, $urlRouterProvider) {
            $urlRouterProvider
                .otherwise('/');

            $stateProvider
                .state('login', {
                    url: '/',
                    templateUrl: '/partials/login.html'
                })
                .state('game', {
                    url: '/game',
                    templateUrl: '/partials/game.html'
                })
        }])

    .factory('socket', function (socketFactory) {
        var myIoSocket = io.connect('/lvlss');
        var socket = socketFactory({
            prefix: '',
            ioSocket: myIoSocket
        });
        socket.forward([
            'login-success',
            'login-failure',
            'location',
            'location_areas',
            'location_inventory',
            'inventory',
            'clientcrap'
        ]);

        return socket;
    })