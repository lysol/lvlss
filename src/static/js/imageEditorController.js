var imageEditorController = function($scope, socket, $location, manos) {
    var self = this;
    this.socket = socket;
    this.manos = manos;
    this.rows = undefined;

    $scope.$on('get-image', function(evt, data) {
        this.rows = [];
        for (var row=0; row<data.dimensions[1]; row++) {
            this.rows.push([])
            for (var cell=0; cell<data.dimensions[0]; cell++) {
                this.rows[row].push(data.pixels[data.dimensions[1] * row + cell]);
            }
        }
    });
};

imageEditorController.prototype.toggle = function(x, y) {
    this.rows[x][y] = !this.rows[x][y];

    this.socket.emit('cmd', {command: 'save_pixel', args: [x, y, this.rows[x][y]]});
};

imageEditorController.prototype.close = function() {
    this.rows = undefined;
};

App.controller('lvlss.imageEditorController', ['$scope', 'socket', '$location', 'manos', imageEditorController]);
