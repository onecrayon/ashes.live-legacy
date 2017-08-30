import Vue from 'vue'
import Vuex from 'vuex'
import CardManager from './card_manager'
import DeckMeta from './deck_meta.vue'
import CardGallery from './card_gallery.vue'

Vue.use(Vuex)

/* eslint-disable no-new */

var cardManager = new CardManager()

var store = new Vuex.Store({
	state: {
		deck: {
			title: '',
			description: '',
			phoenixborn: null,
			dice: [],
			cards: []
		},
		cards: cardManager
	},
	mutations: {
		setTitle: function (state, title) {
			state.deck.title = title
		},
		setDescription: function (state, description) {
			state.deck.description = description
		},
		setPhoenixborn: function (state, id) {
			state.deck.phoenixborn = id
		},
		addDice: function (state, die, number) {
			number = number || 1
			while (number) {
				state.deck.dice.push(die)
				number--
			}
			while (state.deck.dice.length > 10) {
				state.deck.dice.shift()
			}
		},
		replaceDie: function (state, index, die) {
			state.deck.dice[index] = die
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
