var scriptEditorController = function($scope, socket, $location, manos) {
    var self = this;
    this.itemId = undefined;
    this.scriptBody = '';
    this.$scope = $scope;
    this.manos = manos;

    manos.on('edit-script', $scope, function(evt, data) {
        self.itemId = data.itemId;
        $scope.load(self.itemId);
    })

    $scope.$on('script_body', function(evt, data) {
        self.scriptBody = data.script_body;
    });
};

scriptEditorController.prototype.save = function(itemId) {
    this.socket.emit('cmd', {command: 'script', args:[ itemId, this.scriptBody ]})
};

scriptEditorController.prototype.load = function(itemId) {
    this.socket.emit('cmd', {command: 'getscript', args: [itemId]});
};

scriptEditorController.prototype.close = function() {
    this.manos.emit('close-editor', []);
};

App.controller('lvlss.scriptEditorController', ['$scope', 'socket', '$location', 'manos', scriptEditorController]);
