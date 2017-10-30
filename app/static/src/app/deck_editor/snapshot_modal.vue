<template>
	<modal :show="show" @close="close">
		<h2 v-if="public">Publish Deck</h2>
		<h2 v-else>New Snapshot</h2>

		<p v-if="public"><strong>You are creating a public snapshot.</strong> Public snapshots cannot be deleted!</p>

		<div class="tabs btn-group">
			<button class="btn btn-small" :class="{active: activeTab == 'meta'}"
				@click="activeTab = 'meta'">Details</button
			><button class="btn btn-small" :class="{active: activeTab == 'deck'}"
				@click="activeTab = 'deck'">Deck</button
			>
		</div>

		<div v-if="activeTab === 'meta'">
			<div class="form-field">
				<input ref="title" v-model="title" type="text" :placeholder="untitledText">
			</div>

			<div class="form-field">
				<textarea ref="description" v-model="description" placeholder="Description"></textarea>
			</div>
		</div>
		<div v-else>
			<deck-listing view-only="true"></deck-listing>
		</div>

		<div class="text-right">
			<button class="btn" @click="close">Cancel</button>
			<button class="btn btn-primary" @click="saveSnapshot">
				<i class="fa" :class="{'fa-camera': !public, 'fa-share-square-o': public}"></i>
				<span v-if="public">Publish</span>
				<span v-else>Save</span>
			</button>
		</div>
	</modal>
</template>

<script>
	import qwest from 'qwest'
	import DeckListing from 'app/components/deck_listing.vue'
	import Modal from 'app/components/modal.vue'

	export default {
		components: {
			'deck-listing': DeckListing,
			'modal': Modal,
		},
		props: ['show', 'public'],
		data () {
			return {
				'activeTab': 'meta',
				'_title': null,
				'_description': null
			}
		},
		computed: {
			title: {
				get () {
					if (this._title || this._title === '') return this._title
					return this.$store.state.deck.title
				},
				set (value) {
					this._title = value
				}
			},
			untitledText () {
				return this.$store.getters.untitledText
			},
			description: {
				get () {
					if (this._description || this._description === '') return this._description
					return this.$store.state.deck.description
				},
				set (value) {
					this._description = value
				}
			}
		},
		methods: {
			saveSnapshot () {
				console.log('save snapshot!')
				this.close()
			},
			close () {
				this.$emit('close')
				// Reset everything
				this.activeTab = 'meta'
				this._title = null
				this._description = null
			}
		}
	}
</script>

