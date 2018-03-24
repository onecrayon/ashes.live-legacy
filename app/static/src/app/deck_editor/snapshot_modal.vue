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
				<textarea-helpers @actOnText="modifyText"></textarea-helpers>
				<textarea ref="description" v-model="description" placeholder="Description"></textarea>
				<p class="help-text"><em>Supports [[card codes]] and *star formatting*.</em></p>
			</div>
		</div>
		<div v-else>
			<h3><card-link :card="phoenixborn"></card-link></h3>
			<ul class="dice">
				<li v-for="(die, index) of diceList" :key="index"
						class="die" :class="[die ? die : 'basic']">
					<span :class="'phg-' + (die ? die + '-power' : 'basic-magic')"></span>
				</li>
			</ul>
			<deck-listing view-only="true"></deck-listing>
		</div>

		<div class="modal-controls" slot="footer">
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
	import Nanobar from 'app/nanobar'
	import CardLink from 'app/components/card_link.vue'
	import DeckListing from 'app/components/deck_listing.vue'
	import Modal from 'app/components/modal.vue'
	import TextareaHelpers from 'app/components/textarea_helpers.vue'
	import {actOnText, notify} from 'app/utils'

	export default {
		components: {
			'card-link': CardLink,
			'deck-listing': DeckListing,
			'modal': Modal,
			'textarea-helpers': TextareaHelpers,
		},
		props: ['show', 'public'],
		data () {
			return {
				'activeTab': 'meta',
				'title': null,
				'description': null
			}
		},
		computed: {
			untitledText () {
				return this.$store.getters.untitledText
			},
			diceList () {
				let diceArray = new Array(10)
				let nextIndex = 0
				for (let dieType of Object.keys(this.$store.state.deck.dice)) {
					const numDice = this.$store.state.deck.dice[dieType]
					const maxIndex = nextIndex + numDice
					while (nextIndex < maxIndex && nextIndex < 10) {
						diceArray[nextIndex] = dieType
						nextIndex++
					}
				}
				while (nextIndex < 10) {
					diceArray[nextIndex] = null
					nextIndex++
				}
				return diceArray
			},
			phoenixborn () {
				return this.$store.getters.phoenixborn
			}
		},
		watch: {
			show (value) {
				if (value) {
					// Reset everything
					this.activeTab = 'meta'
					this.title = this.$store.state.deck.title
					this.description = this.$store.state.deck.description
					this.$nextTick(() => {
						this.$refs.title.focus()
					})
				}
			}
		},
		methods: {
			modifyText (actions) {
				const logic = actOnText(
					this.description,
					this.$refs.description.selectionStart,
					this.$refs.description.selectionEnd,
					actions
				)
				if (!logic) return
				this.description = logic.text
				this.$nextTick(() => {
					this.$refs.description.setSelectionRange(logic.start, logic.end)
				})
			},
			saveSnapshot () {
				const title = this.title || this.untitledText
				const description = this.description || ''
				const nano = new Nanobar({ autoRun: true })
				qwest.post(
					'/api/decks/snapshot',
					{
						'title': title,
						'description': description,
						'phoenixborn': this.$store.state.deck.phoenixborn,
						'dice': this.$store.state.deck.dice,
						'cards': this.$store.state.deck.cards,
						'source_id': this.$store.state.deck.id,
						'is_snapshot': true,
						'is_public': this.public
					},
					{dataType: 'json'}
				).then((xhr, response) => {
					if (response.validation) {
						return notify(response.validation.title, 'error')
					} else if (response.error) {
						return notify(response.error, 'error')
					} else if (response.success) {
						notify(response.success, 'success')
					}
					this.close()
				}).complete(() => {
					nano.go(100)
				})
			},
			close () {
				this.$emit('close')
			}
		}
	}
</script>

