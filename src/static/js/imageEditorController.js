var imageEditorController = function($scope, $rootScope, socket, $location, manos) {
    var self = this;
    this.socket = socket;
    this.manos = manos;
    this.rows = undefined;
    this.itemId = undefined;

    this.painting = false;
    this.paint_value = 0;

    this.$scope = $scope;
    this.$rootScope = $rootScope;

    this.$scope.$on('image-content', function(evt, data) {
        self.rows = [];
        for (var row=0; row<data.dimensions[1]; row++) {
            self.rows.push([])
            for (var cell=0; cell<data.dimensions[0]; cell++) {
                self.rows[row].push(data.pixels[data.dimensions[1] * row + cell]);
            }
        }
    });

    manos.on('edit-image', this.$scope, function(evt, data) {
        self.itemId = data.itemId;
        self.load();
    })
};

imageEditorController.prototype.stopPainting = function() {
    this.painting = false;
};

imageEditorController.prototype.startPainting = function(x, y, skipStart) {
    this.rows[x][y] = !this.rows[x][y];
    this.socket.emit('cmd', {command: 'save-pixel', args: [this.itemId, x, y, this.rows[x][y]]});
    if (skipStart === undefined || !skipStart) {
        this.painting = true;
        this.paint_value = this.rows[x][y];
    }
};

imageEditorController.prototype.checkPaint = function(x, y) {
    var this_cell = this.rows[x][y];
    if (this.painting && this_cell != this.paint_value) {
        this.startPainting(x, y, true)
    };
};

imageEditorController.prototype.close = function() {
    this.$rootScope.$broadcast('reload-image', { itemId: this.itemId });
    this.rows = undefined;
    this.itemId = undefined;
};

imageEditorController.prototype.load = function() {
    this.socket.emit('cmd', {command: 'get-image', args: [this.itemId]});
};

App.controller('lvlss.imageEditorController', ['$scope', '$rootScope', 'socket', '$location', 'manos', imageEditorController]);
