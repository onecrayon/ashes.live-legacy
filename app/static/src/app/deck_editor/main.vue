<template>
	<div id="editor-meta" :class="{active: editorOpen}">
		<div class="deck-header responsive-cols">
			<div class="col mobile-only">
				<button @click="toggleEditorPane()" class="btn btn-default">
					<i class="fa" :class="'fa-angle-double-' + (editorOpen ? 'down' : 'up')"
						title="Expand deck listing"></i>
				</button>
			</div>
			<div class="col-flex">
				<div class="input-group">
					<div class="form-field">
						<input v-model="title" :disabled="!phoenixborn" type="text" :placeholder="untitledText">
					</div>
					<button @click="save" :disabled="!phoenixborn" class="btn btn-primary">Save</button>
				</div>
			</div>
		</div>
		<div v-if="!phoenixborn">
			<p class="callout">Choose your deck's Phoenixborn to get started! <span class="muted">(Don't worry, you can always change your mind.)</span></p>
		</div>
		<div v-else class="tabs btn-group">
			<button class="btn btn-small" :class="{active: activeTab == 'deck'}"
				@click="activeTab = 'deck'" :disabled="!phoenixborn">Deck</button
			><button class="btn btn-small" :class="{active: activeTab == 'meta'}"
				@click="activeTab = 'meta'" :disabled="!phoenixborn">Meta</button
			><button class="btn btn-small" :class="{active: activeTab == 'actions'}"
				@click="activeTab = 'actions'" :disabled="!phoenixborn">Actions</button>
		</div>
		<div v-if="activeTab == 'deck' && phoenixborn">
			<h3 class="phoenixborn-header">
				<span @click="clearPhoenixborn" class="fa fa-refresh refresh-btn" :class="{disabled: isDisabled === true}" title="Swap Phoenixborn"></span>
				<card-link :card="phoenixborn"></card-link>
				<span @click="showDetails = !showDetails" class="fa details-btn"
					:class="showDetails ? 'fa-toggle-up' : 'fa-toggle-down'" title="Toggle Details"></span>
			</h3>
			<div v-if="showDetails" class="phoenixborn-detail">
				<ul class="statline">
					<li class="battlefield">Battlefield {{ phoenixborn.battlefield }}</li>
					<li class="life">Life {{ phoenixborn.life }}</li>
					<li class="spellboard">Spellboard {{ phoenixborn.spellboard }}</li>
				</ul>
				<card-effects :card="phoenixborn" all-text="true"></card-effects>
			</div>
			<ul v-if="showDetails" class="dice">
				<li v-for="(die, index) of diceList" :key="index"
						class="die" :class="[die ? die : 'basic']"
						@click="clearDie(die)">
					<span :class="'phg-' + (die ? die + '-power' : 'basic-magic')"></span>
				</li>
			</ul>
			<div class="dice-management responsive-cols">
				<die-counter v-for="dieType of diceNames" :key="dieType" :die-type="dieType" class="col"></die-counter>
			</div>
			<div class="dice-controls responsive-cols">
				<div class="col">
					<button class="btn btn-small" @click="clearDice" :disabled="diceEmpty">
						<i class="fa fa-times"></i> Clear Dice
					</button>
				</div>
				<div class="col">
					<button class="btn btn-small" @click="setDiceFilters" :disabled="diceEmpty || isDisabled">
						Set Dice Filter <i class="fa fa-arrow-right desktop-only"></i>
					</button>
				</div>
			</div>
			<hr>
			<deck-listing></deck-listing>
		</div>
		<div v-else-if="activeTab == 'meta' && phoenixborn">
			<button class="btn btn-block" :class="{'btn-success': !isAshes500Enabled}" @click="toggleAshes500">
				<i class="fa fa-tachometer" aria-hidden="true"></i> {{ ashes500ToggleWord }} Ashes 500
			</button>
			<p><a href="/ashes-500/" target="_blank"><strong>Ashes 500</strong></a> is an alternate constructed format where your deck must cost 500 points or less.</p>
			<hr>
			<h3>Description</h3>
			<text-editor state-path="deck.description" field-name="Description"></text-editor>
		</div>
		<div v-else-if="activeTab == 'actions' && phoenixborn">
			<h3>Snapshots</h3>

			<p>Save snapshots of your deck to track changes over time. <span v-if="!isSaved" class="muted">(Save your deck to enable.)</span></p>

			<button class="btn btn-primary btn-block" :disabled="!isSaved" @click="newSnapshot(false)">
				<i class="fa fa-camera"></i> New Snapshot
			</button>
			<a class="btn btn-block" :class="{disabled: !isSaved}" :href="historyUrl" target="_blank">
				<i class="fa fa-history"></i> View History
			</a>

			<p>Publishing your deck will create a public snapshot for others to view!</p>

			<button class="btn btn-success btn-block" :disabled="!isSaved" @click="newSnapshot(true)">
				<i class="fa fa-share-square-o"></i> Publish Deck
			</button>
			<snapshot-modal :show="showSnapshotModal" :public="createPublicSnapshot" @close="closeSnapshotModal"></snapshot-modal>
			<hr>
			<button class="btn btn-block" @click="showExportModal = true">
				<i class="fa fa-share-square-o"></i> Export As Text
			</button>
			<export-modal :show="showExportModal" @close="showExportModal = false"></export-modal>
			<button class="btn btn-block btn-danger" :disabled="!isSaved" @click="showDeleteModal = true">
				<i class="fa fa-trash"></i> Delete Deck
			</button>
			<delete-modal :show="showDeleteModal" @close="showDeleteModal = false"></delete-modal>
		</div>
	</div>
</template>

<script>
	import qwest from 'qwest'
	import Nanobar from 'app/nanobar'
	import TextEditor from 'app/components/text_editor.vue'
	import CardLink from 'app/components/card_link.vue'
	import DeckListing from 'app/components/deck_listing.vue'
	import CardEffects from 'app/gallery/listing/card_effects.vue'
	import DieCounter from './die_counter.vue'
	import DeleteModal from './delete_modal.vue'
	import ExportModal from './export_modal.vue'
	import SnapshotModal from './snapshot_modal.vue'
	import {globals, notify} from 'app/utils'

	export default {
		components: {
			'card-effects': CardEffects,
			'card-link': CardLink,
			'deck-listing': DeckListing,
			'die-counter': DieCounter,
			'text-editor': TextEditor,
			'export-modal': ExportModal,
			'delete-modal': DeleteModal,
			'snapshot-modal': SnapshotModal
		},
		data () {
			return {
				activeTab: 'deck',
				showDeleteModal: false,
				showExportModal: false,
				showSnapshotModal: false,
				createPublicSnapshot: false,
				editorOpen: false
			}
		},
		computed: {
			isDisabled () {
				return this.$store.state.isDisabled
			},
			title: {
				get () {
					return this.$store.state.deck.title
				},
				set (value) {
					this.$store.commit('setTitle', value)
				}
			},
			untitledText () {
				return this.$store.getters.untitledText
			},
			showDetails: {
				get () {
					return this.$store.state.options.showDetails
				},
				set (value) {
					return this.$store.commit('setShowDetails', value)
				}
			},
			phoenixborn () {
				return this.$store.getters.phoenixborn
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
			diceEmpty () {
				return this.$store.getters.totalDice === 0
			},
			diceNames () {
				return globals.diceData
			},
			isSaved () {
				return !!this.deckId
			},
			deckId () {
				return this.$store.state.deck.id
			},
			historyUrl () {
				if (!this.$store.state.deck.id) return '#'
				return ['/decks/view', this.$store.state.deck.id, 'history'].join('/')
			},
			isAshes500Enabled () {
				return this.$store.state.options.enableAshes500
			},
			ashes500ToggleWord () {
				return this.$store.state.options.enableAshes500 ? 'Disable' : 'Enable'
			}
		},
		methods: {
			clearPhoenixborn () {
				this.$store.commit('setTypes', ['Phoenixborn'])
				this.$store.commit('setPhoenixborn', null)
				this.$store.dispatch('filterCards')
				this.toggleEditorPane(false)
			},
			clearDie (die) {
				if (!die) return
				this.$store.commit('decrementDie', die)
			},
			clearDice () {
				this.$store.commit('clearDice')
			},
			setDiceFilters () {
				this.$store.commit('diceToFilters')
				this.$store.dispatch('filterCards')
				this.toggleEditorPane(false)
			},
			save () {
				const nano = new Nanobar({ autoRun: true })
				qwest.post(
					'/api/decks/' + (this.$store.state.deck.id || ''),
					this.$store.state.deck,
					{dataType: 'json'}
				).then((xhr, response) => {
					if (response.validation) {
						return notify(response.validation.title, 'error')
					} else if (response.error) {
						return notify(response.error, 'error')
					} else if (response.success) {
						notify(response.success, 'success')
					}
					if (!this.$store.state.deck.id) {
						this.$store.commit('setId', response.data.id)
						history.pushState(null, 'Deck saved!', '/decks/build/' + response.data.id + '/')
					}
				}).complete(() => {
					nano.go(100)
				})
			},
			newSnapshot (isPublic) {
				if (isPublic && (this.$store.getters.totalDice !== 10 || this.$store.getters.totalCards !== 30)) {
					return notify('Your deck must contain 10 dice and 30 cards to publish it.', 'error')
				}
				this.createPublicSnapshot = isPublic
				this.showSnapshotModal = true
			},
			closeSnapshotModal () {
				this.showSnapshotModal = false
				this.createPublicSnapshot = false
			},
			toggleEditorPane (isOpen) {
				this.editorOpen = (isOpen === undefined ? !this.editorOpen : isOpen)
				document.body.style.overflow = (this.editorOpen ? 'hidden' : 'auto')
			},
			toggleAshes500 () {
				this.$store.commit('toggleAshes500')
			}
		}
	}
</script>
