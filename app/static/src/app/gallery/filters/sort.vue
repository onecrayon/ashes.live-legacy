<template>
	<div class="btn-group">
		<button @click="toggleOrdering()"
			class="btn btn-small">Sort <i class="fa" :class="orderIconClass"></i></button
		><button @click="sortBy('name')"
			class="btn btn-small" :class="{active: isSortedBy('name')}">Name</button
		><button v-if="normalListing" @click="sortBy('type')"
			class="btn btn-small" :class="{active: isSortedBy('type')}">Type</button
		><button v-if="normalListing" @click="sortBy('dice')"
			class="btn btn-small" :class="{active: isSortedBy('dice')}">Dice</button
		><button v-if="normalListing" @click="sortBy('weight')"
			class="btn btn-small" :class="{active: isSortedBy('weight')}">Cost</button
		><button v-if="!normalListing" @click="sortBy('life')"
			class="btn btn-small" :class="{active: isSortedBy('life')}">Life</button
		><button v-if="!normalListing" @click="sortBy('battlefield')"
			class="btn btn-small" :class="{active: isSortedBy('battlefield')}">Battlefield</button
		><button v-if="!normalListing" @click="sortBy('spellboard')"
			class="btn btn-small" :class="{active: isSortedBy('spellboard')}">Spellboard</button
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
