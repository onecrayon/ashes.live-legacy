import Vue from 'vue'

/* eslint-disable no-new */
var vm = new Vue({
	el: '#main',
	render: function(createElement) {
		return createElement('p', ['Coming soon!'])
	}
})
