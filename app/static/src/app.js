import Vue from 'vue'
import store from './store'
import DeckMeta from './deck_meta.vue'
import CardGallery from './card_gallery.vue'

/* eslint-disable no-new */

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
