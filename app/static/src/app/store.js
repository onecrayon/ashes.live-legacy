import Vue from 'vue'
import Vuex from 'vuex'
import qwest from 'qwest'
import Nanobar from 'app/nanobar'
import CardManager from './card_manager'
import {concat, isEmpty, isInteger, merge, reduce} from 'lodash'
import {globals} from './utils'

/* eslint-disable no-new */

Vue.use(Vuex)

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

let defaultReleases = ['core', 'expansions']
let deckPhoenixborn = null
if (globals.deck) {
	deckPhoenixborn = globals.deck._phoenixborn_data
	if (deckPhoenixborn.release > 100) {
		defaultReleases = ['core', 'expansions', 'promos']
	} else if (deckPhoenixborn.release > 0) {
		defaultReleases = ['core', 'expansions']
	}
}
const enableAshes500 = !!(
	globals.enableAshes500 ||
	(globals.deck && globals.deck.ashes_500_revision_id) ||
	window.location.search.indexOf('mode=ashes-500') > -1 ||
	false
)

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

// This will be set asyncronously after defining the store
let pendingFilterOptions = null

export default new Vuex.Store({
	state: {
		cardManager: null,
		ashes_500_revision: null,
		isDisabled: false,
		deck: merge({
			id: null,
			title: '',
			description: '',
			phoenixborn: null,
			dice: reduce(globals.diceData, (result, value) => {
				result[value] = 0
				return result
			}, {}),
			cards: {},
			first_five: [],
			effect_costs: [],
			tutor_map: {},
			ashes_500_score: null,
			ashes_500_revision_id: null
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
			includeAllCards: false,
			enableAshes500: enableAshes500,
			// These options affect the deck listing display
			showDetails: true
		}, storeGetAll(), !globals.galleryOnly && (!globals.deck || !globals.deck.phoenixborn) ? {
			'primarySort': 'name',
			'secondarySort': null
		} : {})
	},
	getters: {
		phoenixborn (state) {
			return !state.cardManager ? null : state.cardManager.cardById(state.deck.phoenixborn)
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
		allCards (state) {
			const ids = Object.keys(state.deck.cards)
			if (!ids.length || !state.cardManager) return []
			const cards = state.cardManager.idsToListing(ids)
			let allCards = []
			for (const card of cards) {
				for (let i = 0; i < state.deck.cards[card.id]; i++) {
					allCards.push(card)
				}
			}
			return allCards
		},
		deckSections (state, getters) {
			const ids = Object.keys(state.deck.cards)
			if (!ids.length || !state.cardManager) return []
			let sections = {}
			const cards = state.cardManager.idsToListing(ids)
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
					'contents': conjurations,
					'isConjurations': true
				})
			}
			return sortedSections
		},
		neededDice (state) {
			const ids = Object.keys(state.deck.cards)
			if (state.deck.phoenixborn) {
				ids.push(state.deck.phoenixborn)
			}
			if (!ids.length || !state.cardManager) return []
			const cards = state.cardManager.idsToListing(ids)
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
		},
		ashes500Score (state) {
			let ids = Object.keys(state.deck.cards).map(str => parseInt(str))
			if (state.deck.phoenixborn) {
				ids.push(state.deck.phoenixborn)
			}
			let score = 0
			if (!ids.length || !state.cardManager) return score
			const cards = state.cardManager.idsToListing(ids)
			for (let card of cards) {
				if (!card.ashes_500_costs) continue
				const qty = state.deck.cards[card.id]
				for (let cost of card.ashes_500_costs) {
					// Skip combo entries for where the combo card isn't in the deck
					if (cost.combo_card_id && ids.indexOf(cost.combo_card_id) === -1) continue
					score += cost.qty_1
					if (qty >= 2 && cost.qty_2) {
						score += cost.qty_2
					}
					if (qty === 3 && cost.qty_3) {
						score += cost.qty_3
					}
				}
			}
			return score
		},
		activeComboIds (state) {
			const ids = Object.keys(state.deck.cards).map(str => parseInt(str))
			let comboIds = []
			if (!ids.length || !state.cardManager) return comboIds
			const cards = state.cardManager.idsToListing(ids)
			for (let card of cards) {
				if (!card.ashes_500_combos) continue
				for (let comboId of card.ashes_500_combos) {
					if (ids.indexOf(comboId) > -1) {
						comboIds.push(comboId)
						comboIds.push(card.id)
					}
				}
			}
			comboIds = Array.from(new Set(comboIds))
			return comboIds
		},
		firstFive (state) {
			if (!state.deck.first_five.length || !state.cardManager) {
				return null
			}
			return state.cardManager.idsToListing(state.deck.first_five)
		},
		effectCostOnlyCards (state) {
			if (!state.deck.effect_costs.length || !state.cardManager) {
				return null
			}
			const cardIds = new Set(concat(state.deck.first_five, state.deck.effect_costs))
			for (const id of state.deck.first_five) {
				cardIds.delete(id)
			}
			if (!cardIds.size) {
				return null
			}
			return state.cardManager.idsToListing(Array.from(cardIds))
		},
		tutorTargets (state) {
			return Object.values(state.deck.tutor_map)
		},
		tutorSelections (state) {
			return state.deck.tutor_map
		},
		tutoredCards (state) {
			if (isEmpty(state.deck.tutor_map) || !state.cardManager) {
				return null
			}
			return state.cardManager.idsToListing(Object.values(state.deck.tutor_map))
		}
	},
	mutations: {
		// We disable controls that could cause an AJAX call while an AJAX call is pending
		setAppDisabled (state, isDisabled) {
			state.isDisabled = isDisabled
		},
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
			const previousPhoenixborn = state.deck.phoenixborn
			const phoenixborn = state.cardManager.cardById(id)
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
				const cards = state.cardManager.idsToListing(ids)
				for (let card of cards) {
					if (card.phoenixborn && card.phoenixborn !== phoenixborn.name) {
						Vue.delete(state.deck.cards, card.id)
					}
				}
			}
			// Remove the Phoenixborn ability from effect cost listing, if it's there
			if (!phoenixborn && previousPhoenixborn && state.deck.effect_costs.indexOf(previousPhoenixborn) > -1) {
				state.deck.effect_costs.splice(state.deck.effect_costs.indexOf(previousPhoenixborn), 1)
			}
			// Remove the Phoenixborn ability from the tutor map, if it's there
			if (!phoenixborn && previousPhoenixborn && state.deck.tutor_map[previousPhoenixborn]) {
				Vue.delete(state.deck.tutor_map, previousPhoenixborn)
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
				// Clear card from first five, effect costs, and tutor map if necessary
				if (state.deck.first_five.indexOf(payload.id) > -1) {
					state.deck.first_five.splice(state.deck.first_five.indexOf(payload.id), 1)
				}
				if (state.deck.effect_costs.indexOf(payload.id) > -1) {
					state.deck.effect_costs.splice(state.deck.effect_costs.indexOf(payload.id), 1)
				}
				if (state.deck.tutor_map[payload.id]) {
					Vue.delete(state.deck.tutor_map, payload.id)
				}
			} else {
				state.deck.cards[payload.id] = payload.qty
				// Ensure we cannot tutor for more copies of a card than are in the deck
				let inUse = reduce(Object.values(state.deck.tutor_map), (total, current) => {
					if (current === payload.id) return total + 1
					return total
				}, 0) + (state.deck.first_five.indexOf(payload.id) > -1 ? 1 : 0)
				if (payload.qty < inUse) {
					// We don't have a way to remove things in order (object keys aren't ordered)
					// So to keep things simple, drop all tutored copies of the card if qty drops
					for (const tutorId of Object.keys(state.deck.tutor_map)) {
						if (state.deck.tutor_map[tutorId] === payload.id) {
							Vue.delete(state.deck.tutor_map, tutorId)
						}
					}
					const card = state.cardManager.cardById(payload.id)
					globals.notify('Quantity too low; ' + card.name + ' removed from search effects in the Costs tab.', 'warning')
				}
			}
		},
		setDeck500Revision (state, revision) {
			state.deck.ashes_500_revision_id = revision
		},
		setDeck500Score (state, score) {
			state.deck.ashes_500_score = score
		},
		toggleFirstFive (state, cardId) {
			if (state.deck.first_five.indexOf(cardId) > -1) {
				state.deck.first_five.splice(state.deck.first_five.indexOf(cardId), 1)
				// Effect costs are not allowed unless a card is in the First Five
				if (state.deck.effect_costs.indexOf(cardId) > -1) {
					state.deck.effect_costs.splice(state.deck.effect_costs.indexOf(cardId), 1)
				}
			} else {
				state.deck.first_five.push(cardId)
			}
		},
		toggleEffectCost (state, cardId) {
			if (state.deck.effect_costs.indexOf(cardId) > -1) {
				state.deck.effect_costs.splice(state.deck.effect_costs.indexOf(cardId), 1)
			} else {
				state.deck.effect_costs.push(cardId)
			}
		},
		setTutorTarget (state, payload) {
			if (!payload.targetId && state.deck.tutor_map[payload.tutorId]) {
				Vue.delete(state.deck.tutor_map, payload.tutorId)
			} else {
				Vue.set(state.deck.tutor_map, payload.tutorId, payload.targetId)
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
			// Disallow filtering by conjuration types when we have a non-basic dice type selected
			if (state.options.dice && state.options.dice.length > 0 &&
					state.options.dice.indexOf('basic') === -1 && state.options.types &&
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
				if (release !== 'promos') {
					onlyPromos = false
				}
			}
			if (onlyPromos) {
				const phoenixborn = state.cardManager.cardById(state.deck.phoenixborn)
				if (phoenixborn.release < 100) {
					state.options.releases = ['core']
				}
			}
		},
		setincludeAllCards (state, includeAllCards) {
			state.options.includeAllCards = includeAllCards
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
		setListing (state, listing) {
			state.listing = listing
		},
		setListType (state, listType) {
			state.options.listType = listType
			storeSet('listType', listType)
		},
		setTempListType (state, listType) {
			state.options.listType = listType
		},
		toggleAshes500 (state) {
			state.options.enableAshes500 = !state.options.enableAshes500
		},
		// Deck listing methods
		setShowDetails (state, value) {
			state.options.showDetails = value
			storeSet('showDetails', value)
		},
		// Setup the cardManager
		setCardManager (state, cardManager) {
			state.cardManager = cardManager
		},
		setAshes500Revision (state, revision) {
			state.ashes_500_revision = revision
		}
	},
	actions: {
		filterCards (context, options) {
			if (context.state.cardManager) {
				context.commit('setAppDisabled', true)
				context.state.cardManager.cardListing((cards) => {
					context.commit('setListing', cards)
					context.commit('setAppDisabled', false)
				}, options || context.state.options)
			} else if (!pendingFilterOptions) {
				pendingFilterOptions = options || true
				const nano = new Nanobar({ autoRun: true })
				context.commit('setAppDisabled', true)
				qwest.get('/api/cards/', null, {responseType: 'json'}).then((xhr, response) => {
					context.commit('setCardManager', new CardManager(response.cards))
					context.commit('setAshes500Revision', response.ashes_500_revision)
					context.dispatch(
						'filterCards',
						pendingFilterOptions !== true ? pendingFilterOptions : null
					)
				}).catch(function (error, xhr, response) {
					globals.notify('Server error! Unable to fetch card listing.', 'error')
					console.error('Server error when fetching card data:', error, xhr, response)
					context.commit('setAppDisabled', false)
				}).complete(() => {
					nano.go(100)
				})
			} else {
				pendingFilterOptions = options || true
			}
		},
		sortCards (context) {
			if (context.state.cardManager) {
				context.commit('setListing', context.state.cardManager.sortListing(context.state.listing, {
					primaryOrder: context.state.options.primaryOrder,
					primarySort: context.state.options.primarySort,
					secondaryOrder: context.state.options.secondaryOrder,
					secondarySort: context.state.options.secondarySort
				}))
			} else {
				context.dispatch('filterCards')
			}
		}
	}
})
