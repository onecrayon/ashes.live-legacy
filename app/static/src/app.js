import Vue from 'vue'
import Vuex from 'vuex'
import CardManager from './card_manager'
import DeckMeta from './deck_meta.vue'
import CardGallery from './card_gallery.vue'

Vue.use(Vuex)

/* eslint-disable no-new */

var cardManager = new CardManager

var store = new Vuex.Store({
	state: {
		deck: {
			title: '',
			description: '',
			phoenixborn: null,
			dice: [],
			cards: []
		},
		listing: [],
		filters: {
			search: null,
			types: null,
			releases: [0],
			dice: null,
			diceLogic: 'or',
			primarySort: 'name',
			primaryOrder: 1,
			secondarySort: null,
			secondaryOrder: 1
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
		},
		addDice (state, die, number) {
			number = number || 1
			while (number) {
				state.deck.dice.push(die)
				number--
			}
			while (state.deck.dice.length > 10) {
				state.deck.dice.shift()
			}
		},
		replaceDie (state, index, die) {
			state.deck.dice[index] = die
		},
		// Filter methods
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
		// Sorting methods
		toggleSortOrder (state) {
			state.filters.primaryOrder *= -1
			state.filters.secondaryOrder *= -1
		},
		setSort (state, field) {
			if (field != 'name') {
				state.filters.primarySort = field
				state.filters.secondarySort = 'name'
			} else {
				state.filters.primarySort = 'name'
				state.filters.secondarySort = null
			}
		},
		filterCards (state, options) {
			options = options || state.filters
			state.listing = cardManager.cardListing(options)
		},
		// TODO: add methods for incrementing and decrementing card counts
	}
})

var vm = new Vue({
	el: '#main',
	store,
	render (createElement) {
		return createElement('div',{
			domProps: {
				id: 'main'
			}
		}, [
			createElement(DeckMeta),
			createElement(CardGallery)
		])
	}
})
