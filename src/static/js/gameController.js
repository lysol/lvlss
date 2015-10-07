App.controller('lvlss.gameController', ['$scope', 'socket', '$location', function($scope, socket, $location) {
    var self = this;
    this.inventory = [];
    this.location = {};
    this.location_areas = [];
    this.location_items = [];
    this.clientcrap = [];

    $scope.$on('location', function(evt, data) {
        self.location = data.area;
    });

    $scope.$on('location_items', function(evt, data) {
        self.location_items = data.inventory;
    });

    $scope.$on('location_areas', function(evt, data) {
        self.location_areas = data.areas;
    });

    $scope.$on('inventory', function(evt, data) {
        self.inventory = data.inventory;
    });

}]);
