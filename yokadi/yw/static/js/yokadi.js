function Task(data) {
    this.url = ko.observable(data.uri);
    this.id = ko.observable(data.id);
    this.title = ko.observable(data.title);
    this.description = ko.observable(data.description);
}

function ProjectWithTask(data) {
    this.url = ko.observable(data.project.uri);
    this.id = ko.observable(data.project.id);
    this.name = ko.observable(data.project.name);
    this.status = ko.observable(data.project.status);
    this.tasks = ko.observableArray(data.tasks)
}

function ProjectListViewModel() {
    var self = this
    self.projects = ko.observableArray();
    $.getJSON('http://localhost:5000/api/tasks?group_by_project=1', function(allData) {
        var mappedProjects = $.map(allData, function(project) { return new ProjectWithTask(project) });
        self.projects(mappedProjects);
    });
}
ko.applyBindings(new ProjectListViewModel());
