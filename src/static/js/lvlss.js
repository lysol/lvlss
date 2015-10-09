var App = angular.module('lvlss', [
    'ui.router',
    'btford.socket-io',
    'luegg.directives'
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
            'clientcrap',
            'script_body',
            'script_saved',
            'script_error'
        ]);

        return socket;
    })

    .directive('ngEnter', function () {
        return function (scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if(event.which === 13) {
                    scope.$apply(function (){
                        scope.$eval(attrs.ngEnter);
                    });

                    event.preventDefault();
                }
            });
        };
    })

    // * * * THE HANDS OF FATE * * *
    .factory('manos', ['$rootScope', function($rootScope) {
        var manos = {};
        manos.emit = function(msg, data) {
        $rootScope.$emit(msg, data);
        };
        manos.on = function(msg, scope, func) {
            var unbind = $rootScope.$on(msg, func);
            scope.$on('$destroy', unbind);
        };
        return manos;
    }])