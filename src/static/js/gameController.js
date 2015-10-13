var gameController = function($scope, socket, $location, manos) {
    var self = this;
    this.inventory = [];
    this.location = {};
    this.location_areas = [];
    this.location_items = [];
    this.clientcrap = [];
    this.socket = socket;
    this.command = '';
    this.$scope = $scope;
    this.manos = manos;
    this.command_error = '';

    $scope.$on('clientcrap', function(evt, data) {
        self.addCrap(data.lines);
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

    $scope.$on('item-info', function(evt, data) {
        angular.element(document.querySelector('#properties')).removeClass('hidden');
        angular.element(document.querySelector('#game')).addClass('hidden');
    });

    manos.on('close-editor', $scope, function(evt, data) {
        self.closeScriptEditor();
    });

    manos.on('close-properties', $scope, function(evt, data) {
        self.closeProperties();
    });

};

gameController.prototype.addCrap = function(crap) {
    if (typeof crap === 'string') {
        crap = [crap];
    }

    this.clientcrap = this.clientcrap.concat(crap);
};

gameController.prototype.travel = function(areaId) {
    this.socket.emit('cmd', {command: 'go', args: [areaId]});
};

gameController.prototype.sendCommand = function() {
    var self = this;
    if (self.command.length > 0) {

        var cmdstack = self.command.split('');
        var in_quote = false;
        var delim = undefined;
        var cmd_args = [];
        var current_arg = '';
        var escaped = false;

        while (true) {
            // stack is depleted. exit this
            if (cmdstack.length == 0) {
                if (current_arg.length > 0) {
                    cmd_args.push(current_arg);
                }
                break;
            }

            // get character
            var c = cmdstack.shift()

            // found an escape char, and we're not escaped.
            if (c == '\\' && !escaped) {
                escaped = true;
                continue;
            // c is a quote char and we're not escaped.
            // flip the quote state and set the quote delimiter.
            } else if ((c == '"' || c == "'") && !escaped) {
                in_quote = !in_quote;
                delim = (in_quote) ? c : undefined;
            // found whitespace, if we're not in quote
            // append the current command to the output stack.
            } else if (!in_quote && !escaped && c.match(/\s+/)) {
                cmd_args.push(current_arg);
                current_arg = '';
            // finally, exhausting all other cases, append the current char.
            } else {
                current_arg += c;
            }

            // at the end of each round, unset escape state.
            escaped = false;
        }

        // bad player
        if (in_quote) {
            self.addCrap('Unterminated ' + delim);
        } else {
            // seems legit.
            self.socket.emit('cmd', {command: cmd_args.shift(), args: cmd_args});
            this.command = '';
        }
    }
};

gameController.prototype.takeItem = function(itemId) {
    this.socket.emit('cmd', {command: 'take', args: [itemId]});
};

gameController.prototype.dropItem = function(itemId) {
    this.socket.emit('cmd', {command: 'drop', args: [itemId]});
};

gameController.prototype.editScript = function(itemId) {
    this.openScriptEditor();
    this.manos.emit('edit-script', {itemId: itemId});
};

gameController.prototype.openScriptEditor = function() {
    angular.element(document.querySelector('#script-editor')).removeClass('hidden');
    angular.element(document.querySelector('#game')).addClass('hidden');
};

gameController.prototype.closeScriptEditor = function() {
    angular.element(document.querySelector('#script-editor')).addClass('hidden');
    angular.element(document.querySelector('#game')).removeClass('hidden');
}

gameController.prototype.openProperties = function(itemId) {
    this.socket.emit('cmd', {command: 'item_info', args: [itemId]});
};

gameController.prototype.closeProperties = function() {
    angular.element(document.querySelector('#properties')).addClass('hidden');
    angular.element(document.querySelector('#game')).removeClass('hidden');
}


App.controller('lvlss.gameController', ['$scope', 'socket', '$location', 'manos', gameController]);
