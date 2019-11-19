<template>
	<modal :show="show" @close="close">
		<h2>Configure your collection</h2>

		<div class="btn-group">
			<button class="btn btn-small" @click="selectRetail" :disabled="isDisabled">Retail</button
			><button class="btn btn-small" @click="selectPromos" :disabled="isDisabled">Promos</button
			><button class="btn btn-small" @click="selectFanMade" :disabled="isDisabled">PnP</button
			><button class="btn btn-small btn-danger" @click="selectNone" :disabled="isDisabled">Clear</button>
		</div>

		<ul class="releases-form">
			<li v-for="release of releaseList" :key="release.id"
				:class="{
					'retail-release': release.is_phg && !release.is_promo,
					'fan-release': !release.is_phg,
					'promo-release': release.is_promo,
					'core-release': isCore(release)
				}">
				<label>
					<input type="checkbox" :checked="includes(selectedReleases, release.id)"
						:disabled="isCore(release) || isDisabled"
						@change="setRelease(release.id, $event)">
					{{ release.name }}
				</label>
			</li>
		</ul>

		<div class="modal-controls" slot="footer">
			<button class="btn" @click="close" :disabled="isDisabled">Cancel</button>
			<button class="btn btn-success" @click="save" :disabled="isDisabled">Save</button>
		</div>
	</modal>
</template>

<script>
	import qwest from 'qwest'
	import Modal from 'app/components/modal.vue'
	import Nanobar from 'app/nanobar'
	import {includes} from 'lodash'
	import {globals, notify} from 'app/utils'

	export default {
		components: {
			'modal': Modal
		},
		props: ['show'],
		data: () => ({
			selectedReleases: [1]
		}),
		created () {
			this.setDefaultCollection()
		},
		computed: {
			releaseList () {
				return globals.releaseList
			},
			isDisabled () {
				return this.$store.state.isDisabled
			}
		},
		methods: {
			includes,
			setDefaultCollection () {
				if (this.$store.state.options.userCollection && this.$store.state.options.userCollection.length) {
					this.selectedReleases = this.$store.state.options.userCollection.slice(0)
				} else {
					this.selectedReleases = [1]
				}
			},
			isCore (release) {
				return release.id === 1
			},
			setRelease (id, event) {
				const index = this.selectedReleases.indexOf(id)
				if (index > -1) {
					this.selectedReleases.splice(index, 1)
				} else {
					this.selectedReleases.push(id)
				}
				// Ensure the core set is always included
				if (!includes(this.selectedReleases, 1)) {
					this.selectedReleases.push(1)
				}
			},
			selectRetail () {
				const releaseSet = new Set(this.selectedReleases)
				// Ensure the core set is always selected
				releaseSet.add(1)
				const phgReleases = globals.releaseList.filter(release => release.is_phg && !release.is_promo)
				for (const release of phgReleases) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectPromos () {
				const releaseSet = new Set(this.selectedReleases)
				// Ensure the core set is always selected
				releaseSet.add(1)
				const promos = globals.releaseList.filter(release => release.is_promo)
				for (const release of promos) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectFanMade () {
				const releaseSet = new Set(this.selectedReleases)
				// Ensure the core set is always selected
				releaseSet.add(1)
				const fanMade = globals.releaseList.filter(release => !release.is_phg)
				for (const release of fanMade) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectNone () {
				this.selectedReleases = []
			},
			close () {
				this.$emit('close')
				this.setDefaultCollection()
				this.selectedReleases = this.$store.state.options.userCollection && this.$store.state.options.userCollection.slice(0) || [1]
			},
			save () {
				const nano = new Nanobar({ autoRun: true })
				this.$store.commit('setAppDisabled', true)
				qwest.post(
					'/api/cards/collection',
					this.selectedReleases,
					{dataType: 'json'}
				).then((xhr, response) => {
					// Configure global personal release list and refresh listing
					this.$store.commit('setUserCollection', response)
					// Ensure that "mine" is selected, and refresh the listing
					if (response && response.length > 0) {
						this.$store.commit('setReleases', 'mine')
					} else {
						this.$store.commit('setReleases', 'phg')
					}
					this.$store.dispatch('filterCards')
				}).catch((error, xhr, response) => {
					if (response.error) {
						notify(response.error, 'error')
					} else {
						notify('Server error: ' + error, 'error')
					}
				}).complete(() => {
					this.$store.commit('setAppDisabled', false)
					this.close()
					nano.go(100)
				})
			}
		}
	}
</script>

