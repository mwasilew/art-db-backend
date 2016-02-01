var app = angular.module('art', ['ngRoute']);

app.controller('Toolbar', ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {

    $rootScope.$on( "$routeChangeSuccess", function(event, next, current) {
        $scope.viewName = next.$$route ? next.$$route.controller : '';
    });

    $http.get('/api/token/').then(function(response) {
        $scope.auth = response.data;
    });

}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/builds/', {
            templateUrl: '/static/templates/build_list.html',
            controller: 'BuildList'
        })
        .when('/build/:buildId', {
            templateUrl: '/static/templates/build_detail.html',
            controller: 'BuildDetail'
        })
        .when('/manifests/', {
            templateUrl: '/static/templates/manifest_list.html',
            controller: 'ManifestList'
        })
        .when('/stats/', {
            templateUrl: '/static/templates/stats.html',
            controller: 'Stats'
        })
        .otherwise({
            redirectTo: '/manifests/'
        });
}]);


app.controller('ManifestList', ['$scope', '$http', '$routeParams', function($scope, $http, $routeParams) {
    var page = $routeParams.page || 1;

    $http.get('/api/manifest/', {cache: false, params: {page: page}})
        .then(function(response) {
            $scope.page = response.data;
        });

    $scope.search = function() {
        $http.get('/api/manifest/', {params: {'search': $scope.searchQuery, page: page}})
            .then(function(response) {
                $scope.page = response.data;
            });
    };

}]);

app.controller('BuildList', ['$scope', '$http', '$routeParams', function($scope, $http, $routeParams) {
    var page = $routeParams.page || 1;

    $http.get('/api/result/', {cache: false, params: {page: page}}).then(function(response) {
        $scope.page = response.data;
    });

    $scope.search = function() {
        $http.get('/api/result/', {params: {'search': $scope.searchQuery, page: page}})
            .then(function(response) {
                $scope.page = response.data;
            });
    };
}]);

app.controller('BuildDetail', ['$scope', '$http', '$routeParams', '$q', function($scope, $http, $routeParams, $q) {

    $http.get('/api/result/' + $routeParams.buildId + '/', {cache: false}).then(function(response) {
        $scope.build = response.data;

        $q.all([
            $http.get('/api/result/' + $routeParams.buildId + '/benchmarks/'),
            $http.get('/api/result/' + $routeParams.buildId + '/benchmarks_compare/')
        ]).then(function(response) {
            $scope.benchmarks = response[0].data;
            $scope.benchmarksCompare = response[1].data;
        });
    });

    $scope.filterBenchmarks = function(criteria) {
        return function(item) {
            if (!criteria) {
                return true;
            }
            if (item.benchmark.toLowerCase().indexOf(criteria.toLowerCase()) != -1 ||
                item.name.toLowerCase().indexOf(criteria.toLowerCase()) != -1) {
                return true;
            }
            return false;
        };
    };

    $scope.filterBenchmarksCompared = function(criteria) {
        return function( item ) {
            if (!criteria) {
                return true;
            }
            if (item.current.benchmark.toLowerCase().indexOf(criteria.toLowerCase()) != -1 ||
                item.current.name.toLowerCase().indexOf(criteria.toLowerCase()) != -1) {
                return true;
            }
            return false;
        };
    };

}]);

app.controller('Stats', ['$scope', '$http', '$routeParams', '$timeout', '$q', function($scope, $http, $routeParams, $timeout, $q) {

    $scope.redrawChart = function() {

        $scope.disabled = true;
        var options = {params: {
            branch: $scope.branch.branch_name,
            benchmark: _.map(_.filter($scope.benchmarkList, "selected"), "name")
        }};

        $http.get('/api/stats/', options).then(function(response) {

            var series = _.map(_.groupBy(response.data, "name"), function(data, name) {
                return {
                    name: name,
                    data: _.map(data, function(data) {
                        return [Date.parse(data.created_at), data.measurement];
                    })
                };
            });


            Highcharts.chart(
                document.getElementById('charts'), {
                    title: {
                        text: 'Benchmark results for branch: ' + $scope.branch.branch_name
                    },
                    xAxis: {
                        type: 'datetime',
                        dateTimeLabelFormats: {
                            month: '%e. %b',
                            year: '%b'
                        },
                        title: {
                            text: 'Date'
                        }
                    },
                    series: series
                });

            $scope.disabled = false;
        });
    };

    $q.all([
        $http.get('/api/branch/'),
        $http.get('/api/benchmark/')
    ]).then(function(response) {
        $scope.branchList = response[0].data;
        $scope.branch = $scope.branchList[0];

        $scope.benchmarkList = response[1].data;
        $scope.benchmarkList[0].selected = true;
    }).then($scope.redrawChart);

}]);
