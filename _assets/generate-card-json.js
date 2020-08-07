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
 *     ~ Between Realms ability text.
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
 * A slash is used to separate Parallel Costs; e.g.:
 *
 *     [[main]] - 1 [[divine:class]] / 1 [[sympathy:class]]
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

const fs = require('fs')
const path = require('path')
const dir = path.normalize(process.argv[2])
const files = fs.readdirSync(dir)
// Delimiter string for costs, etc.
const sep = ' - '
// Function for parsing costs into a diceTypes array in place
function parseCostsToDiceTypes (costsOrText, diceTypes, splitTypes) {
	const splitTypeRE = /(\[\[[a-z]+:(?:power|class)\]\])\s*(?:or|\/)\s*\d*\s*(\[\[[a-z]+:(?:power|class)\]\])/
	const diceTypeRE = /\[\[[a-z]+:(?:power|class)\]\]/g
	let diceMatches = []
	let splitDiceMatches = []
	if (Array.isArray(costsOrText)) {
		costsOrText.forEach(function (cost) {
			const splitMatches = cost.match(splitTypeRE)
			const matches = cost.match(diceTypeRE)
			if (splitMatches) {
				splitDiceMatches = splitDiceMatches.concat([splitMatches[1], splitMatches[2]])
			} else if (matches) {
				diceMatches = diceMatches.concat(matches)
			}
		})
	} else {
		const splitMatches = costsOrText.match(splitTypeRE)
		if (splitMatches) {
			splitDiceMatches = [splitMatches[1], splitMatches[2]]
		} else {
			diceMatches = costsOrText.match(diceTypeRE)
		}
	}
	if (diceMatches && diceMatches.length) {
		diceMatches.forEach(function (match) {
			diceTypes.push(match.replace(/^\[\[([a-z]+):[a-z]+\]\]$/, '$1'))
		})
	}
	if (splitDiceMatches && splitDiceMatches.length) {
		splitDiceMatches.forEach(function (match) {
			splitTypes.push(match.replace(/^\[\[([a-z]+):[a-z]+\]\]$/, '$1'))
		})
	}
}
const possibleDice = ['basic', 'ceremonial', 'charm', 'illusion', 'natural', 'divine', 'sympathy', 'time']
function parseCostToWeight (costCount, costText) {
	if (!costCount && !costText) {
		return 0
	}
	const costNumber = costCount ? parseInt(costCount) : null
	const costTypeArray = costText.split(':')
	const costType = costTypeArray[0]
	const costSubtype = costTypeArray.length > 1 ? costTypeArray[1] : null
	if (possibleDice.indexOf(costType) >= 0 && costNumber) {
		var weight = costNumber * 100
		if (costSubtype === 'class') {
			weight += costNumber * 1
		} else if (costSubtype === 'power') {
			weight += costNumber * 2
		}
		return weight
	} else if (costType === 'discard' && costNumber) {
		return costNumber * 3
	} else if (costType === 'side') {
		return 4
	} else if (costType === 'main') {
		return 5
	}
}

let longestName = ''
if (files) {
	const data = []

	files.forEach(function (filePath) {
		if (!filePath.endsWith('.txt')) {
			return
		}

		const cardText = fs.readFileSync(path.join(dir, filePath)).toString()
		const releaseNumber = parseInt(filePath)
		const cards = cardText.split(/^={3,}\n+/m)

		cards.forEach(function (cardData) {
			if (!cardData) {
				return
			}
			// Parse our basic card sections
			const details = cardData.split('\n\n')
			const meta = details[0].split('\n')
			const effects = details.slice(1)
			const titleMatch = meta[0].match(/^(.+?)(?:[ ]\(([a-z ]+)\))?$/i)
			const card = {
				'name': titleMatch[1],
				'stub': titleMatch[1].replace(/[ ]/g, '-').replace(/[^a-z0-9-]/ig, '').toLowerCase(),
				'release': releaseNumber
			}
			let stats = null
			const conjurations = []
			const diceTypes = []
			const splitTypes = []

			// Track longest name (for setting up database)
			if (card.name.length > longestName.length) {
				longestName = card.name
			}

			// Check to see if we are working with a phoenixborn
			if (meta.length === 2 &&
					!meta[1].startsWith('Reaction Spell') &&
					!meta[1].startsWith('Conjured Alteration Spell')) {
				card.type = 'Phoenixborn'
				stats = meta[1].split(sep)
			} else {
				// Check to see if this is a phoenixborn-specific card
				if (titleMatch.length > 1 && titleMatch[2]) {
					card.phoenixborn = titleMatch[2]
				}
				const typePlacement = meta[1].split(sep)
				// Parse out type, placement, and costs
				card.type = typePlacement[0]
				card.placement = typePlacement[1]
				// If the third line starts with a letter other than X, it's stats; otherwise cost
				if (meta[2] && /^[a-wyz]/i.test(meta[2])) {
					stats = meta[2].split(sep)
				} else {
					card.cost = meta.length > 2 ? meta[2].split(sep) : []
					parseCostsToDiceTypes(card.cost, diceTypes, splitTypes)
					// Calculate cost weighting
					var cardWeight = 0
					card.cost.forEach(function (cost, index) {
						const costMatch = cost.match(/^(\d*)\s*\[\[([a-z:]+)\]\]$/)
						const splitCostMatch = cost.match(/^(\d*)\s*\[\[([a-z:]+)\]\]\s*\/\s*(\d*)\s*\[\[([a-z:]+)\]\]$/)
						if (!costMatch && !splitCostMatch) {
							return
						}
						// For Parallel Costs (split costs, here), we only count the cheaper weight
						// since presumably that's what people will be using most of the time
						const match = costMatch || splitCostMatch
						const weight = parseCostToWeight(match[1], match[2])
						const weight2 = parseCostToWeight(match[3], match[4])
						if (weight2) {
							cardWeight += (weight < weight2 ? weight : weight2)
						} else {
							cardWeight += weight
						}
						if (splitCostMatch) {
							card.cost[index] = cost.split(' / ')
						}
					})
					card.weight = cardWeight
					// Grab stats list
					if (meta.length > 3) {
						stats = meta[3].split(sep)
					}
				}
			}
			// If there is a stat line, parse it
			if (stats) {
				stats.forEach(function (stat) {
					const regexMatch = stat.match(/^([a-z]+)[ ]([0-9X+-]+)$/i)
					// Store numeric stats as pure numbers
					const value = /^\d+$/.test(regexMatch[2]) ? parseInt(regexMatch[2]) : regexMatch[2]
					card[regexMatch[1].toLowerCase()] = value
				})
			}
			// Parse through our effect text
			card.text = []
			effects.forEach(function (text) {
				if (!text) {
					return
				}
				const parts = text.match(/^(?:(\*|~)\s+)?(?:([a-z0-9' ]+):\s+)?(?:((?:(?:\d+[ ])?\[\[[a-z:]+\]\](?:[ ](?:or|-)[ ])?)+):\s+)?(.+)\n*$/i)
				const effect = {}
				const conjurationMatches = parts[4].match(/\[\[[A-Z][A-Za-z' ]+\]\](?=[ ](?:(?:conjuration|conjured alteration spell)s?|or))/g)
				if (parts[1]) {
					if (parts[1] === '~') {
						effect.betweenRealms = true
					} else {
						effect.inexhaustible = true
					}
				}
				if (parts[2]) {
					effect.name = parts[2]
				}
				if (parts[3]) {
					effect.cost = parts[3].split(sep)
					parseCostsToDiceTypes(effect.cost, diceTypes, splitTypes)
				}
				effect.text = parts[4]
				parseCostsToDiceTypes(effect.text, diceTypes, splitTypes)
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
			if (splitTypes.length) {
				card.altDice = Array.from(new Set(splitTypes))
			}
			// And finally append our card and continue
			data.push(card)
		})
	})

	const outPath = path.join(dir, '_export.json')
	const outFile = fs.createWriteStream(outPath, { encoding: "utf8" })

	outFile.write(JSON.stringify(data))
	outFile.end()

	console.log('Writing to ' + outPath + ' complete!')
}

console.log('Longest name is ' + longestName.length + ' chars long')
console.log('All card data files parsed!')
