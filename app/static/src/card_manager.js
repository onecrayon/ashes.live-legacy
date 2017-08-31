/**
 * Offers interface for sorting, filtering, and selecting
 * card JSON.
 */
export default class {
	constructor () {
		// TODO: loop over globals.cards and globals.dice to construct indices necessary for easily relating the two?
		// Create lookup table by ID
		this.idMap = {}
		for (let card in globals.cardData) {
			this.idMap[card.id] = card
		}
	}
	cardById (id) {
		return this.idMap[id] || null
	}
	cardsByType (type) {
		// TODO: return array of cards based on the given type and active sorting
	}
	// TODO: add methods for fetching, filtering, and sorting card and die data
}
