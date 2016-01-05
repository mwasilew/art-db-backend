var app = angular.module('art', ['ngMaterial']);

app.controller('Toolbar', ['$scope', '$http', function($scope, $http) {

    $http.get('/api/token/').then(function(response) {
        $scope.auth = response.data;
    });

}]);

app.controller('JobsList', ['$scope', '$http', function($scope, $http) {

    $http.get('/api/build/').then(function(response) {
        $scope.builds = response.data;
    });

}]);

