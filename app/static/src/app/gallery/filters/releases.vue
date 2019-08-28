<template>
	<div class="btn-group">
		<button @click="toggleReleases('phg')"
			class="btn btn-small" :class="{active: hasReleases('phg')}" :disabled="isDisabled"
			title="Only show Plaid Hat cards">PHG</button
		><button @click="toggleReleases('mine')"
			class="btn btn-small" :class="{active: hasReleases('mine')}" :disabled="isDisabled"
			title="Only show my cards">Mine</button
		>
	</div>
</template>

<script>
	import {includes} from 'lodash'
	import {globals} from 'app/utils'

	export default {
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			}
		},
		methods: {
			toggleReleases (releasesKey) {
				this.$store.commit('toggleReleases', releasesKey)
				this.$store.dispatch('filterCards')
			},
			hasReleases (releasesKey) {
				if (releasesKey === null || this.$store.state.options.releases === null) {
					return releasesKey === null && this.$store.state.options.releases === null
				}
				if (!includes(this.$store.state.options.releases, releasesKey)) {
					return false
				}
				return true
			}
		}
	}
</script>
