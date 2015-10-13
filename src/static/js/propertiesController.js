var propertiesController = function($scope, socket, $location, manos) {
    var self = this;
    this.id = '';
    this.name = '';
    this.manos = manos;
    this.socket = socket;

    $scope.$on('item-info', function(evt, data) {
        self.setThing(data.item);
    });    

    $scope.$on('area-info', function(evt, data) {
        self.setThing(data.area);
    });    
};

propertiesController.prototype.setThing = function(thing) {
    this.id = thing.id;
    this.name = thing.name;
}

propertiesController.prototype.close = function() {
    this.manos.emit('close-properties', []);
}

App.controller('lvlss.propertiesController', ['$scope', 'socket', '$location', 'manos', propertiesController]);
