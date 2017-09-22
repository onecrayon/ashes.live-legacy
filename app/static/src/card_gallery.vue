<template>
	<div id="editor-gallery">
		<div v-if="phoenixborn" class="gallery">
			<card-filters></card-filters>
			<card-listing></card-listing>
		</div>
		<div v-else class="phoenixborn-picker">
			<div class="filters">
				<div class="responsive-cols main-filters">
					<dice-filter class="col"></dice-filter>
					<text-filter class="col-flex"></text-filter>
				</div>
				<div class="responsive-cols listing-controls">
					<sort-filter class="col"></sort-filter>
					<release-filter class="col"></release-filter>
				</div>
			</div>	
			<ul class="listing">
				<no-results></no-results>
				<li v-for="card of listing" :key="card.id">
					<a v-on:click.prevent="phoenixborn = card.id" :href="cardUrl(card)" class="card">
						<img :src="card.images.compressed" :alt="card.name">
					</a>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import CardFilters from './card_filters.vue'
	import CardListing from './card_listing.vue'
	import DiceFilter from './filters/dice.vue'
	import ReleaseFilter from './filters/releases.vue'
	import SortFilter from './filters/sort.vue'
	import TextFilter from './filters/text.vue'
	import NoResults from './no_results.vue'
	import {cardUrl} from './utils'
	
	export default {
		components: {
			'card-filters': CardFilters,
			'card-listing': CardListing,
			'dice-filter': DiceFilter,
			'release-filter': ReleaseFilter,
			'sort-filter': SortFilter,
			'text-filter': TextFilter,
			'no-results': NoResults
		},
		created () {
			if (!this.$store.state.deck.phoenixborn) {
				this.$store.commit('setTypes', ['Phoenixborn'])
			}
			this.$store.commit('filterCards')
		},
		computed: {
			phoenixborn: {
				get () {
					return this.$store.state.deck.phoenixborn
				},
				set (cardId) {
					this.$store.commit('setPhoenixborn', cardId)
					this.$store.commit('setTypes', null)
					this.$store.commit('filterCards')
				}
			},
			listing () {
				return this.$store.state.listing
			}
		},
		methods: {
			cardUrl
		}
	}
</script>
