<template>
	<modal :show="show" @close="close">
		<h2>Configure your collection</h2>

		<!-- LEFT OFF: need to switch to a list of objects, or just reuse the release mapping that Python already uses; need to be able to call out promos and fan-made stuff -->
		<ul class="releases-form">
			<li v-for="release of releaseList" :key="release[0]">
				<label>
					<input type="checkbox" :checked="isCore(release) || includes(userCollection, release[0])"
						:disabled="isCore(release)" :value="release[0]">
					{{ release[1] }}
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
		computed: {
			releaseList () {
				return globals.releaseList
			},
			userCollection () {
				return globals.userCollection || []
			}
		},
		methods: {
			includes,
			isCore (release) {
				return release[0] === 1
			},
			close () {
				this.$emit('close')
			},
			save () {
				console.log('saved!')
				this.close()
				return
				// TODO
				const nano = new Nanobar({ autoRun: true })
				qwest.post('/api/releases').then(() => {
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

