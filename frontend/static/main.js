var app = angular.module('art', ['ngRoute']);

app.controller('Toolbar', ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {

    $rootScope.$on( "$routeChangeSuccess", function(event, next, current) {
        $scope.viewName = next.$$route.controller;
    });

    $http.get('/api/token/').then(function(response) {
        $scope.auth = response.data;
    });

}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '/static/templates/build_list.html',
            controller: 'BuildList'
        })
        .when('/build/:buildId', {
            templateUrl: '/static/templates/build_detail.html',
            controller: 'BuildDetail'
        });
}]);

app.controller('BuildList', ['$scope', '$http', '$route', function($scope, $http, $route) {

    $http.get('/api/build/', {cache: false}).then(function(response) {
        $scope.builds = response.data;
    });

    $scope.search = function() {
        $http.get('/api/build/', {params: {'name': $scope.searchQuery }})
            .then(function(response) {
                $scope.builds = response.data;
            });
    };
}]);

app.controller('BuildDetail', ['$scope', '$http', '$routeParams', function($scope, $http, $routeParams) {

    $http.get('/api/build/' + $routeParams.buildId + '/', {cache: false}).then(function(response) {
        $scope.build = response.data;
    });

}]);
