import {filter, includes, isEqual, startsWith} from 'lodash'

const diceWeightMap = {
	'ceremonial': 1,
	'charm': 2,
	'illusion': 3,
	'natural': 4,
	'divine': 5,
	'sympathy': 6
}
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

/**
 * Offers interface for sorting, filtering, and selecting
 * card JSON.
 */
export default class {
	constructor () {
		// TODO: loop over globals.cards and globals.dice to construct indices necessary for easily relating the two?
		// Create lookup table by ID
		this.idMap = {}
		for (let card of globals.cardData) {
			this.idMap[card.id] = card
		}
	}
	cardById (id) {
		return this.idMap[id] || null
	}
	cardListing ({
		search = null,
		types = null,
		releases = [0],
		dice = null,
		diceLogic = 'or',
		primarySort = 'name',
		primaryOrder = 1,
		secondarySort = null,
		secondaryOrder = 1
	} = {}) {
		// Only include conjurations if they are specifically called for
		const excludeConjurations = !types || !includes(types, 'Conjuration')
		const excludePhoenixborn = !types || !includes(types, 'Phoenixborn')
		let subset = filter(globals.cardData, (card) => {
			if (excludeConjurations && card.type == 'Conjuration') {
				return false
			}
			if (excludePhoenixborn && card.type == 'Phoenixborn') {
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
			// TODO: implement text search logic
			return true
		})
		subset.sort((a, b) => {
			// Sorting by dice requires special weighting
			if (primarySort == 'dice') {
				// Grab sorted versions of our dice arrays
				let aDice = a.dice && a.dice.length ? a.dice : []
				let bDice = b.dice && b.dice.length ? b.dice : []
				aDice.sort()
				bDice.sort()
				// If the arrays are equal, check secondarySort
				if (isEqual(aDice, bDice)) {
					if (!secondarySort) return 0
					if (b[secondarySort] < a[secondarySort]) {
						return secondaryOrder
					}
					return a[secondarySort] == b[secondarySort] ? 0 : -secondaryOrder
				}
				// Arrays are not equal, so we need to compare them
				let aWeight = getDiceWeight(aDice)
				let bWeight = getDiceWeight(bDice)
				return bWeight < aWeight ? primaryOrder : -primaryOrder
			}
			// Not sorting by dice, so just compare attributes normally
			// Only need to do secondarySort if primarySort is equal
			if (a[primarySort] == b[primarySort]) {
				if (!secondarySort) return 0
				if (b[secondarySort] < a[secondarySort]) {
					return secondaryOrder
				}
				return a[secondarySort] == b[secondarySort] ? 0 : -secondaryOrder
			}
			return b[primarySort] < a[primarySort] ? primaryOrder : -primaryOrder
		})
		return subset
	}
}
