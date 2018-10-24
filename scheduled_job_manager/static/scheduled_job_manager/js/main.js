// javascript for scheduled job manager


var jobRefreshInterval = 8;
var taskRefreshInterval = 15;
var dateFormat = 'MM/DD h:mm:ssa';

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    registerEvents();

    fetchJobs();
    fetchTasks();
});


var displayPageHeader = function() {
    var source = $("#page-top").html();
    var template = Handlebars.compile(source);
    $("#top_banner").html(template({
        netid: window.user.netid
    }));
};


var registerEvents = function () {
    $(document).on('sjm:JobList', function (e, jobs) {
        displayJobList(jobs)
    }).on('sjm:JobListError', function (e, error) {
        Notify.error('Cannot load jobs: ' + error);
        $('.joblist table tbody').html('<tr><td>Our Apologies, but we cannot load jobs at this time.</td></tr><tr><td>' + error + '</td></tr>')
    }).on('sjm:TaskList', function (e, tasks) {
        displayTaskList(tasks)
    }).on('sjm:TaskListError', function (e, error) {
        Notify.error('Cannot load tasks: ' + error);
        $('.tasklist table tbody').html('<tr><td>Our Apologies, but we cannot load tasks at this time.</td></tr><tr><td>' + error + '</td></tr>')
    }).on('click', 'a.launch-job', function (e) {
        var $link = $(this),
            cluster = $link.attr('data-job-cluster'),
            label = $link.attr('data-job-label'),
            $select = $('#members-' + cluster + '-' + label),
            member = $('option:selected', $select).val();

        startJob(cluster, member, label);
    }).on('sjm:JobLaunch', function (e, result) {
        Notify.success('Job Start: ' + result);
    }).on('sjm:JobLaunchError', function (e, error) {
        Notify.error('Cannot start job: ' + error);
    });
};


var fetchJobs = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        $content = $(document);

    $content.html($('#sjm-loading').html());

    $.ajax({
        url: "api/v1/jobs/",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $content.trigger('sjm:JobList', [results]);
        },
        error: function(xhr, status, error) {
            $content.trigger('sjm:JobListError', [error]);
        },
        complete: function() {
            var interval = refreshCountdown($('.job_countdown'),
                                            jobRefreshInterval);

            setTimeout(function () {
                clearInterval(interval);
                fetchJobs();
            }, jobRefreshInterval * 1000);
        }
    });
};


var fetchTasks = function () {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        $content = $(document);

    $.ajax({
        url: "api/v1/tasks/",
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $content.trigger('sjm:TaskList', [results]);
        },
        error: function(xhr, status, error) {
            $content.trigger('sjm:TaskListError', [error]);
        },
        complete: function() {
            var interval = refreshCountdown($('.task_countdown'),
                                            taskRefreshInterval);

            setTimeout(function () {
                clearInterval(interval);
                fetchTasks();
            }, taskRefreshInterval * 1000);
        }
    });
};


var startJob = function (job_cluster, job_member, job_label) {
    var csrf_token = $("input[name=csrfmiddlewaretoken]")[0].value,
        $content = $(document);

    $.ajax({
        url: "api/v1/launch/" + job_cluster + '/' + job_member + '/' + job_label,
        dataType: "JSON",
        type: "GET",
        accepts: {html: "application/json"},
        headers: {
            "X-CSRFToken": csrf_token
        },
        success: function(results) {
            $content.trigger('sjm:JobLaunch', [results]);
        },
        error: function(xhr, status, error) {
            $content.trigger('sjm:JobLaunchError', [error]);
        }
    });
}


var displayJobList = function (jobs) {
    var source = $("#job-table-row-template").html(),
        template = Handlebars.compile(source),
        $content = $('.joblist table tbody');

    $.each(jobs.jobs, function () {
        var launch_moment = this.datetime_launch ? moment(this.datetime_launch) : null,
            exit_moment = this.datetime_exit ? moment(this.datetime_exit) : null;
        
        this.launch_date = launch_moment ? launch_moment.format(dateFormat) : null;
        this.exit_date = exit_moment ? exit_moment.format(dateFormat) : null;
        this.exit_output_abbreviated = (this.exit_output && this.exit_output.length > 20) ? this.exit_output.slice(0,20) + '...' : null;
        this.bad_exit = (this.exit_status != null && this.exit_status !== 0);
        this.runtime = (launch_moment && exit_moment) ? launch_moment.from(exit_moment, true) : null;
        this.running_time = (launch_moment) ? launch_moment.from(moment(), true) : null;
    });

    $content.html('');
    $.each(jobs.jobs, function () {
        $content.append(template(this));
    });

    $content.find('[data-toggle="tooltip"]').tooltip()
};


var displayTaskList = function (tasks) {
    var source = $("#task-table-row-template").html(),
        template = Handlebars.compile(source),
        $tasklist_tbody = $('.tasklist table tbody'),
        row_contexts = {},
        current_cluster;

    $tasklist_tbody.html('');

    // coalesce cluster/member/jobs
    $.each(tasks.tasks, function () {
        if (row_contexts.hasOwnProperty(this.cluster)) {
            if (row_contexts[this.cluster].hasOwnProperty(this.label)) {
                row_contexts[this.cluster][this.label].push(this.member);
            } else {
                row_contexts[this.cluster][this.label] = [this.member];
            }
        } else {
            row_contexts[this.cluster] = {};
            row_contexts[this.cluster][this.label] = [this.member];
        }
    });

    $.each(row_contexts, function (cluster) {
        $.each(this, function (job_label) {
            $tasklist_tbody.append(template({
                cluster: (!current_cluster || current_cluster != cluster) ? cluster : '',
                cluster_label: cluster,
                label: job_label,
                members: this
            }));

            current_cluster = cluster;
        });
    });

    $tasklist_tbody.find('[data-toggle="tooltip"]').tooltip();
};


var refreshCountdown = function ($node, interval) {
    var count = interval;

    $node.text(count);
    return setInterval(function () {
        count -= 1;
        if (count < 0) {
            count = interval;
        }

        $node.text(count);
    }, 1000);
};
