<template>
	<div>
		<div class="btn-group">
			<button @click="toggleReleases('phg')"
				class="btn btn-small" :class="{active: hasReleases('phg')}" :disabled="isDisabled"
				title="Only show Plaid Hat cards">PHG</button
			><button @click="toggleReleases('mine')"
				class="btn btn-small" :class="{active: hasReleases('mine')}" :disabled="isDisabled"
				title="Only show my cards">Mine</button
			><button @click="showReleaseModal = true"
				class="btn btn-small" :disabled="isDisabled"
				title="Configure my collection"><i class="fa fa-cog"></i></button
			>
		</div>
		<release-modal :show="showReleaseModal" @close="showReleaseModal = false"></release-modal>
	</div>
</template>

<script>
	import {includes} from 'lodash'
	import {globals} from 'app/utils'
	import ReleaseModal from './release_modal.vue'

	export default {
		components: {
			'release-modal': ReleaseModal
		},
		data: () => ({
			showReleaseModal: false
		}),
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
