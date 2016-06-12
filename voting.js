/**
 * Retrieves all the rows in the active spreadsheet that contain data and logs the
 * values for each row.
 * For more information on using the Spreadsheet API, see
 * https://developers.google.com/apps-script/service_spreadsheet
 */

report = ""

function readRows() {
	var sheet = SpreadsheetApp.getActiveSheet();
	var rows = sheet.getDataRange();
	var numRows = rows.getNumRows();
	var values = rows.getValues();


	if (!numRows > 1) {
		error("No voting data");
		return;
	}
	var meta = processHeaders(values[0])
	var voteDb = {}
	meta.positions.forEach(function(position) {
		voteDb[position] = []
	})

	// loop over all but the header (first) row
	for (var i = 1; i < numRows; i++) {
		processRow(values[i], meta, voteDb)
	}
	for (var position in voteDb) {
		addToReport("<h3>Counting votes for " + position + "</h3>")
		addToReport("The winner for <b>" + position + "</b> is <b>" + determineWinner(voteDb[position]) + "</b>")
	}
	var htmlApp = HtmlService
		.createHtmlOutput('<p>' + report + '</p>')
		.setTitle('Results')
		.setWidth(300)
		.setHeight(700);

	SpreadsheetApp.getActiveSpreadsheet().show(htmlApp);
};

function error(msg) {
	addToReport("Error:", msg)
}

function processHeaders(hr) {
	var headers = []
	var positions = []
	hr.forEach(function(cell) {
		var val = false
		if (cell.indexOf(" [") != -1) {
			var bits = cell.split(" [")
			val = {
				"position": bits[0],
				"candidate": bits[1].split("]")[0]
			}
			if (positions.indexOf(val.position) == -1) {
				positions.push(val.position)
			}
		}
		headers.push(val)
	})
	return {
		"headers": headers,
		"positions": positions
	}
}

function processRow(row, meta, voteDb) {
	var votes = {}
	meta.positions.forEach(function(position) {
		votes[position] = {}
	})

	for (var i = 0; i < meta.headers.length; i++) {
		if (meta.headers[i]) {
			votes[meta.headers[i].position][row[i]] = meta.headers[i].candidate
		}
	}

	for (var position in votes) {
		var voteD = votes[position]
		var vote = []
		var ranks = getSortedNumericKeys(voteD)
		ranks.forEach(function(rank) {
			vote.push(voteD[rank])
		})
		voteDb[position].push(vote)
	}
}

function getSortedNumericKeys(d) {
	var keys = []
	for (var key in d) {
		var k = parseInt(key)
		keys.push(k)
	}
	keys.sort()
	return keys
}

function determineWinner(votes, candidates, text) {
	if (candidates === undefined) {
		candidates = getAllCandidates(votes)
	}
	var totalVotes = 0;
	var maxVotes = 0;
	var winningCandidate = null;
	var tallies = {}
	candidates.forEach(function(candidate) {
		tallies[candidate] = 0
	})
	votes.forEach(function(vote) {
		var isDone = false;
		vote.forEach(function(candidate) {
			if (!isDone && candidates.indexOf(candidate) != -1) {
				tallies[candidate]++;
				if (tallies[candidate] > maxVotes) {
					maxVotes = tallies[candidate]
					winningCandidate = candidate;
				}
				totalVotes++;
				isDone = true
			}
		})
	})

	// print the votes
	for (var candidate in tallies) {
		addToReport(candidate + ": " + tallies[candidate])
	}

	if (maxVotes * 2 > totalVotes) {
		return winningCandidate;
	} else {
		var leastVotes, leastVotesCount, pendingTie = false;
		for (var candidate in tallies) {
			if (leastVotesCount !== undefined && leastVotesCount === tallies[candidate]) {
				pendingTie = true;
			}
			if (leastVotesCount === undefined || leastVotesCount > tallies[candidate]) {
				leastVotesCount = tallies[candidate]
				leastVotes = candidate
				pendingTie = false
			}
		}
		if (pendingTie) {
			addToReport('<span style="color:red">Tie detected, think here. </span>')
		}
		addToReport("<b>Eliminating: </b>" + leastVotes)
			// copy the array
		var idx = candidates.indexOf(leastVotes)
			// remove the losing candidate
		candidates.splice(idx, 1)
		return determineWinner(votes, candidates)
	}
}

function getAllCandidates(votes) {
	var candidates = []
	votes.forEach(function(vote) {
		vote.forEach(function(candidate) {
			if (candidate !== undefined && candidates.indexOf(candidate) == -1) {
				candidates.push(candidate)
			}
		})
	})
	return candidates
}

function addToReport(text) {
	report += text + "<br />"
}


/**
 * Adds a custom menu to the active spreadsheet, containing a single menu item
 * for invoking the readRows() function specified above.
 * The onOpen() function, when defined, is automatically invoked whenever the
 * spreadsheet is opened.
 * For more information on using the Spreadsheet API, see
 * https://developers.google.com/apps-script/service_spreadsheet
 */
function onOpen() {
	var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
	var entries = [{
		name: "Calculate Votes",
		functionName: "readRows"
	}];
	spreadsheet.addMenu("Voting Calculator", entries);
};