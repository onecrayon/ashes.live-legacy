import Vue from 'vue'
import Vuex from 'vuex'
import CardManager from './card_manager'
import {reduce} from 'lodash'

/* eslint-disable no-new */

Vue.use(Vuex)

const cardManager = new CardManager

function disableReleaseDice(state) {
	if ((!state.filters.releases || state.filters.releases.indexOf(5) == -1)
			&& state.filters.dice && state.filters.dice.indexOf('divine') > -1) {
		state.filters.dice.splice(state.filters.dice.indexOf('divine'), 1)
	}
	if ((!state.filters.releases || state.filters.releases.indexOf(6) == -1)
			&& state.filters.dice && state.filters.dice.indexOf('sympathy') > -1) {
		state.filters.dice.splice(state.filters.dice.indexOf('sympathy'), 1)
	}
}

function gatherConjurations (card, conjurationList) {
	if (card && card.conjurations) {
		for (let conjuration of card.conjurations) {
			conjurationList.push({
				'count': conjuration.copies,
				'data': conjuration
			})
			gatherConjurations(conjuration, conjurationList)
		}
	}
}

function pluralCardType (cardType) {
	if (cardType == 'Ally') {
		return 'Allies'
	}
	return cardType + 's'
}

const cardTypeOrder = [
	'Ready Spell', 'Ally', 'Alteration Spell', 'Action Spell', 'Reaction Spell'
]

export default new Vuex.Store({
	state: {
		deck: {
			title: '',
			description: '',
			phoenixborn: null,
			dice: reduce(globals.diceData, (result, value) => {
				result[value] = 0
				return result
			}, {}),
			cards: {}
		},
		listing: [],
		listType: 'list',
		filters: {
			search: null,
			types: null,
			releases: [0],
			dice: null,
			diceLogic: 'or',
			phoenixborn: null,
			primarySort: 'name',
			primaryOrder: 1,
			secondarySort: null,
			secondaryOrder: 1
		}
	},
	getters: {
		totalDice (state) {
			return reduce(state.deck.dice, (result, value, key) => {
				return result + value
			}, 0)
		},
		deckSections (state) {
			const ids = Object.keys(state.deck.cards)
			if (!ids.length) return []
			let sections = {}
			const cards = cardManager.idsToListing(ids)
			let conjurations = []
			for (let card of cards) {
				if (!sections[card.type]) {
					sections[card.type] = []
				}
				sections[card.type].push({
					'count': state.deck.cards[card.id],
					'data': card
				})
				gatherConjurations(card, conjurations)
			}
			gatherConjurations(state.deck.phoenixborn, conjurations)
			let sectionTitles = Object.keys(sections)
			sectionTitles.sort((a, b) => {
				return cardTypeOrder.indexOf(a) < cardTypeOrder.indexOf(b) ? -1 : 1
			})
			let sortedSections = []
			for (let section of sectionTitles) {
				let contents = sections[section]
				contents.sort((a, b) => {
					if (a.data.name == b.data.name) {
						return 0
					}
					return a.data.name < b.data.name ? -1 : 1
				})
				sortedSections.push({
					'title': pluralCardType(section),
					'contents': contents
				})
			}
			if (conjurations.length) {
				conjurations.sort((a, b) => {
					if (a.data.name == b.data.name) {
						return 0
					}
					return a.data.name < b.data.name ? -1 : 1
				})
				sortedSections.push({
					'title': 'Conjuration Deck',
					'contents': conjurations
				})
			}
			return sortedSections
		},
		neededDice (state) {
			const ids = Object.keys(state.deck.cards)
			if (!ids.length) return []
			const cards = cardManager.idsToListing(ids)
			return reduce(cards, (result, card) => {
				if (card.dice && card.dice.length) {
					for (let die of card.dice) {
						if (result.indexOf(die) == -1) {
							result.push(die)
						}
					}
				}
				return result
			}, [])
		}
	},
	mutations: {
		// Deck editing methods
		setTitle (state, title) {
			state.deck.title = title
		},
		setDescription (state, description) {
			state.deck.description = description
		},
		setPhoenixborn (state, id) {
			state.deck.phoenixborn = cardManager.cardById(id)
			state.filters.phoenixborn = state.deck.phoenixborn ? state.deck.phoenixborn.name : null
			// Clear out the search, since the listing contents are updating
			state.filters.search = null
			const ids = Object.keys(state.deck.cards)
			if (state.deck.phoenixborn && ids.length) {
				// Clear out any Phoenixborn-specific cards in the deck
				const cards = cardManager.idsToListing(ids)
				for (let card of cards) {
					if (card.phoenixborn && card.phoenixborn != state.deck.phoenixborn.name) {
						Vue.delete(state.deck.cards, card.id)
					}
				}
			}
		},
		setDieCount (state, payload) {
			state.deck.dice[payload.die] = payload.count
		},
		decrementDie (state, dieType) {
			if (state.deck.dice[dieType] > 0) {
				state.deck.dice[dieType] -= 1
			}
		},
		clearDice (state) {
			for (let dieType of Object.keys(state.deck.dice)) {
				state.deck.dice[dieType] = 0
			}
		},
		setCardQty (state, payload) {
			if (!state.deck.cards[payload.id] && payload.qty > 0) {
				Vue.set(state.deck.cards, payload.id, payload.qty)
			} else if (state.deck.cards[payload.id] && payload.qty == 0) {
				Vue.delete(state.deck.cards, payload.id)
			} else {
				state.deck.cards[payload.id] = payload.qty
			}
		},
		// Filter methods
		setSearch (state, search) {
			state.filters.search = search
		},
		diceToFilters (state) {
			state.filters.diceLogic = 'or'
			let activeDice = ['basic']
			for (let dieType of Object.keys(state.deck.dice)) {
				if (state.deck.dice[dieType]
						&& (dieType != 'divine' || state.filters.releases.indexOf(5) > -1)
						&& (dieType != 'sympathy' || state.filters.releases.indexOf(6) > -1)) {
					activeDice.push(dieType)
				}
			}
			state.filters.dice = activeDice
		},
		toggleDiceLogic (state) {
			state.filters.diceLogic = state.filters.diceLogic == 'or' ? 'and' : 'or'
			// Exclude basic die check from "and" comparisons
			if (state.filters.diceLogic == 'and' && state.filters.dice
					&& state.filters.dice.indexOf('basic') > -1) {
				state.filters.dice.splice(state.filters.dice.indexOf('basic'), 1)
			}
		},
		toggleDieFilter (state, die) {
			if (!state.filters.dice || !state.filters.dice.length) {
				state.filters.dice = [die]
			} else if (state.filters.dice.indexOf(die) > -1) {
				state.filters.dice.splice(state.filters.dice.indexOf(die), 1)
			} else {
				state.filters.dice.push(die)
			}
		},
		toggleTypeFilter (state, typeName) {
			if (!state.filters.types || !state.filters.types.length) {
				state.filters.types = [typeName]
			} else if (state.filters.types.indexOf(typeName) > -1) {
				state.filters.types.splice(state.filters.types.indexOf(typeName), 1)
			} else {
				state.filters.types.push(typeName)
			}
		},
		setTypes (state, types) {
			state.filters.types = types
		},
		toggleRelease (state, releaseNumber) {
			if (state.filters.releases === null) {
				state.filters.releases = [releaseNumber]
			} else if (state.filters.releases.indexOf(releaseNumber) > -1) {
				state.filters.releases.splice(state.filters.releases.indexOf(releaseNumber), 1)
				disableReleaseDice(state)
			} else {
				state.filters.releases.push(releaseNumber)
			}
		},
		toggleReleases (state, releases) {
			if (state.filters.releases === null) {
				state.filters.releases = releases
			} else {
				for (let release of releases) {
					if (state.filters.releases.indexOf(release) > -1) {
						state.filters.releases.splice(state.filters.releases.indexOf(release), 1)
					} else {
						state.filters.releases.push(release)
					}
				}
				disableReleaseDice(state)
				// Disallow a completely empty list by defaulting to showing the core set
				if (!state.filters.releases.length) {
					state.filters.releases = [0]
				}
			}
		},
		resetFilters (state) {
			state.filters.search = null
			state.filters.types = null
			state.filters.dice = null
			// If only "promo" cards are being shown, it's possible that
			// clearing filters will not show anything if the selected
			// phoenixborn is not a promo
			let onlyPromos = true
			for (let release of state.filters.releases) {
				if (release < 100) {
					onlyPromos = false
				}
			}
			if (onlyPromos && state.deck.phoenixborn.release < 100) {
				state.filters.releases = [0]
			}
		},
		// Sorting methods
		toggleSortOrder (state) {
			state.filters.primaryOrder *= -1
			state.filters.secondaryOrder *= -1
		},
		setSort (state, field) {
			if (field == 'dice') {
				state.filters.primarySort = field
				state.filters.secondarySort = 'weight'
			} else if (field != 'name') {
				state.filters.primarySort = field
				state.filters.secondarySort = 'name'
			} else {
				state.filters.primarySort = 'name'
				state.filters.secondarySort = null
			}
		},
		// Listing methods
		setListType (state, listType) {
			state.listType = listType
		},
		filterCards (state, options) {
			options = options || state.filters
			cardManager.cardListing((cards) => {
				state.listing = cards
			}, options)
		},
		// TODO: add methods for incrementing and decrementing card counts
	}
})
