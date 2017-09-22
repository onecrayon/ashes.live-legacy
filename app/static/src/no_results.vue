<template>
	<li v-if="!listing.length" class="no-results">
		<h2>No cards found</h2>
		<p><button v-on:click="resetFilters" class="btn btn-primary">Clear filters</button></p>
	</li>
</template>

<script>
	export default {
		computed: {
			listing () {
				return this.$store.state.listing
			}
		},
		methods: {
			resetFilters () {
				this.$store.commit('resetFilters')
				this.$store.commit('filterCards')
			}
		}
	}
</script>

