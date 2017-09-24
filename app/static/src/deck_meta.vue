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
		</div>
		<ul v-if="phoenixborn" class="dice">
			<li v-for="(die, index) of dice" :key="index" class="die" :class="[die ? die : '']">
				<span v-if="die" :class="'phg-' + die + '-power'"></span>
				<i v-if="!die" class="fa fa-plus"></i>
			</li>
		</ul>
	</div>
</template>

<script>
	import qwest from 'qwest'
	import {cardUrl} from './utils'
	import CardEffects from './listing/card_effects.vue'
	import {assign, clone, fill} from 'lodash'

	export default {
		components: {
			'card-effects': CardEffects
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
			dice () {
				let diceArray = clone(this.$store.state.deck.dice)
				if (this.$store.state.deck.dice.length < 10) {
					diceArray = assign(fill(new Array(10), null), diceArray)
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
