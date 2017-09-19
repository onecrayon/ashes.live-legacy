<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<card-filters></card-filters>
			<card-listing></card-listing>
		</div>
		<div v-else class="phoenixborn-picker">
			<ul class="listing">
				<li v-for="card of listing" :key="card.id">
					<img v-on:click="phoenixborn = card.id" :src="card.images.compressed" :alt="card.name">
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import CardFilters from './card_filters.vue'
	import CardListing from './card_listing.vue'
	
	export default {
		components: {
			'card-filters': CardFilters,
			'card-listing': CardListing
		},
		created () {
			if (this.$store.state.deck.phoenixborn) {
				this.$store.commit('filterCards')
			} else {
				this.$store.commit('filterCards', {types: ['Phoenixborn']})
			}
		},
		computed: {
			phoenixborn: {
				get () {
					return this.$store.state.deck.phoenixborn
				},
				set (cardId) {
					this.$store.commit('setPhoenixborn', cardId)
					this.$store.commit('filterCards')
				}
			},
			listing () {
				return this.$store.state.listing
			}
		}
	}
</script>
