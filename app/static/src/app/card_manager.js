import qwest from 'qwest'
import {filter, includes, isEqual, reduce, startsWith} from 'lodash'

const diceWeightMap = reduce(globals.diceData, (result, value, index) => {
	result[value] = index + 1
	return result
}, {})

function getDiceWeight (dice) {
	// First, determine our diceWeightMap numbers
	let weights = []
	for (let die of dice) {
		weights.push(diceWeightMap[die])
	}
	weights.sort()
	// Ensure we have 4 "digits" in weights
	let weightsLength = weights.length
	while (weightsLength < 4) {
		weights.push(0)
		weightsLength++
	}
	// And convert our weight to an integer
	return parseInt(weights.join(''))
}

function attributeSort(a, b, primarySort, primaryOrder, secondarySort, secondaryOrder) {
	if (a[primarySort] == b[primarySort]) {
		// If primarySorts are equal, we are not sorting by name (names are unique)
		// so ensure that we end with a name sort
		if (!secondarySort || secondarySort == 'name') {
			return attributeSort(
				a, b, 'name', secondaryOrder, null, secondaryOrder
			)
		} else {
			return attributeSort(
				a, b, secondarySort, secondaryOrder,
				'name', secondaryOrder
			)
		}
	}
	return b[primarySort] < a[primarySort] ? primaryOrder : -primaryOrder
}

/**
 * Offers interface for sorting, filtering, and selecting
 * card JSON.
 */
export default class {
	constructor () {
		// Create lookup table by ID
		this.idMap = {}
		let nameMap = {}
		for (let card of globals.cardData) {
			this.idMap[card.id] = card
			nameMap[card.name] = card
		}
		// Attach conjurations
		for (let card of globals.cardData) {
			if (card.conjurations && card.conjurations.length) {
				let conjurations = []
				for (let cardName of card.conjurations) {
					conjurations.push(nameMap[cardName])
				}
				card.conjurations = conjurations
			}
		}
	}
	cardById (id) {
		return this.idMap[id] || null
	}
	cardListing (callback, {
		search = null,
		types = null,
		releases = [0],
		dice = null,
		diceLogic = 'or',
		phoenixborn = null,
		primarySort = 'name',
		primaryOrder = 1,
		secondarySort = null,
		secondaryOrder = 1
	} = {}) {
		if (search) {
			qwest.post('/api/cards/search', {
				search: search,
				types: types,
				releases: releases,
				dice: dice,
				diceLogic: diceLogic,
				phoenixborn: phoenixborn
			}, {dataType: 'json'}).then((xhr, response) => {
				let cards = this.idsToListing(response)
				callback(this.sortListing(cards, {
					primaryOrder, primarySort, secondaryOrder, secondarySort
				}))
			}).catch(function(error, xhr, response) {
				console.log('Failure!', response)
				callback(null)
			})
			return
		}
		// Only include conjurations if they are specifically called for
		const excludeConjurations = !types || !includes(types, 'Conjuration')
		const excludePhoenixborn = !types || !includes(types, 'Phoenixborn')
		let subset = filter(globals.cardData, (card) => {
			if (excludeConjurations 
					&& (card.type == 'Conjuration' || card.type == 'Conjured Alteration Spell')) {
				return false
			}
			if (excludePhoenixborn && card.type == 'Phoenixborn') {
				return false
			}
			if (phoenixborn && card.phoenixborn && card.phoenixborn != phoenixborn) {
				return false
			}
			if (types && types.length
					&& !includes(types, card.type)
					&& (!includes(types, 'summon') || !startsWith(card.name, 'Summon'))) {
				return false
			}
			if (releases && releases.length && !releases.includes(card.release)) {
				return false
			}
			if (dice && dice.length) {
				if (diceLogic == 'and') {
					for (const die of dice) {
						if (!includes(card.dice, die)) {
							return false
						}
					}
				} else if (card.dice && card.dice.length) {
					let valid = false
					for (const die of card.dice) {
						if (includes(dice, die)) {
							valid = true
							continue
						}
					}
					if (!valid) return false
				} else if (!includes(dice, 'basic')) {
					// Card doesn't have any dice associated with it,
					// and we aren't filtering for basic-only
					return false
				}
			}
			return true
		})
		callback(this.sortListing(subset, {
			primaryOrder, primarySort, secondaryOrder, secondarySort
		}))
	}
	sortListing (cards, {
		primarySort = 'name',
		primaryOrder = 1,
		secondarySort = null,
		secondaryOrder = 1
	} = {}) {
		cards.sort((a, b) => {
			// Sorting by dice requires special weighting
			if (primarySort == 'dice') {
				// Grab sorted versions of our dice arrays
				let aDice = a.dice && a.dice.length ? a.dice : []
				let bDice = b.dice && b.dice.length ? b.dice : []
				aDice.sort()
				bDice.sort()
				// If the arrays are equal, check secondarySort
				if (isEqual(aDice, bDice)) {
					return attributeSort(
						a, b, secondarySort, secondaryOrder, null, secondaryOrder
					)
				}
				// Arrays are not equal, so we need to compare them
				let aWeight = getDiceWeight(aDice)
				let bWeight = getDiceWeight(bDice)
				return bWeight < aWeight ? primaryOrder : -primaryOrder
			}
			// Not sorting by dice, so just compare attributes normally
			return attributeSort(
				a, b, primarySort, primaryOrder, secondarySort, secondaryOrder
			)
		})
		return cards
	}
	idsToListing (ids) {
		let cards = []
		for (let id of ids) {
			cards.push(this.cardById(id))
		}
		return cards
	}
}
