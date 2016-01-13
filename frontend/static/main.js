var app = angular.module('art', ['ngRoute']);

app.controller('Toolbar', ['$scope', '$http', function($scope, $http) {
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
        .when('/stats/', {
            templateUrl: '/static/templates/stats.html',
            controller: 'Stats'
        })
        .when('/build/:buildId', {
            templateUrl: '/static/templates/build_detail.html',
            controller: 'BuildDetail'
        });
}]);


app.controller('BuildList', ['$scope', '$http', function($scope, $http) {

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

app.controller('Stats', ['$scope', '$http', '$routeParams', '$timeout', function($scope, $http, $routeParams, $timeout) {

    $timeout(function() {
        Highcharts.chart(
            document.getElementById('charts'), {
                title: {
                    text: 'Monthly Average Temperature',
                    x: -20 //center
                },
                subtitle: {
                    text: 'Source: WorldClimate.com',
                    x: -20
                },
                text: 'Monthly Average Temperature',
                series: [{
                    name: 'Tokyo',
                    data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
                }, {
                    name: 'New York',
                    data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
                }, {
                    name: 'Berlin',
                    data: [-0.9, 0.6, 3.5, 8.4, 13.5, 17.0, 18.6, 17.9, 14.3, 9.0, 3.9, 1.0]
                }, {
                    name: 'London',
                    data: [3.9, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
                }]
            });
    });
}]);
