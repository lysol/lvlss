var App = angular.module('lvlss', [
    'ui.router',
    'btford.socket-io',
    'luegg.directives',
    'ngAnimate'
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
            'location-areas',
            'location-inventory',
            'inventory',
            'clientcrap',
            'script-body',
            'script-saved',
            'script-error',
            'item-info',
            'player-status',
            'image-content',
            'pixel-set'
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

    .directive('ngReloadImage', ['$rootScope', function($rootScope) {
        return {
            scope: false,
            link: function(scope, element, attrs) {
                scope.$on('reload-image', function(ev, data){
                    if (attrs.id == data.itemId) {
                        // image ID matches, reload it
                        scope.$parent.updateItemToken(data.itemId);
                    }
                });
            }
        };
    }])

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