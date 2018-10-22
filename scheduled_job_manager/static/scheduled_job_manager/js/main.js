// javascript for scheduled job manager


var refreshInterval = 8;
var dateFormat = 'LLL';

$(window.document).ready(function() {
	$("span.warning").popover({'trigger':'hover'});
    displayPageHeader();

    registerEvents()

    setInterval(fetchJobs, refreshInterval * 1000);
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
        loadSJMTable(jobs);
    }).on('sjm:JobListError', function (e, error) {
        Notify.error('Cannot load jobs: ' + error);
        $('.joblist').html('Our Apologies, but we cannot load jobs at this time.<br>' + error)
    });
};

var loadSJMTable = function (jobs) {
    displayJobList(jobs)
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


var displayJobList = function (jobs) {
    var source = $("#job-table-template").html(),
        template = Handlebars.compile(source),
        $content = $('.joblist');

    $.each(jobs.jobs, function () {
        this.launch_date = this.datetime_launch ? moment(this.datetime_launch).format(dateFormat) : null;
        this.exit_date = this.datetime_exit ? moment(this.datetime_exit).format(dateFormat) : null;
    });

    $content.html(template({
        jobs: jobs,
        refresh: refreshInterval
    }));

    refreshCountdown();
};


var refreshCountdown = function () {
    var $counter = $('.countdown'),
        count = refreshInterval;

    setInterval(function () {
        count -= 1;
        $counter.text(count);
    }, 1000);
};
