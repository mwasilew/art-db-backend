var app = angular.module('art', ['ngRoute']);

app.controller('Toolbar', ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope) {

    $rootScope.$on( "$routeChangeSuccess", function(event, next, current) {
        $scope.viewName = next.$$route ? next.$$route.controller : '';
    });

    $http.get('/api/token/').then(function(response) {
        $scope.auth = response.data;
    });

    $scope.show_user_dropdown = false;

    $scope.toggle_user_dropdown = function() {
        $scope.show_user_dropdown = !$scope.show_user_dropdown;
        var dropdown = document.getElementById('user-dropdown-menu');
        if ($scope.show_user_dropdown) {
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = '';
        }
    }

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

    $scope.get_environment_ids = function() {
        var selected = _.filter($scope.environments, function(env) { return env.selected });
        return _.map(selected, function(env) { return env.identifier} );
    }

    $scope.change = function() {

        var params = {
            branch: $scope.branch && $scope.branch.branch_name,
            environment: $scope.get_environment_ids()
        };
        var stats_endpoint;
        if ($scope.benchmark) {
            if ($scope.benchmark.type == 'benchmark_group' || $scope.benchmark.type == 'root_benchmark_group') {
                stats_endpoint = '/api/benchmark_group_summary/';
                params.benchmark_group = $scope.benchmark.name;
            } else {
                stats_endpoint = '/api/stats/';
                params.benchmark = $scope.benchmark.name;
            }
        }

        if (!(params.branch && params.environment.length > 0 && (params.benchmark || params.benchmark_group))) {
            return;
        }

        $scope.disabled = true;

        $location.search(params);

        $q.all(_.map($scope.get_environment_ids(), function(env) {
            var env_params = {};
            _.each(params, function(v, k) {
                env_params[k] = v;
            });
            env_params.environment = env;
            return $http.get(stats_endpoint, { params: env_params });
        })).then(function(multiple_responses) {
            var series = [];
            var i = -1;
            _.each(multiple_responses, function(response) {

                var env = response.config.params.environment;
                _.each(_.groupBy(response.data, "name"), function(data, name) {

                    i++;

                    // data itself
                    series.push({
                        name: name + ' (' + env + ')',
                        color: Highcharts.getOptions().colors[i],
                        zIndex: 1,
                        data: _.map(data, function(point) {
                            return {
                                x: Date.parse(point.created_at),
                                y: point.measurement,
                                stdev: point.stdev,
                                result_id: point.result,
                                build_id: point.build_id
                            };
                        })
                    });

                    if (data[0].stdev == undefined) {
                        // data has no stdev, skip the stdev data series
                        return;
                    }

                    // range of values, based on the standard deviation
                    series.push({
                        name: name + ' stdev (' + env + ')',
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

                });
            });

            var envs = _.join($scope.get_environment_ids(), ' x ');

            Highcharts.chart(
                document.getElementById('charts'), {
                    title: {
                        text: $scope.benchmark.label + ' on branch ' + $scope.branch.branch_name + '; ' + envs
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
                            var range = this.stdev && (3 * this.stdev).toFixed(2);
                            var stdev = this.stdev && this.stdev.toFixed(2);
                            var html = [
                                '<br/><p><strong>',
                                '<span style="color: ' + this.series.color + '">' + this.series.name + ':</span> ',
                                y + (this.stdev && (' ± ' + range + ' (st. dev.: ' + stdev + ')') || ''),
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

    $scope.toggleEnvironment = function(env_id) {
        for (var i = 0; i < $scope.environments.length; i++) {
            if ($scope.environments.identifier == env_id) {
                $scope.environments.selected = ! $scope.environments.selected;
            }
        }
        $scope.change();
    };

    $scope.reset = function() {
        $scope.branch = undefined;
        _.each($scope.environments, function(env) {
            env.selected = false;
        });
        $scope.benchmark = undefined;
        $location.search({});
        document.getElementById('charts').innerHTML = '';
    }

    $q.all([
        $http.get('/api/branch/'),
        $http.get('/api/benchmark/'),
        $http.get('/api/environments/')
    ]).then(function(response) {

        $scope.branchList = response[0].data;

        var benchmarkList = [];
        benchmarkList.push({ name: "/", label: 'Overall summary', type: 'root_benchmark_group' });
        _.each(_.groupBy(response[1].data, 'group'), function(benchmarks, group) {
            benchmarkList.push({ name: group, label: '  ' + group + ' (summary)', type: 'benchmark_group' });
            _.each(benchmarks, function(benchmark) {
                benchmark.type = 'benchmark';
                benchmark.label = '    ' + benchmark.name;
                benchmarkList.push(benchmark);
            });
        });
        $scope.benchmarkList = benchmarkList;

        $scope.environmentList = response[2].data;

        var defaults = {
            branch: $routeParams.branch,
            benchmark: $routeParams.benchmark || $routeParams.benchmark_group,
            environments: $routeParams.environment || []
        };

        if (defaults.branch) {
            $scope.branch = _.find($scope.branchList, ['branch_name', defaults.branch]);
        }
        $scope.environments = _.map($scope.environmentList, function(env) {
            env.selected = defaults.environments.indexOf(env.identifier) > -1;
            return env;
        });
        if (defaults.benchmark) {
            $scope.benchmark = _.find($scope.benchmarkList, ['name', defaults.benchmark]);
        }

    }).then($scope.change);

}]);
