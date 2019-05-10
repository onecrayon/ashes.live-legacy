#!/usr/bin/env node
/**
 * generate-ashes-500-json.js
 * 
 * This script generates a JSON file representing Ashes 500 point values based on a CSV file.
 * 
 * The CSV file must observe the following rules:
 * 
 * - First row is column headings (and ignored)
 * - First three columns are:
 *     1. Card title
 *     2. Cost for 1x
 *     3. Cost for 2x
 *     4. Cost for 3x
 * - Any other columns are ignored
 * 
 * After parsing the CSV, the script will query for card-specific overrides.
 */

// Output help text
if (!process.argv[2] || ['-h', '-?', '--help'].indexOf(process.argv[2]) > -1) {
	console.log('USAGE: ./generate-ashes-500-json.js comma_separated_values.csv')
	process.exit()
}

var fs = require('fs')
var path = require('path')
var readline = require('readline')
var filePath = path.normalize(process.argv[2])
var parseQty = function (qtyStr) {
	if (qtyStr === '') return null
	return parseInt(qtyStr)
}
var stubify = function (title) {
	return title.replace(/[ ]/g, '-').replace(/[^a-z0-9-]/ig, '').toLowerCase()
}

if (!filePath.endsWith('.csv')) {
	console.log('ERROR: input file must use .csv file extension.')
	process.exit()
}

var	valueStr = fs.readFileSync(filePath).toString()
var rows = valueStr.split('\n')
var data = []
// Remove the header row
rows.splice(0, 1)

rows.forEach(function (row) {
	var columns = row.split(',')
	if (!columns[0]) return
	data.push({
		'stub': stubify(columns[0]),
		'qty_1': parseQty(columns[1]),
		'qty_2': parseQty(columns[2]),
		'qty_3': parseQty(columns[3])
	})
})

console.log('Please input combo penalties...')

var rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout
})
var queryFallen = function (finalCallback) {
	console.log('===================================================================')
	rl.question('Per-Ally penalty for Summon Fallen: ', function (answer) {
		if (!answer) {
			return finalCallback()
		}
		data.push({
			stub: 'summon-fallen',
			combo_card_type: 'Ally',
			qty_1: answer,
			qty_2: null,
			qty_3: null
		})
		finalCallback()
	})
}
var queryCombo = function (finalCallback) {
	console.log('===================================================================')
	rl.question('Card title (leave blank to exit): ', function (answer) {
		if (!answer) {
			rl.close()
			return finalCallback()
		}
		var comboData = {}
		comboData['stub'] = stubify(answer)
		rl.question('Combo card title: ', function (answer) {
			if (!answer) {
				return queryCombo(finalCallback)
			}
			comboData['combo_stub'] = stubify(answer)

			rl.question('Penalty for 1x combo card: ', function (answer) {
				answer = parseQty(answer)
				if (answer === null) {
					return queryCombo(finalCallback)
				}
				comboData['qty_1'] = answer

				rl.question('Penalty for 2x combo card: ', function (answer) {
					answer = parseQty(answer)
					if (answer === null) {
						comboData['qty_2'] = null
						comboData['qty_3'] = null
						data.push(comboData)
						return queryCombo(finalCallback)
					}
					comboData['qty_2'] = answer

					rl.question('Penalty for 3x combo card: ', function (answer) {
						answer = parseQty(answer)
						if (answer === null) {
							comboData['qty_3'] = null
							data.push(comboData)
							return queryCombo(finalCallback)
						}
						comboData['qty_3'] = answer
						data.push(comboData)
						return queryCombo(finalCallback)
					})
				})
			})
		})
	})
}

queryFallen(function () {
	queryCombo(function () {
		var outPath = filePath.replace('.csv', '_export.json')
		var outFile = fs.createWriteStream(outPath, { encoding: 'utf8' })

		outFile.write(JSON.stringify(data))
		outFile.end()

		console.log('===================================================================')
		console.log('Writing to ' + outPath + ' complete!')
	})
})
