<template>
	<div class="btn-group">
		<button @click="toggleOrdering()" class="btn btn-small"
			:title="'Sorted in ' + sortOrder + ' order'"
			>Sort <i class="fa" :class="orderIconClass"></i></button
		><button @click="sortBy('name')"
			class="btn btn-small" :class="{active: isSortedBy('name')}"
			title="Sort alphabetically by name">Name</button
		><button v-if="normalListing" @click="sortBy('type')"
			class="btn btn-small" :class="{active: isSortedBy('type')}"
			title="Group by card type, then sort by name">Type</button
		><button v-if="normalListing" @click="sortBy('weight')"
			class="btn btn-small" :class="{active: isSortedBy('weight')}"
			title="Sort by play cost">Cost</button
		><button v-if="normalListing" @click="sortBy('dice')"
			class="btn btn-small" :class="{active: isSortedBy('dice')}"
			title="Group by dice required, then sort by cost">Dice</button
		><button v-if="!normalListing" @click="sortBy('life')"
			class="btn btn-small" :class="{active: isSortedBy('life')}"
			title="Sort by life value">Life</button
		><button v-if="!normalListing" @click="sortBy('battlefield')"
			class="btn btn-small" :class="{active: isSortedBy('battlefield')}"
			title="Sort by battlefield value">Battlefield</button
		><button v-if="!normalListing" @click="sortBy('spellboard')"
			class="btn btn-small" :class="{active: isSortedBy('spellboard')}"
			title="Sort by spellboard value">Spellboard</button
		>
	</div>
</template>

<script>
	import {globals} from 'app/utils'

	export default {
		computed: {
			normalListing () {
				return !!this.$store.state.deck.phoenixborn || globals.galleryOnly
			},
			orderIconClass () {
				return 'fa-chevron-' + (this.$store.state.options.primaryOrder === 1 ? 'up' : 'down')
			},
			sortOrder () {
				return this.$store.state.options.primaryOrder === 1 ? 'ascending' : 'descending'
			}
		},
		methods: {
			toggleOrdering () {
				this.$store.commit('toggleSortOrder')
				this.$store.dispatch('sortCards')
			},
			sortBy (field) {
				this.$store.commit('setSort', field)
				this.$store.dispatch('sortCards')
			},
			isSortedBy (field) {
				return this.$store.state.options.primarySort === field
			}
		}
	}
</script>
