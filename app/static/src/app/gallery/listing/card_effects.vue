<template>
	<ol class="card-effects">
		<li v-if="isReadySummon(card)" class="summon-effect">
			<div class="costs" v-if="card.text[0].cost || (card.text[1] && card.text[1].cost)">
				<card-codes v-for="(cost, cost_index) of (card.text[0].cost || card.text[1].cost)" :key="card.id + '-effect-0-cost-' + cost_index" class="cost" :content="cost"></card-codes>: 
			</div>
			<div class="conjuration"
				><h4><card-link :card="card.conjurations[0]"></card-link></h4
				><span v-for="(effect, effect_index) of namedEffects(card.conjurations[0])" class="effect tooltip"
					:title="effectTextTooltip(effect, true)" :key="card.conjurations[0].id + '-effect-' + effect_index"
					>{{ effect.name }}</span
				><ul class="statline"
					><li v-if="card.conjurations[0].attack !== undefined" class="attack">Attack {{ card.conjurations[0].attack }}</li
					><li v-if="card.conjurations[0].life !== undefined" class="life">Life {{ card.conjurations[0].life }}</li
					><li v-if="card.conjurations[0].recover !== undefined" class="recover">Recover {{ card.conjurations[0].recover }}</li
				></ul
			></div>
		</li>
		<li v-else v-for="(effect, effect_index) of card.text" :class="[effect.inexhaustible ? 'inexhaustible' : '', effect.betweenRealms ? 'between-realms' : '']"
				:key="card.id + '-effect-' + effect_index">
			<strong v-if="effect.name" :title="effectTextTooltip(effect)" :class="{tooltip: !!effectTextTooltip(effect)}">
				{{ effect.name }}</strong
			><span v-if="effect.cost" class="costs"
				><span v-if="effect.name">: </span
			><card-codes v-for="(cost, cost_index) of effect.cost" class="cost"
					:content="cost" :key="card.id + '-effect-' + effect_index + '-cost-' + cost_index"></card-codes></span
			><span v-if="!effect.name || isEffectTextException(effect)"
				><span v-if="effect.name || effect.cost">: </span
			><card-codes :content="effect.text"></card-codes></span>
		</li>
	</ol>
</template>

<script>
	import CardCodes from 'app/components/card_codes.vue'
	import CardLink from 'app/components/card_link.vue'
	import {initTooltips, teardownTooltips} from 'app/utils'
	import {filter, endsWith, startsWith} from 'lodash'

	export default {
		props: [
			'card',
			'allText'
		],
		components: {
			'card-codes': CardCodes,
			'card-link': CardLink
		},
		mounted: initTooltips,
		updated: function () {
			teardownTooltips.call(this)
			initTooltips.call(this)
		},
		beforeDestroy: teardownTooltips,
		methods: {
			namedEffects (card) {
				// Exclude common mount abilities (always the last two)
				const maxLength = endsWith(card.name, ' Mount') ? card.text.length - 2 : card.text.length
				return filter(card.text, (effect, index) => {
					return !!effect.name && index < maxLength
				})
			},
			effectTextTooltip (effect, showAll) {
				if (this.allText) return
				if (showAll || (effect.text && !this.isEffectTextException(effect))) {
					return (showAll && effect.cost ? effect.cost.join(' - ') + ': ' : '') + effect.text
				}
			},
			isEffectTextException (effect) {
				return !!this.allText || startsWith(effect.name, 'Focus') || startsWith(effect.name, 'Respark')
			},
			isReadySummon (card) {
				return card.type === 'Ready Spell' && startsWith(card.name, 'Summon')
			}
		}
	}
</script>
