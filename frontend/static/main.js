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

         $http.get('/api/settings/manifest_settings/').then(function(response) {
             $scope.settings = response.data;
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

    $scope.isEmpty = _.isEmpty;

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

            var series = [];
            var i = 0;
            _.each(_.groupBy(response.data, "name"), function(data, name) {

                // data itself
                series.push({
                    name: name,
                    color: Highcharts.getOptions().colors[i],
                    zIndex: 1,
                    data: _.map(data, function(data) {
                        return {
                            x: Date.parse(data.created_at),
                            y: data.measurement,
                            stdev: data.stdev,
                            result_id: data.result,
                            build_id: data.build_id
                        };
                    })
                });

                // range of values, based on the standard deviation
                series.push({
                    name: name + ' stdev',
                    type: 'arearange',
                    color: Highcharts.getOptions().colors[i],
                    lineWidth: 0,
                    linkedTo: ':previous',
                    fillOpacity: 0.3,
                    zIndex: 0,
                    data: _.map(data, function(point) {
                        return [
                            Date.parse(point.created_at),
                            // 99.73% of values are in the range (mean ± 3 * stdev)
                            point.measurement - 3 * point.stdev,
                            point.measurement + 3 * point.stdev
                        ]
                    })
                });

                i++;
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
                    tooltip: {
                        useHTML: true,
                        pointFormatter: function() {
                            if (this.series.type == 'arearange') {
                                return '';
                            }
                            var y = this.y.toFixed(2);
                            var range = (3 * this.stdev).toFixed(2);
                            var stdev = this.stdev.toFixed(2);
                            var html = [
                                '<br/><p><strong>',
                                '<span style="color: ' + this.series.color + '">' + this.series.name + ':</span> ',
                                y + ' ± ' + range + ' (st. dev.: ' + stdev + ')',
                                '</strong></p>',
                                '<p>',
                                '<a href="#/build/' + this.result_id + '">See details for build #' + this.build_id + '</a>',
                                '</p>'
                            ]
                            return _.join(html, '');
                        }
                    },
                    plotOptions: {
                        series: {
                            cursor: 'pointer',
                            point: {
                                events: {
                                    click: function (e) {
                                        location.href = '#/build/' + this.result_id;
                                    }
                                }
                            },
                            marker: {
                                lineWidth: 1
                            }
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
        $scope.benchmarkList = response[1].data;

        var defaults = {
            branch: $routeParams.branch || $scope.branchList[0]['branch_name'],
            benchmark: $routeParams.benchmark || $scope.benchmarkList[0]['name']
        };

        $scope.branch = _.find($scope.branchList, ['branch_name', defaults.branch]);
        $scope.benchmark = _.find($scope.benchmarkList, ['name', defaults.benchmark]);

    }).then($scope.change);

}]);
