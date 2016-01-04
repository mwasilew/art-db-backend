var app = angular.module('art', ['ngMaterial']);

app.controller('Toolbar', ['$scope', '$http', function($scope, $http) {

    $http.get('/api/token/').then(function(response) {
        $scope.token = response.data.key;
    });

}]);

