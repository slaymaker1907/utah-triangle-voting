var Question = function() {
	this.name = "";
	this.choices = ["1", "2"];
}

var formApp = angular.module("formApp", []);
formApp.controller("mainControl", function($scope){
	$scope.questions = [new Question(), new Question, new Question()];
});