/**var data = {
	labels: ["Zion", "Bryce Canyon", "Grand Junction"],
	datasets: [{
			label: "Main",
			fillColor: "rgba(151,187,205,0.5)",
			strokeColor: "rgba(151,187,205,0.8)",
			highlightFill: "rgba(151,187,205,0.75)",
			highlightStroke: "rgba(151,187,205,1)",
			data: [7, 10, 3]
	}]
}
**/

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

var data1 = {"Zion":7, "Bryce Canyon":10, "Grand Junction":3}
var barChart1 = plotResults("chart1", data1);

var data2 = {"Yes":17, "No":3}
var barChart2 = plotResults("chart2", data2);