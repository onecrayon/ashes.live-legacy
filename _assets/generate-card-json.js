#!/usr/bin/env node
/**
 * generate-card-json.js
 * 
 * This script parses a textual representation of an Ashes card into JSON
 * using the following schema:
 * 
 *     Card Title 1
 *     Type - Placement
 *     Cost
 *     Stats
 *     
 *     Ability Name: Ability Cost: Ability text.
 *     
 *     * Inexhaustible ability text.
 *     
 *     =====
 *     
 *     Card Title 2 (Phoenixborn name)
 *     ...
 * 
 * Stats are optional (typically only there for units or alterations).
 * Same applies to ability names and costs. Costs and cards are represented
 * in double brackets with optional numbers preceding them:
 * 
 *     [[main]]
 *     1 [[charm:class]]
 *     [[Butterfly Monk]]
 * 
 * A space-delimited hyphen character ( - ) is used to separate costs,
 * or anywhere the "diamond" separator is used on a card.
 * 
 * Phoenixborn do not have a Type or Cost line, but do have Stats
 * (with battlefield/life/spellboard values).
 * 
 * A card with a parenthesized Phoenixborn name after the title is
 * only usable in decks with that Phoenixborn.
 */

// Output help text
if (!process.argv[2] || ['-h', '-?', '--help'].indexOf(process.argv[2]) > -1) {
	console.log('USAGE: ./generate-card-json.js targetDirectory')
	process.exit()
}

var fs = require('fs'),
	path = require('path'),
	dir = path.normalize(process.argv[2]),
	files = fs.readdirSync(dir),
	// Delimiter string for costs, etc.
	sep = ' - ',
	// Function for parsing costs into a diceTypes array in place
	parseCostsToDiceTypes = function (costsOrText, diceTypes) {
		var diceTypeRE = /\[\[[a-z]+:(?:power|class)\]\]/g,
			diceMatches = []
		if (Array.isArray(costsOrText)) {
			costsOrText.forEach(function (cost) {
				var matches = cost.match(diceTypeRE)
				if (matches) {
					diceMatches = diceMatches.concat(matches)
				}
			})
		} else {
			diceMatches = costsOrText.match(diceTypeRE)
		}
		if (diceMatches) {
			diceMatches.forEach(function (match) {
				diceTypes.push(match.replace(/^\[\[([a-z]+):[a-z]+\]\]$/, '$1'))
			})
		}
	}

if (files) {
	files.forEach(function (filePath) {
		if (!filePath.endsWith('.txt')) {
			return
		}
		
		var	cardText = fs.readFileSync(path.join(dir, filePath)).toString(),
			outPath = path.join(dir, filePath.replace(/\.txt$/, '.json')),
			outFile = fs.createWriteStream(outPath, { encoding: "utf8" }),
			cards = cardText.split(/^={3,}\n+/m),
			data = []
		
		cards.forEach(function (cardData) {
			if (!cardData) {
				return
			}
			// Parse our basic card sections
			var details = cardData.split('\n\n'),
				meta = details[0].split('\n'),
				effects = details.slice(1),
				titleMatch = meta[0].match(/^(.+?)(?:[ ]\(([a-z ]+)\))?$/i),
				card = {
					'name': titleMatch[1],
					'stub': titleMatch[1].replace(/[ ]/g, '-').replace(/[^a-z0-9-]/ig, '').toLowerCase()
				},
				stats = null,
				conjurations = [],
				diceTypes = []
			
			// Check to see if we are working with a phoenixborn
			if (meta.length == 2) {
				card.type = 'Phoenixborn'
				stats = meta[1].split(sep)
			} else {
				// Check to see if this is a phoenixborn-specific card
				if (titleMatch.length > 1 && titleMatch[2]) {
					card.phoenixborn = titleMatch[2]
				}
				var typePlacement = meta[1].split(sep)
				// Parse out type, placement, and costs
				card.type = typePlacement[0]
				card.placement = typePlacement[1]
				// If the third line starts with a letter, it's stats; otherwise cost
				if (/^[a-z]/i.test(meta[2])) {
					stats = meta[2].split(sep)
				} else {
					card.cost = meta[2].split(sep)
					diceType = parseCostsToDiceTypes(card.cost, diceTypes)
					if (meta.length > 3) {
						stats = meta[3].split(sep)
					}
				}
			}
			// If there is a stat line, parse it
			if (stats) {
				stats.forEach(function (stat) {
					var regexMatch = stat.match(/^([a-z]+)[ ]([0-9X+-]+)$/i)
					card[regexMatch[1].toLowerCase()] = regexMatch[2]
				})
			}
			// Parse through our effect text
			card.text = []
			effects.forEach(function (text) {
				if (!text) {
					return
				}
				var parts = text.match(/^(\*\s+)?(?:([a-z0-9 ]+):\s+)?(?:((?:(?:\d+[ ])?\[\[[a-z:]+\]\](?:[ ]-[ ])?)+):\s+)?(.+)\n*$/i)
					effect = {},
					conjurationMatches = parts[4].match(/\[\[[a-z ]+\]\](?=[ ](?:conjuration|conjured alteration spell)s?)/ig)
				if (parts[1]) {
					effect.inexhaustible = true
				}
				if (parts[2]) {
					effect.name = parts[2]
				}
				if (parts[3]) {
					effect.cost = parts[3].split(sep)
					parseCostsToDiceTypes(effect.cost, diceTypes)
				}
				effect.text = parts[4]
				parseCostsToDiceTypes(effect.text, diceTypes)
				card.text.push(effect)
				// Lastly, check for any conjurations
				if (conjurationMatches) {
					conjurationMatches.forEach(function (cardString) {
						// Grab just the card name, excluding the square braces
						var cardName = cardString.substring(2, cardString.length - 2)
						if (conjurations.indexOf(cardName) < 0) {
							conjurations.push(cardName)
						}
					})
				}
			})
			if (conjurations.length) {
				card.conjurations = conjurations
			}
			if (diceTypes.length) {
				card.dice = Array.from(new Set(diceTypes))
			}
			// And finally append our card and continue
			data.push(card)
		})
		
		outFile.write(JSON.stringify(data))
		outFile.end()
		
		console.log('Writing to ' + outPath + ' complete!')
	})
}

console.log('All card data files parsed!')
