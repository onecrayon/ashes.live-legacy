import Vue from 'vue'
import store from 'app/store'
import DeckEditor from 'app/deck_editor/main.vue'
import CardGallery from 'app/gallery/main.vue'

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
			createElement(DeckEditor),
			createElement(CardGallery)
		])
	}
})
