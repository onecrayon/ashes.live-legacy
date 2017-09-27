<template>
	<div class="btn-group">
		<button @click="toggleReleases([0])"
			class="btn btn-small" :class="{active: hasReleases([0])}"
			>Core</button
		><button @click="toggleReleases([1, 2, 3, 4, 5, 6])"
			class="btn btn-small" :class="{active: hasReleases([1, 2, 3, 4, 5, 6])}"
			title="Expansions">Exp.</button
		><button @click="toggleReleases([101, 102, 103])"
			class="btn btn-small" :class="{active: hasReleases([101, 102, 103])}"
			title="Promos">Pro.</button
		>
	</div>
</template>

<script>
	import {includes} from 'lodash'

	export default {
		methods: {
			toggleReleases (releases) {
				this.$store.commit('toggleReleases', releases)
				this.$store.commit('filterCards')
			},
			hasReleases (releases) {
				if (releases === null || this.$store.state.filters.releases === null) {
					return releases === this.$store.state.filters.releases
				}
				for (let release of releases) {
					if (!includes(this.$store.state.filters.releases, release)) {
						return false
					}
				}
				return true
			}
		}
	}
</script>
