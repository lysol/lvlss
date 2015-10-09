var scriptEditorController = function($scope, socket, $location, manos) {
    var self = this;
    this.itemId = undefined;
    this.scriptBody = '';
    this.$scope = $scope;
    this.manos = manos;
    this.socket = socket;
    this.scriptMessage = '';

    manos.on('edit-script', $scope, function(evt, data) {
        self.itemId = data.itemId;
        self.load();
    })

    $scope.$on('script_body', function(evt, data) {
        self.scriptBody = data.script_body;
    });

    $scope.$on('script_error', function(evt, data) {
        self.scriptMessage = data.error;
    });

    $scope.$on('script_saved', function(evt, data) {
        self.scriptMessage = 'Script saved.';
        setTimeout(function() {
            self.scriptMessage = '';
        }, 3000);
    });
};

scriptEditorController.prototype.save = function() {
    this.scriptMessage = 'Saving...';
    this.socket.emit('cmd', {command: 'script', args: [this.itemId, this.scriptBody]})
};

scriptEditorController.prototype.load = function() {
    this.socket.emit('cmd', {command: 'getscript', args: [this.itemId]});
};

scriptEditorController.prototype.close = function() {
    this.manos.emit('close-editor', []);
    this.scriptMessage = '';
    this.scriptBody = '';
    this.itemId = undefined;
};

App.controller('lvlss.scriptEditorController', ['$scope', 'socket', '$location', 'manos', scriptEditorController]);
