<template>
	<ul class="listing">
		<no-results></no-results>
		<li v-for="card of listing" :key="card.id" class="card-detail">
			<div class="thumbnail">
				<img :src="card.images.thumbnail" :alt="card.name">
				<qty-buttons :card="card"></qty-buttons>
			</div>
			<div class="details" :class="{'with-statline': hasStatline(card)} ">
				<h3>
					<a :href="cardUrl(card)" class="card">{{ card.name }}</a>
					<span v-if="card.phoenixborn" class="phoenixborn" :title="card.phoenixborn">
						({{ card.phoenixborn.split(' ')[0] }})
					</span>
				</h3>
				<p class="meta">{{ card.type }} <span class="divider"></span> {{ card.placement }}</p>
				<card-effects :card="card"></card-effects>
				<ul v-if="hasStatline(card)" class="statline">
					<li v-if="card.attack !== undefined" class="attack">Attack {{ card.attack }}</li>
					<li v-if="card.life !== undefined" class="life">Life {{ card.life }}</li>
					<li v-if="card.recover !== undefined" class="recover">Recover {{ card.recover }}</li>
				</ul>
			</div>
			<ol class="costs">
				<li v-for="cost of card.cost" class="cost" v-html="parseCardText(cost)"></li>
			</ol>
		</li>
	</ul>
</template>

<script>
	import {cardUrl, parseCardText} from './utils'
	import {filter, startsWith} from 'lodash'
	import CardEffects from './listing/card_effects.vue'
	import NoResults from './listing/no_results.vue'
	import QtyButtons from './listing/qty_buttons.vue'
	
	export default {
		components: {
			'card-effects': CardEffects,
			'no-results': NoResults,
			'qty-buttons': QtyButtons
		},
		computed: {
			listing () {
				return this.$store.state.listing
			}
		},
		methods: {
			cardUrl,
			parseCardText,
			startsWith,
			hasStatline (card) {
				return card.attack !== undefined
					|| card.life !== undefined
					|| card.recover !== undefined
			}
		}
	}
</script>

