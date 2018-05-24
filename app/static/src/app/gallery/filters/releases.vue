<template>
	<div class="btn-group">
		<button @click="toggleReleases('core')"
			class="btn btn-small" :class="{active: hasReleases('core')}" :disabled="isDisabled"
			>Core</button
		><button @click="toggleReleases('expansions')"
			class="btn btn-small" :class="{active: hasReleases('expansions')}" :disabled="isDisabled"
			title="Expansions">Exp.</button
		><button @click="toggleReleases('promos')"
			class="btn btn-small" :class="{active: hasReleases('promos')}" :disabled="isDisabled"
			title="Promos">Pro.</button
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
