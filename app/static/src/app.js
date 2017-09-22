import Vue from 'vue'
import Vuex from 'vuex'
import CardManager from './card_manager'
import DeckMeta from './deck_meta.vue'
import CardGallery from './card_gallery.vue'

Vue.use(Vuex)

/* eslint-disable no-new */

var cardManager = new CardManager

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
		listType: 'list',
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
