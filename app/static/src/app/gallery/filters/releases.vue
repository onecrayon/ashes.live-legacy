<template>
	<div class="btn-group">
		<button @click="toggleReleases('core')"
			class="btn btn-small" :class="{active: hasReleases('core')}"
			>Core</button
		><button @click="toggleReleases('expansions')"
			class="btn btn-small" :class="{active: hasReleases('expansions')}"
			title="Expansions">Exp.</button
		><button @click="toggleReleases('promos')"
			class="btn btn-small" :class="{active: hasReleases('promos')}"
			title="Promos">Pro.</button
		>
	</div>
</template>

<script>
	import {includes} from 'lodash'

	export default {
		methods: {
			toggleReleases (releasesKey) {
				this.$store.commit('toggleReleases', globals.releaseData[releasesKey])
				this.$store.commit('filterCards')
			},
			hasReleases (releasesKey) {
				if (releasesKey === null || this.$store.state.filters.releases === null) {
					return releasesKey === null && this.$store.state.filters.releases === null
				}
				for (let release of globals.releaseData[releasesKey]) {
					if (!includes(this.$store.state.filters.releases, release)) {
						return false
					}
				}
				return true
			}
		}
	}
</script>
