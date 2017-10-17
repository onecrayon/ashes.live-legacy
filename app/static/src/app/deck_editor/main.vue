<template>
	<div id="editor-meta">
		<ul v-if="alerts && alerts.length" class="alerts">
			<li v-for="(alert, index) of alerts" :key="index" :class="[alert.type]">
				<button class="btn-close" title="Dismiss"
					@click="dismissAlert(index)"><i class="fa fa-times"></i></button>
				{{ alert.message }}
			</li>
		</ul>
		<div class="deck-header">
			<div class="input-group">
				<div class="form-field">
					<input v-model="title" :disabled="!phoenixborn" type="text" placeholder="Untitled deck">
				</div>
				<button @click="save" :disabled="!phoenixborn" class="btn btn-primary">Save</button>
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
				<span @click="clearPhoenixborn" class="fa fa-refresh refresh-btn" title="Swap Phoenixborn"></span>
				<card-link :card="phoenixborn"></card-link>
			</h3>
			<div class="phoenixborn-detail">
				<ul class="statline">
					<li class="battlefield">Battlefield {{ phoenixborn.battlefield }}</li>
					<li class="life">Life {{ phoenixborn.life }}</li>
					<li class="spellboard">Spellboard {{ phoenixborn.spellboard }}</li>
				</ul>
				<card-effects :card="phoenixborn" all-text="true"></card-effects>
			</div>
			<ul class="dice">
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
					<button class="btn btn-small" @click="setDiceFilters" :disabled="diceEmpty">
						Set Dice Filter <i class="fa fa-arrow-right"></i>
					</button>
				</div>
			</div>
			<hr>
			<h3>
				Cards
				<span class="card-count">
					<span :class="{error: totalCards > 30}">{{ totalCards }}</span> / 30
				</span>
			</h3>
			<div v-for="section of deckSections" :key="section.title" class="deck-section">
				<hr v-if="section.title == 'Conjuration Deck'">
				<h4>{{ section.title }}</h4>
				<ul>
					<li v-for="card of section.contents" :key="card.data.id">
						<div v-if="section.title == 'Conjuration Deck'">
							{{ card.count }}&times; <card-link :card="card.data"></card-link>
						</div>
						<div v-else>
							<qty-buttons :card="card.data" classes="btn-small"
								zero-output="<i class='fa fa-times' title='Remove'></i>"></qty-buttons>
							<card-link :card="card.data"></card-link>
							<span v-if="card.data.phoenixborn" class="phoenixborn" :title="card.data.phoenixborn">
								({{ card.data.phoenixborn.split(' ')[0] }})
							</span>
						</div>
					</li>
				</ul>
			</div>
		</div>
		<div v-else-if="activeTab == 'meta' && phoenixborn">
			<text-editor state-path="deck.description" field-name="Description"></text-editor>
		</div>
		<div v-else-if="activeTab == 'actions' && phoenixborn">
			<button class="btn btn-block btn-primary" @click="showExportModal = true">
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
	import TextEditor from 'app/components/text_editor.vue'
	import CardLink from 'app/components/card_link.vue'
	import CardEffects from 'app/gallery/listing/card_effects.vue'
	import QtyButtons from 'app/gallery/listing/qty_buttons.vue'
	import DieCounter from './die_counter.vue'
	import DeleteModal from './delete_modal.vue'
	import ExportModal from './export_modal.vue'
	import {globals} from 'app/utils'

	export default {
		components: {
			'card-effects': CardEffects,
			'card-link': CardLink,
			'qty-buttons': QtyButtons,
			'die-counter': DieCounter,
			'text-editor': TextEditor,
			'export-modal': ExportModal,
			'delete-modal': DeleteModal
		},
		data: function () {
			return {
				activeTab: 'deck',
				alerts: [],
				showDeleteModal: false,
				showExportModal: false
			}
		},
		computed: {
			title: {
				get () {
					return this.$store.state.deck.title
				},
				set (value) {
					this.$store.commit('setTitle', value)
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
			deckSections () {
				return this.$store.getters.deckSections
			},
			totalCards () {
				return this.$store.getters.totalCards
			},
			diceNames () {
				return globals.diceData
			},
			isSaved () {
				return !!this.$store.state.deck.id
			}
		},
		methods: {
			clearPhoenixborn () {
				this.$store.commit('setTypes', ['Phoenixborn'])
				this.$store.commit('setPhoenixborn', null)
				this.$store.commit('filterCards')
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
				this.$store.commit('filterCards')
			},
			save () {
				this.alerts = []
				qwest.post(
					'/api/decks/' + (this.$store.state.deck.id || ''),
					this.$store.state.deck,
					{dataType: 'json'}
				).then((xhr, response) => {
					if (response.validation) {
						this.alerts.push({'type': 'error', 'message': response.validation.title})
					} else if (response.error) {
						this.alerts.push({'type': 'error', 'message': response.error})
					} else if (response.success) {
						this.alerts.push({'type': 'success', 'message': response.success})
					}
					if (!this.$store.state.deck.id) {
						this.$store.commit('setId', response.data.id)
						history.pushState(null, 'Deck saved!', '/decks/build/' + response.data.id + '/')
					}
				}).catch((error, xhr, response) => {
					this.alerts.push({'type': 'error', error})
					console.log('Failed to save deck:', response)
				})
			},
			dismissAlert (index) {
				this.alerts.splice(index, 1)
			}
		}
	}
</script>
