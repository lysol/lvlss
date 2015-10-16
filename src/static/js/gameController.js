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
    this.player = {name: '', credits: 0}

    $scope.$on('clientcrap', function(evt, data) {
        self.addCrap(data.lines);
    });

    $scope.$on('location', function(evt, data) {
        self.location = data.area;
    });

    $scope.$on('location-inventory', function(evt, data) {
        self.location_items = data.inventory;
    });

    $scope.$on('location-areas', function(evt, data) {
        self.location_areas = data.areas;
    });

    $scope.$on('inventory', function(evt, data) {
        self.inventory = data.inventory;
    });

    $scope.$on('player-status', function(evt, data) {
        self.player.name = data.player.name;
        self.player.credits = data.player.credits;
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

gameController.prototype.copyItem = function(itemId) {
    this.socket.emit('cmd', {command: 'copy', args: [itemId]});
};

gameController.prototype.editScript = function(itemId) {
    this.manos.emit('edit-script', {itemId: itemId});
};

gameController.prototype.openProperties = function(itemId) {
    this.socket.emit('cmd', {command: 'item_info', args: [itemId]});
};

App.controller('lvlss.gameController', ['$scope', 'socket', '$location', 'manos', gameController]);
