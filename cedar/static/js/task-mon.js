/*
Celery task monitoring.
 */
var task_mon_poll_interval = 3000; // millisecs
var task_mon_debug = false;
var task_mon_auto_start = true;

$(document).ready(function (evt) {
    $('.tooltipped-management').tooltip();

    // Set up click listeners and activity monitors:
    $('a.task-trigger').on('click', function (e) {
        let trigger = new Trigger(this);

        if (trigger.is_running()) {
            e.preventDefault(); // stop the jump
            message("There is a task already running for this account.");
        }
        else {
            e.preventDefault(); // stop the jump/click
            launch_task(trigger);
        }
    });
    // Set up task killer click listener:
    $('a.task-killer').on('click', function (e) {
        e.preventDefault(); // stop the jump
        let task_id = $(this).attr('data-task-id');
        let trigger = findTrigger(task_id); //use trigger class to get the revoke url
        $.get(trigger.get_revoke_url(),
            // revoke retrieved:
            function (data) {
                message("Succesfully requested revoke for task id " + task_id.toString());
                message(data);
            }
        ).fail(function () {
            var msg = 'Failed to stop the harvest task id:' + task_id.toString();
            message(msg);
        });
    });

    // start initial status checks and monitors:
    if (task_mon_auto_start) {
        check_triggers();   // once for on first load.
    }
    setInterval(function(){
        if (task_mon_auto_start) {
            message("check triggers");
            check_triggers();
        }
    }, 5000);

    // Suppress the onclick event for task-mon li elements.
    $('li.task-mon').click(function (e) {
        console.log('Clicked the harvest button!');
        e.stopPropagation();
    });

});

function launch_task(trigger){
    $.get(trigger.trigger_url,
        // success
        function (data) {
            message('task launch response:', data);
            if (data.ok == 'true') {
                poll_for_launch_task_status(trigger, data.task_id);
            }
            else {
                let msg = 'Task not started successfully :(';
                message(msg);
            }
        }
    ).done(function () {
        // A second success function
    }).fail(function () {
        let msg = 'Task not started successfully :(';
        message(msg);
    });
}

function poll_for_launch_task_status(trigger, task_id){
    trigger.set_pending_status(true);
    trigger.set_launch_task_id(task_id);

    let status_url_for_launch = trigger.get_launch_status_url();

    message("request launch task status:", status_url_for_launch);

    // Update the trigger's task_id with the chord's task_id and start monitoring:
    $.get(status_url_for_launch, function (data) {
        message("task parent status url response", data);

        if (data.task.result) {
            message("launch task status query came back with result. Proceed to monitor task.");
            trigger.set_task_id(data.task.result);
            poll_for_task_status(trigger);

            let msg = 'Task started successfully!';
            message(msg);
        }
        else if (data.task.id){
            message("launch task status query came back without result but has an ID. Try again.");
            setTimeout(function(){
                poll_for_launch_task_status(trigger,data.task.id);
            }, task_mon_poll_interval/2);
            return;
        }
        else {
            let msg = 'Task status is not executing.';
            message(msg);
            trigger.set_pending_status(false);
        }
    }).fail(function () {
            let msg = 'Failed to request task launch.';
            message(msg);
            trigger.set_pending_status(false);
    });
}

function poll_for_task_status(trigger) {
    // Run get. If status still running then set next timeout and quit.
    // If status NOT running, return.
    trigger.set_run_status(true);

    $.get(trigger.get_status_url(),
        // status retrieved:
        function (data) {
            var stop_monitoring = false;
            // console.log(data);
            if (data.task.status == 'SUCCESS') {
                message('Task succeeded!');
                stop_monitoring = true;
            }
            else if (data.task.status == 'FAILURE') {
                message('Task failed :(');
                console.error("Task traceback:", data.task.traceback);
                stop_monitoring = true;
            }
            else if (data.task.status == 'REVOKED') {
                message('Task was revoked.');
                stop_monitoring = true;
            }
            else {
                msg = 'Task status is:' + data.task.status.toString();
                message(msg);
            }
            if (stop_monitoring) {
                // clear_monitoring_status(mail_account_id);
                trigger.stop_monitoring();
            }
            else {
                setTimeout(function () {
                    poll_for_task_status(trigger)
                }, task_mon_poll_interval);
            }
        }
    ).fail(function () {
        var msg = 'Failed to check status of task:' + trigger.get_task_id();
        message(msg);
        trigger.stop_monitoring();
    });
}

class Trigger {
    constructor(node) {
        this.node = node;
        this.trigger_url = $(this.node).attr('data-task-trigger-url')
    }

    _get_url_from_mask(url_mask, task_id) {
        return url_mask.replace('placeholder', task_id.toString());
    }

    set_run_status(status) {
        // status == true : set task to running.
        if (status) {
            $(this.node).addClass('task-running');
            if (this.is_pending()) {
                this.set_pending_status(false);
            }
            this.set_pulsar(true);
        }
        else {
            $(this.node).removeClass('task-running');
            this.set_pulsar(false);
        }
    }

    set_pending_status(status) {
        // status == true : set task to pending.
        if (status) {
            $(this.node).addClass('pending');
            if (this.is_running()) {
                this.set_run_status(false);
            }
        }
        else {
            $(this.node).removeClass('pending');
        }
    }

    set_launch_task_id(task_id) {
        $(this.node).attr('data-launch-task-id', task_id);
        $(this.get_task_killer_node()).attr('data-launch-task-id', task_id);
    }

    get_launch_task_id() {
        return $(this.node).attr('data-launch-task-id');
    }

    set_task_id(task_id) {
        $(this.node).attr('data-task-id', task_id);
        $(this.get_task_killer_node()).attr('data-task-id', task_id);
    }

    get_task_id() {
        return $(this.node).attr('data-task-id');
    }

    is_running() {
        if ($(this.node).hasClass('task-running')) {
            return true;
        }
        else {
            return false;
        }
    }

    is_pending() {
        if ($(this.node).hasClass('pending')) {
            return true;
        }
        else {
            return false;
        }
    }

    get_status_url() {
        return this._get_url_from_mask(
            $(this.node).attr('data-task-status-url-mask'),
            this.get_task_id());
    }

    get_launch_status_url() {
        return this._get_url_from_mask(
            $(this.node).attr('data-task-status-url-mask'),
            this.get_launch_task_id());
    }

    get_parent_status_url() {
        /*
         lame hack to get around the mysterious pending null tasks:
         */
        return $(this.node).attr('data-task-parent-status-url');
    }

    get_revoke_url() {
        return this._get_url_from_mask(
            $(this.node).attr('data-task-revoke-url-mask'),
            this.get_task_id());
    }

    stop_monitoring() {
        this.set_run_status(false);
        this.set_pending_status(false);
        this.set_task_id('');
    }

    get_task_killer_node() {
        return $(this.node)
            .siblings('.task-killer');
    }

    get_pulsar_span(){
        var span = $('span[data-task-trigger-url="' + this.trigger_url + '"]');
        if (span){
            return span;
        }
        else {
            return null;
        }
    }

    set_pulsar(status){
        let span = this.get_pulsar_span();
        if (span){
            if (status) {
                $(span).addClass('pulsar');
            }
            else {
                $(span).removeClass('pulsar');
            }

        }
        else {
            // do nothing, no span found.
        }
    }
}

function findTrigger(task_id){
    return new Trigger(
        $('a[data-task-id="'+ task_id +'"')
    );
}

function message(){
    /* use it like console.log */
    if (task_mon_debug){
        console.debug(arguments);
    }
}

function check_triggers(){
    $('a.task-trigger').each(function(){
        let trigger = new Trigger($(this));
        $.get(trigger.get_parent_status_url(), function (data) {
            // console.log("start up data:", data);
            if (data.task.id) {
                trigger.set_task_id(data.task.id);
                poll_for_task_status(trigger);
            }
        }).fail(function () {
            // I think this will happen if the trigger state
            // is changed by one of the other monitors and messes
            // up its ability to build a query url.
            let msg = 'Failed to check trigger task state.';
            message(msg);
        });

    })
}
