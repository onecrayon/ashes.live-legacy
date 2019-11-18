<template>
	<modal :show="show" @close="close">
		<h2>Configure your collection</h2>

		<div class="btn-group">
			<button class="btn btn-small" @click="selectRetail">Retail</button
			><button class="btn btn-small" @click="selectPromos">Promos</button
			><button class="btn btn-small" @click="selectFanMade">PnP</button
			><button class="btn btn-small btn-danger" @click="selectNone">Clear</button>
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
						:disabled="isCore(release)"
						@change="setRelease(release.id, $event)">
					{{ release.name }}
				</label>
			</li>
		</ul>

		<div class="modal-controls" slot="footer">
			<button class="btn" @click="close">Cancel</button>
			<button class="btn btn-success" @click="save">Save</button>
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
			selectedReleases: globals.userCollection && globals.userCollection.slice(0) || [1]
		}),
		computed: {
			releaseList () {
				return globals.releaseList
			}
		},
		methods: {
			includes,
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
			},
			selectRetail () {
				const releaseSet = new Set(this.selectedReleases)
				const phgReleases = globals.releaseList.filter(release => release.is_phg && !release.is_promo)
				for (const release of phgReleases) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectPromos () {
				const releaseSet = new Set(this.selectedReleases)
				const promos = globals.releaseList.filter(release => release.is_promo)
				for (const release of promos) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectFanMade () {
				const releaseSet = new Set(this.selectedReleases)
				const fanMade = globals.releaseList.filter(release => !release.is_phg)
				for (const release of fanMade) {
					releaseSet.add(release.id)
				}
				this.selectedReleases = Array.from(releaseSet)
			},
			selectNone () {
				this.selectedReleases = [1]
			},
			close () {
				this.$emit('close')
				this.selectedReleases = globals.userCollection && globals.userCollection.slice(0) || [1]
			},
			save () {
				console.log('saved!')
				this.close()
				return
				// TODO
				const nano = new Nanobar({ autoRun: true })
				qwest.post('/api/releases', this.selectedReleases).then(() => {
					// TODO: configure global personal release list and refresh listing

					// Ensure that "mine" is selected, and refresh the listing
					this.$store.commit('toggleReleases', 'mine')
					this.$store.dispatch('filterCards')
				}).catch((error, xhr, response) => {
					if (response.error) {
						notify(response.error, 'error')
					} else {
						notify('Server error: ' + error, 'error')
					}
					this.close()
				}).complete(() => {
					nano.go(100)
				})
			}
		}
	}
</script>

