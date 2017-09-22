page_history = {
    update: function () {
        var history = sessionStorage.history;
        if (history != "" && history != null) {
            var stack = history.toString().split(",");
            var insert = true;

            // Check if this url needs to be added:
            for (var i = stack.length - 1; i >= 0; i--) {
                if (stack[i] == document.URL) {
                    insert = false;
                }
            }
            if (insert) {
                stack.push(document.URL);
                sessionStorage.history = stack.toString();
            }
        }
        else {
            var stack = new Array();
            stack.push(document.URL);
            sessionStorage.history = stack.toString();
            console.log("page history started");
        }
        // console.log("page history:", get_page_history());
    },
    get: function () {
        var history = sessionStorage.history;

        if (history != "" && history != null) {
            var stack = history.toString().split(",");
            return stack
        }
        else {
        }
        return null;
    },
    pop: function () {
        var stack = this.get();
        var item = stack.pop();
        sessionStorage.history = stack.toString();
        return item;
    },
    clear: function(){
        sessionStorage.history = '';
    }
};

page_history.update();

