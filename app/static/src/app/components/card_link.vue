<template>
	<a :href="href" @touchstart="touchStarted" @touchmove="touchMoved" @touchend="touchEnded"
		class="card" target="_blank"><slot>{{ card.name }}</slot></a>
</template>

<script>
	import {initCardTooltips, teardownTooltips, cardUrl} from 'app/utils'

	export default {
		props: ['card'],
		mounted: function () {
			initCardTooltips.call(this, this.$el)
		},
		updated: function () {
			teardownTooltips.call(this)
			initCardTooltips.call(this, this.$el)
		},
		beforeDestroy: teardownTooltips,
		computed: {
			href () {
				return cardUrl(this.card)
			}
		},
		methods: {
			touchStarted (event) {
				this.$el.setAttribute('data-touch-moved', '0')
			},
			touchMoved (event) {
				this.$el.setAttribute('data-touch-moved', '1')
			},
			touchEnded (event) {
				if (this.$el.getAttribute('data-touch-moved') === '0') {
					if (!this.$el.getAttribute('data-touch-active')) {
						event.preventDefault()
						// Simulate a click event on the document to auto-close all other tooltips
						document.dispatchEvent(new MouseEvent('click'))
						// And show the current tooltip
						this.tip.show(this.tip.getPopperElement(this.$el))
					}
				}
				this.$el.removeAttribute('data-touch-moved')
			}
		}
	}
</script>

