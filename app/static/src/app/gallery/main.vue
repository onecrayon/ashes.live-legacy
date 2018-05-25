<template>
	<div :id="isCardGallery ? 'gallery' : 'editor-gallery'">
		<div v-if="isCardGallery || phoenixborn" class="gallery">
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
					<a @click.prevent="phoenixborn = card.id" :href="cardUrl(card)">
						<span class="loading-text">
							<i class="fa fa-spinner fa-spin" aria-hidden="true"></i><br>
							{{ card.name }}
						</span>
						<img :src="assetPath(card.images.compressed)" :alt="card.name">
						<div v-if="isAshes500Enabled" class="ashes-500-overlay">
							<i class="fa fa-tachometer" aria-hidden="true"></i>
							<ashes-500-costs :card="card"></ashes-500-costs>
						</div>
					</a>
				</li>
			</ul>
		</div>
	</div>
</template>

<script>
	import CardFilters from './filters/main.vue'
	import CardListing from './listing/main.vue'
	import DiceFilter from './filters/dice.vue'
	import ReleaseFilter from './filters/releases.vue'
	import SortFilter from './filters/sort.vue'
	import TextFilter from './filters/text.vue'
	import NoResults from './listing/no_results.vue'
	import Ashes500Costs from 'app/components/ashes_500_costs.vue'
	import {assetPath, cardUrl, globals} from 'app/utils'
	
	export default {
		components: {
			'card-filters': CardFilters,
			'card-listing': CardListing,
			'dice-filter': DiceFilter,
			'release-filter': ReleaseFilter,
			'sort-filter': SortFilter,
			'text-filter': TextFilter,
			'no-results': NoResults,
			'ashes-500-costs': Ashes500Costs,
		},
		created () {
			if (this.isCardGallery) {
				this.$store.commit('setincludeAllCards', true)
				this.$store.commit('setTempListType', 'table')
			} else if (!this.$store.state.deck.phoenixborn) {
				this.$store.commit('setTypes', ['Phoenixborn'])
			}
			this.$store.dispatch('filterCards')
		},
		computed: {
			phoenixborn: {
				get () {
					return this.$store.getters.phoenixborn
				},
				set (cardId) {
					this.$store.commit('setPhoenixborn', cardId)
					this.$store.commit('setTypes', null)
					this.$store.dispatch('filterCards')
				}
			},
			listing () {
				return this.$store.state.listing
			},
			isCardGallery () {
				return globals.galleryOnly
			},
			isAshes500Enabled () {
				return this.$store.state.options.enableAshes500
			},
		},
		methods: {
			assetPath,
			cardUrl
		}
	}
</script>
