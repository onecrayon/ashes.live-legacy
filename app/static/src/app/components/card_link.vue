<template>
	<a :href="href" class="card" :target="target"><slot>{{ card.name }}</slot></a>
</template>

<script>
	import {initCardTooltips, teardownTooltips, cardUrl, globals} from 'app/utils'

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
			},
			target () {
				return globals.galleryOnly ? false : '_blank'
			}
		}
	}
</script>

