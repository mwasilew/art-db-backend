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
            redirectTo: '/stats/'
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

    $scope.getChangeClass = function(criteria) {
        if (criteria < -3) {
            return "success";
        }
        if (criteria >= -3 && criteria <= 3) {
            return "";
        }
        if (criteria > 3) {
            return "danger";
        }
    }

}]);


function forceArray(obj) {
    if (obj) {
      if (Array.isArray(obj)) {
          return obj;
      } else {
          return [obj];
      }
    } else {
        return [];
    }
}

function slug(s) {
    return s.toLowerCase().replace(/\W+/g, '-').replace(/-$/, '');
}

app.controller('Stats', ['$scope', '$http', '$routeParams', '$timeout', '$q', '$routeParams', '$location', function($scope, $http, $routeParams, $timeout, $q, $routeParams, $location) {

    $scope.get_environment_ids = function() {
        var selected = _.filter($scope.environments, function(env) { return env.selected });
        return _.map(selected, function(env) { return env.identifier} );
    }

    $scope.change = function() {

        $scope.disabled = true;

        for (var i = 0; i < $scope.benchmarks.length; i++) {
            var benchmark = $scope.benchmarks[i];

            // skip benchmarks that were already graphed
            if (benchmark.graphed) {
                continue;
            }

            var params = {
                branch: $scope.branch.branch_name,
                environment: $scope.get_environment_ids()
            };

            var stats_endpoint;
            if (benchmark.type == 'benchmark_group' || benchmark.type == 'root_benchmark_group') {
                stats_endpoint = '/api/benchmark_group_summary/';
                params.benchmark_group = benchmark.name;
            } else {
                stats_endpoint = '/api/stats/';
                params.benchmark = benchmark.name;
            }

            $q.all(_.map($scope.get_environment_ids(), function(env) {
                var env_params = {};
                _.each(params, function(v, k) {
                    env_params[k] = v;
                });
                env_params.environment = env;
                return $http.get(stats_endpoint, { params: env_params });
            })).then(function(data_by_env) {
                var bname = data_by_env[0].config.params.benchmark ||
                    data_by_env[0].config.params.benchmark_group;

                var benchmark = _.find($scope.benchmarks, ['name', bname]);
                $scope.drawChart(benchmark, $scope.branch, data_by_env);
                benchmark.graphed = true;
            });
        }

        $location.search({
            branch: $scope.branch.branch_name,
            environment: $scope.get_environment_ids(),
            benchmark: _.map($scope.benchmarks, 'name')
        });

        $scope.disabled = false;
    };

    $scope.addBenchmark = function() {
        var benchmark = $scope.benchmark;
        $scope.benchmarks.push(benchmark);
        $scope.change();
        $scope.benchmark = undefined;
    }

    $scope.removeBenchmark = function(benchmark) {
        document.getElementById('chart-' + slug(benchmark.label)).remove();
        _.remove($scope.benchmarks, benchmark);
        $scope.change();
    }

    $scope.drawChart = function(benchmark, branch, env_data) {
        var series = [];
        var i = -1;

        _.each(env_data, function(response) {

            var env = response.config.params.environment;

            _.each(_.groupBy(response.data, "name"), function(data, name) {

                i++;

                // data itself
                series.push({
                    name: name + ' (' + env + ')',
                                  type: 'spline',
                                  color: Highcharts.getOptions().colors[i],
                                  zIndex: 1,
                                  data: _.map(data, function(point) {
                                      return {
                                          x: Date.parse(point.created_at),
                                          y: point.measurement,
                                          min: _.min(point.values),
                                          max: _.max(point.values),
                                          result_id: point.result,
                                          build_id: point.build_id
                                      };
                                  })
                                  });

                    if (data[0].values == undefined) {
                        // data does not have multiple values, skip the range
                        // data series
                        return;
                    }

                    // range of values, based on the standard deviation
                    series.push({
                        name: name + ' range (' + env + ')',
                                      type: 'areasplinerange',
                                      color: Highcharts.getOptions().colors[i],
                                      lineWidth: 0,
                                      linkedTo: ':previous',
                                      fillOpacity: 0.3,
                                      zIndex: 0,
                                      data: _.map(data, function(point) {
                                          return [
                                              Date.parse(point.created_at),
                                              _.min(point.values),
                                              _.max(point.values)
                                          ]
                                      })
                                      });

                        });
        });

        var charts = document.getElementById('charts');

        var this_chart = document.createElement('div');
        this_chart.className = 'panel panel-default';
        this_chart.id = 'chart-' + slug(benchmark.label);
        this_chart.innerHTML = '<i class="fa fa-cog fa-spin"></i>';
        charts.appendChild(this_chart);

        Highcharts.chart(
                this_chart, {
                    chart: {
                        zoomType: "xy"
                    },
                    title: {
                        text: benchmark.label + ' on branch ' + branch.branch_name
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
                            var min = this.min && this.min.toFixed(2);
                            var max = this.max && this.max.toFixed(2);
                            var range = '';
                            if (this.min && this.max) {
                                range = _.join([
                                        '<br/>',
                                        'Range: ',
                                        this.min.toFixed(2),
                                        ' — ',
                                        this.max.toFixed(2)
                                ], '');
                            }
                            var html = [
                                '<br/><p><em>',
                                '<span style="color: ' + this.series.color + '">' + this.series.name + '</span></em><br/> ',
                                '<strong>',
                            'Mean: ' + y,
                            '</strong>',
                            range,
                            '</p>',
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
                    legend: {
                        maxHeight: 100
                    },
                    series: series
                });
    }

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
        benchmarkList.push({ name: "/", label: 'Overall summary', padding: '', type: 'root_benchmark_group' });
        _.each(_.groupBy(response[1].data, 'group'), function(benchmarks, group) {
            benchmarkList.push({ name: group, label: group + ' (summary)', padding: '  ', type: 'benchmark_group' });
            _.each(benchmarks, function(benchmark) {
                benchmark.type = 'benchmark';
                benchmark.label = benchmark.name;
                benchmark.padding = '    ';
                benchmarkList.push(benchmark);
            });
        });
        $scope.benchmarkList = benchmarkList;

        $scope.environmentList = response[2].data;

        var defaults;
        if ($routeParams.branch || $routeParams.benchmark || $routeParams.environment) {
            defaults = {
                branch: $routeParams.branch,
                benchmarks: forceArray($routeParams.benchmark),
                environments: forceArray($routeParams.environment)
            };
        } else {
            defaults = {
                branch: 'master',
                benchmarks: ['/'],
                environments: _.map($scope.environmentList, function(env) {
                    return env.identifier;
                })
            };
        }

        if (defaults.branch) {
            $scope.branch = _.find($scope.branchList, ['branch_name', defaults.branch]);
        }
        $scope.environments = _.map($scope.environmentList, function(env) {
            env.selected = defaults.environments.indexOf(env.identifier) > -1;
            return env;
        });
        $scope.benchmarks = _.map(defaults.benchmarks, function(b) {
            return _.find($scope.benchmarkList, ['name', b])
        });

    }).then($scope.change);

}]);
