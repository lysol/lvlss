var App = angular.module('lvlss', [
    'ui.router'
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
    .factory('socket', function($rootScope) {
        var socket = io.connect('/lvlss');
        return {
            on: function (eventName, callback) {
                socket.on(eventName, function () {
                    var args = arguments;
                    $rootScope.$apply(function () {
                        callback.apply(socket, args);
                    });
                });
            },
            emit: function (eventName, data, callback) {
                console.log('Emit event ' + eventName);
                socket.emit(eventName, data, function () {
                    var args = arguments;
                    $rootScope.$apply(function () {
                        if (callback) {
                            callback.apply(socket, args);
                        }
                    });
                });
            }
        };
    });