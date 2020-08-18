<template>
	<a :href="href" class="card" :class="{'not-owned': isNotOwned, 'fan-made': !card.release.is_phg, 'is-retiring': card.release.is_retiring}" :target="target"><slot>{{ card.name }}</slot></a>
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
			},
			isNotOwned () {
				return this.$store.state.options.releases === 'mine' && this.$store.state.options.userCollection && !this.$store.state.options.userCollection.includes(this.card.release.id)
			}
		}
	}
</script>

