<template>
	<a :href="href" class="card" target="_blank"><slot>{{ card.name }}</slot></a>
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
		}
	}
</script>

