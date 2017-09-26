<template>
	<div id="editor-meta">
		<div class="deck-header">
			<div class="input-group">
				<div class="form-field">
					<input v-model="title" :disabled="!phoenixborn" type="text" placeholder="Untitled deck">
				</div>
				<button v-on:click="save" :disabled="!phoenixborn" class="btn btn-primary">Save</button>
			</div>
		</div>
		<div v-if="phoenixborn">
			<h3 class="phoenixborn-header">
				<span v-on:click="clearPhoenixborn" class="fa fa-refresh refresh-btn" title="Swap Phoenixborn"></span>
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
		</div>
	</div>
</template>

<script>
	import qwest from 'qwest'
	import {cardUrl} from './utils'
	import CardEffects from './listing/card_effects.vue'
	import DieCounter from './deck/die_counter.vue'

	export default {
		components: {
			'card-effects': CardEffects,
			'die-counter': DieCounter
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
