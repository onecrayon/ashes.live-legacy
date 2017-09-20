import {filter, includes, startsWith} from 'lodash'

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
			// TODO: implement sorting by dice type
			// When primarySort is 'name' we do not do a secondary sort (names are always unique)
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
