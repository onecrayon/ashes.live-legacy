import {filter, includes} from 'lodash'

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
			if (types && !includes(types, card.type)) {
				return false
			}
			if (releases && !releases.includes(card.release)) {
				return false
			}
			if (dice) {
				if (diceLogic == 'and') {
					// TODO: replace this with a lodash method?
					for (const die of dice) {
						if (!includes(card.dice, die)) {
							return false
						}
					}
				} else {
					let valid = false
					for (const die of card.dice) {
						if (includes(dice, die)) {
							valid = true
							continue
						}
					}
					if (!valid) return false
				}
			}
			// TODO: implement text search logic
			return true
		})
		subset.sort((a, b) => {
			// When primarySort is 'name' we do not do a secondary sort (names are always unique)
			if (primarySort == 'name') {
				if (b < a) {
					return primaryOrder
				}
				return a == b ? 0 : -primaryOrder
			}
			// TODO: implement sorting by other column (including secondarySort)
		})
		return subset
	}
}
