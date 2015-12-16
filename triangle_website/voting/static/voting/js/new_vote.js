var Question = function() {
	this.name = "";
	this.choices = ["", ""];
}

/**
function getQuestion() {
	return new Question();
}**/

var formApp = angular.module("formApp", []);
formApp.controller("mainControl", function($scope){
	$scope.questions = [new Question()];
	$scope.useCode = true;
	// This is a hacky thing since angular does not allow use of the new operator in expressions but does allow function calls.
	// Also, this function must be here so that Angular will register the new object.
	$scope.getQuestion = function() {
		return new Question();
	}
});