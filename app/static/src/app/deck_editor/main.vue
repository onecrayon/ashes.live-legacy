<template>
	<div id="editor-meta">
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
				@click="activeTab = 'meta'" :disabled="!phoenixborn">Meta</button>
		</div>
		<div v-if="activeTab == 'deck' && phoenixborn">
			<h3 class="phoenixborn-header">
				<span @click="clearPhoenixborn" class="fa fa-refresh refresh-btn" title="Swap Phoenixborn"></span>
				<a :href="cardUrl(phoenixborn)" class="card">{{ phoenixborn.name }}</a>
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
				<die-counter die-type="ceremonial" class="col"></die-counter>
				<die-counter die-type="charm" class="col"></die-counter>
				<die-counter die-type="illusion" class="col"></die-counter>
				<die-counter die-type="natural" class="col"></die-counter>
				<die-counter die-type="divine" class="col"></die-counter>
				<die-counter die-type="sympathy" class="col"></die-counter>
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
			<div v-for="section of deckSections" :key="section.title" class="deck-section">
				<hr v-if="section.title == 'Conjuration Deck'">
				<h4>{{ section.title }}</h4>
				<ul>
					<li v-for="card of section.contents" :key="card.data.id">
						<div v-if="section.title == 'Conjuration Deck'">
							{{ card.count }}&times; <a :href="cardUrl(card.data)" class="card">{{ card.data.name }}</a>
						</div>
						<div v-else>
							<qty-buttons :card="card.data" classes="btn-small"
								zero-output="<i class='fa fa-times' title='Remove'></i>"></qty-buttons>
							<a :href="cardUrl(card.data)" class="card">{{ card.data.name }}</a>
							<span v-if="card.data.phoenixborn" class="phoenixborn" :title="card.data.phoenixborn">
								({{ card.data.phoenixborn.split(' ')[0] }})
							</span>
						</div>
					</li>
				</ul>
			</div>
		</div>
		<div v-else-if="activeTab == 'meta' && phoenixborn">
			<text-editor :field="description" field-name="Description"></text-editor>
		</div>
	</div>
</template>

<script>
	import qwest from 'qwest'
	import {cardUrl} from 'app/utils'
	import TextEditor from 'app/forms/text_editor.vue'
	import CardEffects from 'app/gallery/listing/card_effects.vue'
	import QtyButtons from 'app/gallery/listing/qty_buttons.vue'
	import DieCounter from './die_counter.vue'

	export default {
		components: {
			'card-effects': CardEffects,
			'qty-buttons': QtyButtons,
			'die-counter': DieCounter,
			'text-editor': TextEditor
		},
		data: function () {
			return {
				activeTab: 'deck'
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
			description: {
				get () {
					return this.$store.state.deck.description
				},
				set (value) {
					this.$store.commit('setDescription', value)
				}
			},
			phoenixborn () {
				return this.$store.state.deck.phoenixborn
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
				return this.$store.getters.totalDice == 0
			},
			deckSections () {
				return this.$store.getters.deckSections
			}
		},
		methods: {
			cardUrl,
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
				// TODO
				var title = this.$store.state.deck.title
				console.log('Saving? ' + title)
				qwest.get('/api').then(function(xhr, response) {
					console.log('"Saved" deck (' + title + ') with API version: ' + response.version)
				}).catch(function(error, xhr, response) {
					console.log('Failed to save deck: ' + JSON.stringify(response))
				})
			}
		}
	}
</script>
