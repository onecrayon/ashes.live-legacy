import Vue from 'vue'
import Vuex from 'vuex'
import DeckMeta from './deck_meta.vue'
import CardGallery from './card_gallery.vue'

Vue.use(Vuex)

/* eslint-disable no-new */

var store = new Vuex.Store({
	state: {
		deck: {
			title: '',
			phoenixborn: null
		}
	},
	mutations: {
		title: function (state, title) {
			state.deck.title = title
		},
		phoenixborn: function (state, id) {
			state.deck.phoenixborn = id
		}
	}
})

var vm = new Vue({
	el: '#main',
	store,
	render: function(createElement) {
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
