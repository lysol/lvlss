var imageEditorController = function($scope, socket, $location, manos) {
    var self = this;
    this.socket = socket;
    this.manos = manos;
    this.rows = undefined;
    this.itemId = undefined;

    $scope.$on('image-content', function(evt, data) {
        self.rows = [];
        for (var row=0; row<data.dimensions[1]; row++) {
            self.rows.push([])
            for (var cell=0; cell<data.dimensions[0]; cell++) {
                self.rows[row].push(data.pixels[data.dimensions[1] * row + cell]);
            }
        }
    });

    manos.on('edit-image', $scope, function(evt, data) {
        self.itemId = data.itemId;
        self.load();
    })
};

imageEditorController.prototype.toggle = function(x, y) {
    this.rows[x][y] = !this.rows[x][y];

    this.socket.emit('cmd', {command: 'save-pixel', args: [this.itemId, x, y, this.rows[x][y]]});
};

imageEditorController.prototype.close = function() {
    this.rows = undefined;
};

imageEditorController.prototype.load = function() {
    this.socket.emit('cmd', {command: 'get-image', args: [this.itemId]});
};

App.controller('lvlss.imageEditorController', ['$scope', 'socket', '$location', 'manos', imageEditorController]);
