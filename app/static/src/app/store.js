import Vue from 'vue'
import Vuex from 'vuex'
import CardManager from './card_manager'
import {isInteger, merge, reduce} from 'lodash'
import {globals} from './utils'

/* eslint-disable no-new */

Vue.use(Vuex)

const cardManager = new CardManager()

function disableReleaseDice (state) {
	if (!state.options.releases || state.options.releases.indexOf('expansions') === -1) {
		if (state.options.dice && state.options.dice.indexOf('divine') > -1) {
			state.options.dice.splice(state.options.dice.indexOf('divine'), 1)
		}
		if (state.options.dice && state.options.dice.indexOf('sympathy') > -1) {
			state.options.dice.splice(state.options.dice.indexOf('sympathy'), 1)
		}
	}
}

function gatherConjurations (card, conjurationList, currentStubs) {
	if (card && card.conjurations) {
		currentStubs = currentStubs || reduce(conjurationList, (stubs, conj) => {
			stubs.push(conj.data.stub)
			return stubs
		}, [])
		for (let conjuration of card.conjurations) {
			if (currentStubs.indexOf(conjuration.stub) === -1) {
				conjurationList.push({
					'count': conjuration.copies,
					'data': conjuration
				})
				currentStubs.push(conjuration.stub)
				gatherConjurations(conjuration, conjurationList, currentStubs)
			}
		}
	}
}

function pluralCardType (cardType) {
	if (cardType === 'Ally') {
		return 'Allies'
	}
	return cardType + 's'
}

const cardTypeOrder = [
	'Ready Spell', 'Ally', 'Alteration Spell', 'Action Spell', 'Reaction Spell'
]

let defaultReleases = ['core']
let deckPhoenixborn = null
if (globals.deck) {
	deckPhoenixborn = cardManager.cardById(globals.deck.phoenixborn)
	if (deckPhoenixborn.release > 100) {
		defaultReleases = ['core', 'expansions', 'promos']
	} else if (deckPhoenixborn.release > 0) {
		defaultReleases = ['core', 'expansions']
	}
}

const storageOptionsKey = 'deckbuilder.options'
function storeSet (key, value) {
	const stashed = window.localStorage.getItem(storageOptionsKey)
	let options = stashed ? JSON.parse(stashed) : {}
	options[key] = value
	window.localStorage.setItem(storageOptionsKey, JSON.stringify(options))
}

function storeGet (key) {
	const stashed = window.localStorage.getItem(storageOptionsKey)
	let options = stashed ? JSON.parse(stashed) : {}
	return options[key]
}

function storeGetAll () {
	const stashed = window.localStorage.getItem(storageOptionsKey)
	const options = stashed ? JSON.parse(stashed) : {}
	return options
}

// Upgrade our stored releases (if any); we used to store the numeric IDs, but this destroys the
// ability to see new expansions when they are added to the site
const oldReleases = storeGet('releases')
if (oldReleases && isInteger(oldReleases[0])) {
	let releases = []
	if (oldReleases.indexOf(0) > -1) {
		releases.push('core')
	}
	if (oldReleases.indexOf(1) > -1) {
		releases.push('expansions')
	}
	if (oldReleases.indexOf(101) > -1) {
		releases.push('promos')
	}
	storeSet('releases', releases)
}

export default new Vuex.Store({
	state: {
		deck: merge({
			id: null,
			title: '',
			description: '',
			phoenixborn: null,
			dice: reduce(globals.diceData, (result, value) => {
				result[value] = 0
				return result
			}, {}),
			cards: {}
		}, globals.deck || {}),
		listing: [],
		options: merge({
			// These options filter the list
			search: null,
			types: null,
			releases: defaultReleases,
			dice: null,
			diceLogic: 'or',
			phoenixborn: deckPhoenixborn ? deckPhoenixborn.name : null,
			// These options affect listing display
			listType: 'table',
			primarySort: 'name',
			primaryOrder: 1,
			secondarySort: null,
			secondaryOrder: 1,
			includeConjurations: false,
			// These options affect the deck listing display
			showDetails: true
		}, storeGetAll(), !globals.galleryOnly && (!globals.deck || !globals.deck.phoenixborn) ? {
			'primarySort': 'name',
			'secondarySort': null
		} : {})
	},
	getters: {
		phoenixborn (state) {
			return cardManager.cardById(state.deck.phoenixborn)
		},
		totalDice (state) {
			let totalDice = 0
			const values = Object.values(state.deck.dice)
			for (let value of values) {
				totalDice += value
			}
			return totalDice
		},
		totalCards (state) {
			let totalCards = 0
			const values = Object.values(state.deck.cards)
			for (let value of values) {
				totalCards += value
			}
			return totalCards
		},
		deckSections (state, getters) {
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
			gatherConjurations(getters.phoenixborn, conjurations)
			let sectionTitles = Object.keys(sections)
			sectionTitles.sort((a, b) => {
				return cardTypeOrder.indexOf(a) < cardTypeOrder.indexOf(b) ? -1 : 1
			})
			let sortedSections = []
			for (let section of sectionTitles) {
				let contents = sections[section]
				contents.sort((a, b) => {
					if (a.data.name === b.data.name) {
						return 0
					}
					return a.data.name < b.data.name ? -1 : 1
				})
				const totalCards = reduce(contents, (total, card) => {
					return total + card.count
				}, 0)
				sortedSections.push({
					'title': pluralCardType(section),
					'count': totalCards,
					'contents': contents
				})
			}
			if (conjurations.length) {
				conjurations.sort((a, b) => {
					if (a.data.name === b.data.name) {
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
						if (result.indexOf(die) === -1) {
							result.push(die)
						}
					}
				}
				return result
			}, [])
		},
		untitledText (state, getters) {
			return 'Untitled ' + ((getters.phoenixborn && getters.phoenixborn.name) || 'deck')
		}
	},
	mutations: {
		// Deck editing methods
		setId (state, id) {
			state.deck.id = id
		},
		setTitle (state, title) {
			state.deck.title = title
		},
		setDeckDescription (state, description) {
			state.deck.description = description
		},
		setPhoenixborn (state, id) {
			const phoenixborn = cardManager.cardById(id)
			state.deck.phoenixborn = id
			state.options.phoenixborn = phoenixborn ? phoenixborn.name : null
			// Configure the sorting options (because they differ between the listing types)
			if (id) {
				state.options.primarySort = storeGet('primarySort') || 'name'
				state.options.secondarySort = storeGet('secondarySort') || null
			} else {
				state.options.primarySort = 'name'
				state.options.secondarySort = null
			}
			// Clear out the search, since the listing contents are updating
			state.options.search = null
			const ids = Object.keys(state.deck.cards)
			if (phoenixborn && ids.length) {
				// Clear out any Phoenixborn-specific cards in the deck
				const cards = cardManager.idsToListing(ids)
				for (let card of cards) {
					if (card.phoenixborn && card.phoenixborn !== phoenixborn.name) {
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
			} else if (state.deck.cards[payload.id] && payload.qty === 0) {
				Vue.delete(state.deck.cards, payload.id)
			} else {
				state.deck.cards[payload.id] = payload.qty
			}
		},
		// Filter methods
		setSearch (state, search) {
			state.options.search = search
		},
		diceToFilters (state) {
			state.options.diceLogic = 'or'
			let activeDice = ['basic']
			const showingExpansions = state.options.releases.indexOf('expansions') > -1
			for (let dieType of Object.keys(state.deck.dice)) {
				if (state.deck.dice[dieType] &&
						(dieType !== 'divine' || showingExpansions) &&
						(dieType !== 'sympathy' || showingExpansions)) {
					activeDice.push(dieType)
				}
			}
			state.options.dice = activeDice
		},
		toggleDiceLogic (state) {
			state.options.diceLogic = state.options.diceLogic === 'or' ? 'and' : 'or'
			// Exclude basic die check from "and" comparisons
			if (state.options.diceLogic === 'and' && state.options.dice &&
					state.options.dice.indexOf('basic') > -1) {
				state.options.dice.splice(state.options.dice.indexOf('basic'), 1)
			}
		},
		toggleDieFilter (state, die) {
			if (!state.options.dice || !state.options.dice.length) {
				state.options.dice = [die]
			} else if (state.options.dice.indexOf(die) > -1) {
				state.options.dice.splice(state.options.dice.indexOf(die), 1)
			} else {
				state.options.dice.push(die)
			}
			// Disallow filtering by conjuration types when we have a dice type selected
			if (state.options.dice && state.options.dice.length > 0 && state.options.types &&
					state.options.types.indexOf('conjurations') > -1) {
				state.options.types.splice(state.options.types.indexOf('conjurations'), 1)
			}
		},
		toggleTypeFilter (state, typeName) {
			if (!state.options.types || !state.options.types.length) {
				state.options.types = [typeName]
			} else if (state.options.types.indexOf(typeName) > -1) {
				state.options.types.splice(state.options.types.indexOf(typeName), 1)
			} else {
				state.options.types.push(typeName)
			}
		},
		setTypes (state, types) {
			state.options.types = types
		},
		toggleReleases (state, releasesKey) {
			if (state.options.releases === null) {
				state.options.releases = [releasesKey]
			} else if (state.options.releases.indexOf(releasesKey) > -1) {
				state.options.releases.splice(state.options.releases.indexOf(releasesKey), 1)
				disableReleaseDice(state)
				// Disallow a completely empty list by defaulting to showing the core set
				if (!state.options.releases.length) {
					state.options.releases = ['core']
				}
			} else {
				state.options.releases.push(releasesKey)
			}
			storeSet('releases', state.options.releases)
		},
		resetFilters (state) {
			state.options.search = null
			state.options.types = null
			state.options.dice = null
			// If only "promo" cards are being shown, it's possible that
			// clearing filters will not show anything if the selected
			// phoenixborn is not a promo
			let onlyPromos = true
			for (let release of state.options.releases) {
				if (release < 100) {
					onlyPromos = false
				}
			}
			if (onlyPromos) {
				const phoenixborn = cardManager.cardById(state.deck.phoenixborn)
				if (phoenixborn.release < 100) {
					state.options.releases = [0]
				}
			}
		},
		setincludeConjurations (state, includeConjurations) {
			state.options.includeConjurations = includeConjurations
		},
		// Sorting methods
		toggleSortOrder (state) {
			state.options.primaryOrder *= -1
			state.options.secondaryOrder *= -1
			storeSet('primaryOrder', state.options.primaryOrder)
			storeSet('secondaryOrder', state.options.secondaryOrder)
		},
		setSort (state, field) {
			if (field === 'dice') {
				state.options.primarySort = field
				state.options.secondarySort = 'weight'
			} else if (field !== 'name') {
				state.options.primarySort = field
				state.options.secondarySort = 'name'
			} else {
				state.options.primarySort = 'name'
				state.options.secondarySort = null
			}
			// We only persist the sort if we are working with the standard deckbuilder
			// (because the Phoenixborn sort options are different)
			if (state.deck.phoenixborn) {
				storeSet('primarySort', state.options.primarySort)
				storeSet('secondarySort', state.options.secondarySort)
			}
		},
		// Listing methods
		setListType (state, listType) {
			state.options.listType = listType
			storeSet('listType', listType)
		},
		filterCards (state, options) {
			options = options || state.options
			cardManager.cardListing((cards) => {
				state.listing = cards
			}, options)
		},
		// Deck listing methods
		setShowDetails (state, value) {
			state.options.showDetails = value
			storeSet('showDetails', value)
		}
	}
})
