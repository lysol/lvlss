var gameController = function($scope, socket, $location) {
    var self = this;
    this.inventory = [];
    this.location = {};
    this.location_areas = [];
    this.location_items = [];
    this.clientcrap = [];
    this.socket = socket;
    this.command = '';

    $scope.$on('clientcrap', function(evt, data) {
        self.clientcrap = self.clientcrap.concat(data.lines);
    });

    $scope.$on('location', function(evt, data) {
        self.location = data.area;
    });

    $scope.$on('location_inventory', function(evt, data) {
        self.location_items = data.inventory;
    });

    $scope.$on('location_areas', function(evt, data) {
        self.location_areas = data.areas;
    });

    $scope.$on('inventory', function(evt, data) {
        self.inventory = data.inventory;
    });



};

gameController.prototype.travel = function(areaId) {
    this.socket.emit('cmd', {command: 'go', args: [areaId]});
};

gameController.prototype.sendCommand = function() {
    if (this.command.length > 0) {
        var parts = this.command.split(' ')
        this.socket.emit('cmd', {command: parts.shift(), args: parts});
        this.command = '';
    }
};

gameController.prototype.takeItem = function(itemId) {
    this.socket.emit('cmd', {command: 'take', args: [itemId]});
};

gameController.prototype.dropItem = function(itemId) {
    this.socket.emit('cmd', {command: 'drop', args: [itemId]});
};

App.controller('lvlss.gameController', ['$scope', 'socket', '$location', gameController]);
