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
            controller: 'BuildList',
            reloadOnSearch: false
        })
        .when('/build/:buildId', {
            templateUrl: '/static/templates/build_detail.html',
            controller: 'BuildDetail',
            reloadOnSearch: false
        })
        .when('/manifests/', {
            templateUrl: '/static/templates/manifest_list.html',
            controller: 'ManifestList',
            reloadOnSearch: false
        })
        .when('/manifests/reduced/', {
            templateUrl: '/static/templates/manifest_reduced_list.html',
            controller: 'ManifestReducedList',
            reloadOnSearch: false
        })
        .when('/stats/', {
            templateUrl: '/static/templates/stats.html',
            controller: 'Stats',
            reloadOnSearch: false
        })
        .otherwise({
            redirectTo: '/manifests/'
        });
}]);

app.directive('pagination', ['$route', '$httpParamSerializer', '$location', function($route, $httpParamSerializer, $location) {
    return {
        restrict: 'E',
        scope: {
            page: '='
        },
        templateUrl: '/static/templates/_pagination.html',
        link: function(scope, elem, attrs) {

            scope.goNext = function() {
                $location.search("page", scope.page.page.next);
                $route.reload();
            };

            scope.goBack = function() {
                $location.search("page", scope.page.page.previous);
                $route.reload();
            };
        }
    };
}]);


app.controller(
    'ManifestList',

    ['$scope', '$http', '$routeParams', '$location',

     function($scope, $http, $routeParams, $location) {

         var params = {
             'search': $routeParams.search,
             'page': $routeParams.page
         };

         $http.get('/api/manifest/', {params: params}).then(function(response) {
             $scope.page = response.data;
         });

         $scope.search = $routeParams.search;

         $scope.makeSearch = function() {
             $location.search({'search': $scope.search || null});

             $http.get('/api/manifest/', {params: {'search': $scope.search}})
                 .then(function(response) {
                     $scope.page = response.data;
                 });
         };
     }]
);

app.controller(
    'ManifestReducedList',

    ['$scope', '$http', '$routeParams', '$location',

     function($scope, $http, $routeParams, $location) {

         var params = {
             'search': $routeParams.search,
             'page': $routeParams.page
         };

         $http.get('/api/manifest_reduced/', {params: params}).then(function(response) {
             $scope.page = response.data;
         });

         $scope.search = $routeParams.search;

         $scope.makeSearch = function() {
             $location.search({'search': $scope.search || null});

             $http.get('/api/manifest_reduced/', {params: {'search': $scope.search}})
                 .then(function(response) {
                     $scope.page = response.data;
                 });
         };
     }]
);


app.controller(
    'BuildList',

    ['$scope', '$http', '$routeParams', '$location',

     function($scope, $http, $routeParams, $location) {

         var params = {
             'search': $routeParams.search,
             'page': $routeParams.page
         };

         $http.get('/api/result/', {params: params}).then(function(response) {
             $scope.page = response.data;
         });

         $scope.search = $routeParams.search;

         $scope.makeSearch = function() {
             $location.search({'search': $scope.search || null});

             $http.get('/api/result/', {params: {'search': $scope.search}})
                 .then(function(response) {
                     $scope.page = response.data;
                 });
         };
     }]
);

app.controller('BuildDetail', ['$scope', '$http', '$routeParams', '$q', '$routeParams', '$location', function($scope, $http, $routeParams, $q, $routeParams, $location) {

    $scope.queryBenchmarks = $routeParams.benchmarks || "";

    $q.all([
        $http.get('/api/result/' + $routeParams.buildId + '/'),
        $http.get('/api/result/' + $routeParams.buildId + '/benchmarks/'),
        $http.get('/api/result/' + $routeParams.buildId + '/benchmarks_compare/'),
        $http.get('/api/result/' + $routeParams.buildId + '/baseline/')
    ]).then(function(response) {
        $scope.build = response[0].data;
        $scope.benchmarks = response[1].data;
        $scope.benchmarksCompare = response[2].data;
        $scope.baseline = response[3].data;
    });

    $scope.resubmit = function(testJob) {
        testJob.refresh = false;
        $scope.testJobUpdate = true;
        $http.get('/api/testjob/' + testJob.id + '/resubmit/').then(function(response) {
            $scope.build.test_jobs = response.data;
            $scope.testJobUpdate = false;
        });
    };

    $scope.filterBenchmarks = function(criteria) {
        $location.search({'benchmarks': criteria || null});

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
        $location.search({'benchmarks': criteria || null});

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

app.controller('Stats', ['$scope', '$http', '$routeParams', '$timeout', '$q', '$routeParams', '$location', function($scope, $http, $routeParams, $timeout, $q, $routeParams, $location) {

    $scope.change = function() {

        $scope.disabled = true;

        var params = {
            branch: $scope.branch.branch_name,
            benchmark: $scope.benchmark.name
        };

        $location.search(params);

        var options = {params: params};

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

        var defaults = {
            branch: $routeParams.branch || "master",
            benchmark: $routeParams.benchmark || "NBody"
        };

        $scope.branchList = response[0].data;
        $scope.benchmarkList = response[1].data;

        $scope.branch = _.find($scope.branchList, ['branch_name', defaults.branch]);
        $scope.benchmark = _.find($scope.benchmarkList, ['name', defaults.benchmark]);

    }).then($scope.change);

}]);
