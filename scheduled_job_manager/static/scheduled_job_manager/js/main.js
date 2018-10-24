// javascript for scheduled job manager


var refreshInterval = 8;
var dateFormat = 'MM/DD h:mm:ssa';

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    registerEvents()

    fetchJobs()
    setInterval(fetchJobs, refreshInterval * 1000);

    fetchTasks()
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
        $('.joblist').html('Our Apologies, but we cannot load jobs at this time.<br>' + error)
    }).on('sjm:TaskList', function (e, tasks) {
        displayTaskList(tasks)
    }).on('sjm:TaskListError', function (e, error) {
        Notify.error('Cannot load tasks: ' + error);
        $('.tasklist').html('Our Apologies, but we cannot load tasks at this time.<br>' + error)
    }).on('click', '[data-cluster]', function (e) {
        startJob($(this).attr('data-job-cluster'), 
                 $(this).attr('data-job-member'),
                 $(this).attr('data-job-job'))
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
        }
    });
};


var displayJobList = function (jobs) {
    var source = $("#job-table-template").html(),
        template = Handlebars.compile(source),
        $content = $('.joblist');

    $.each(jobs.jobs, function () {
        var launch_moment = this.datetime_launch ? moment(this.datetime_launch) : null,
            exit_moment = this.datetime_exit ? moment(this.datetime_exit) : null;
        
        this.launch_date = launch_moment ? launch_moment.format(dateFormat) : null;
        this.exit_date = exit_moment ? exit_moment.format(dateFormat) : null;
        this.exit_output_abbreviated = (this.exit_output && this.exit_output.length > 20) ? this.exit_output.slice(0,20) + '...' : null;
        this.bad_exit = (this.exit_status != null && this.exit_status !== 0);
        this.runtime = (launch_moment && exit_moment) ? launch_moment.from(exit_moment, true) : null;
    });

    $content.html(template({
        jobs: jobs,
        refresh: refreshInterval
    }));

    $content.find('[data-toggle="tooltip"]').tooltip()
};


var displayTaskList = function (tasks) {
    var source = $("#task-table-row-template").html(),
        template = Handlebars.compile(source),
        $tasklist_tbody = $('.tasklist table tbody');

    $tasklist_tbody.html('');
    $.each(tasks. function () {
        var task = this

        $tasklist_tbody.append(template(task));
    });

    $tasklist_tbody.find('[data-toggle="tooltip"]').tooltip()
};


var refreshCountdown = function () {
    var $counter = $('.countdown'),
        count = refreshInterval;

    setInterval(function () {
        count -= 1;
        if (count < 0) {
            count = refreshInterval;
        }

        $counter.text(count);
    }, 1000);
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
