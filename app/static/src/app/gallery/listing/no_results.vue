<template>
	<li v-if="!listing.length && !isDisabled" class="no-results">
		<h2>No cards found</h2>
		<p><button @click="resetFilters" class="btn btn-primary">Clear filters</button></p>
	</li>
	<li v-else-if="!listing.length" class="loading-results">
		<p class="callout muted"><i class="fa fa-spinner fa-spin" aria-hidden="true"></i> Loading cards...</p>
	</li>
</template>

<script>
	export default {
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			},
			listing () {
				return this.$store.state.listing
			}
		},
		methods: {
			resetFilters () {
				this.$store.commit('resetFilters')
				this.$store.dispatch('filterCards')
			}
		}
	}
</script>

