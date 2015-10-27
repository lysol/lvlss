var propertiesController = function($scope, socket, $location, manos) {
    var self = this;
    this.id = undefined;
    this.name = '';
    this.manos = manos;
    this.socket = socket;
    this.thing = undefined;

    $scope.$on('item-info', function(evt, data) {
        self.setThing(data.item);
    });    

    $scope.$on('area-info', function(evt, data) {
        self.setThing(data.area);
    });    
};

propertiesController.prototype.setThing = function(thing) {
    this.id = thing.id;
    this.thing = thing;
}

propertiesController.prototype.close = function() {
    this.id = undefined;
    this.thing = undefined;
}

propertiesController.prototype.editScript = function(itemId) {
    this.id = undefined;
    this.thing = undefined;
    this.manos.emit('edit-script', {itemId: itemId});
}

propertiesController.prototype.editImage = function(itemId) {
    this.id = undefined;
    this.thing = undefined;
    this.manos.emit('edit-image', {itemId: itemId});
}

App.controller('lvlss.propertiesController', ['$scope', 'socket', '$location', 'manos', propertiesController]);
