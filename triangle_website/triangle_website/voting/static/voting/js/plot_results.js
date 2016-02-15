function getResultChartData(results) {
	var chartLabels = [];
	var dataSet = [];
	for(var resp in results) {
		chartLabels.push(resp);
		dataSet.push(results[resp]);
	}
	return {
		labels: chartLabels,
		datasets: [{
			label: "Main",
			fillColor: "rgba(151,187,205,0.5)",
			strokeColor: "rgba(151,187,205,0.8)",
			highlightFill: "rgba(151,187,205,0.75)",
			highlightStroke: "rgba(151,187,205,1)",
			data: dataSet
		}]
	}
}

function plotResults(chartId, data) {
	var ctx = document.getElementById(chartId).getContext("2d");
	return new Chart(ctx).Bar(getResultChartData(data, {"responsive":true}));
}

var questions = $('[ques_id]')
questions.each(function(quesNum)
{
	var question = $(questions[quesNum])
	var choices = question.find('[choice]')
	var data = {}
	choices.each(function(choiceI)
	{
		var choice = $(choices[choiceI])
		data[choice.attr('choice_text')] = choice.attr('vote_count')
	});
	var barChart = plotResults("chart" + question.attr('ques_id'), data);
});


