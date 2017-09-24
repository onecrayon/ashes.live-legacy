<template>
	<ol class="card-effects">
		<li v-if="isReadySummon(card)" class="summon-effect">
			<div class="costs">
				<span v-for="cost of card.text[0].cost" class="cost" v-html="parseCardText(cost)"></span>: 
			</div>
			<div class="conjuration"
				><h4><a :href="cardUrl(card.conjurations[0])" class="card">{{ card.conjurations[0].name  }}</a></h4
				><span v-for="effect of namedEffects(card.conjurations[0].text)" class="effect"
					:title="effectTextTooltip(effect, true)"
					>{{ effect.name }}</span
				><ul class="statline"
					><li v-if="card.conjurations[0].attack !== undefined" class="attack">Attack {{ card.conjurations[0].attack }}</li
					><li v-if="card.conjurations[0].life !== undefined" class="life">Life {{ card.conjurations[0].life }}</li
					><li v-if="card.conjurations[0].recover !== undefined" class="recover">Recover {{ card.conjurations[0].recover }}</li
				></ul
			></div>
		</li>
		<li v-else v-for="effect of card.text" :class="[effect.inexhaustible ? 'inexhaustible' : '']">
			<strong v-if="effect.name" :title="effectTextTooltip(effect)">
				{{ effect.name }}</strong
			><span v-if="effect.cost" class="costs"
				><span v-if="effect.name">: </span
			><span v-for="cost of effect.cost" class="cost"
					v-html="parseCardText(cost)"></span></span
			><span v-if="!effect.name || isEffectTextException(effect)"
				><span v-if="effect.name || effect.cost">: </span
			><span v-html="parseCardText(effect.text)"></span></span>
		</li>
	</ol>
</template>

<script>
	import {cardUrl, parseCardText} from '../utils'
	import {filter, startsWith} from 'lodash'

	export default {
		props: [
			'card',
			'allText'
		],
		methods: {
			cardUrl,
			parseCardText,
			namedEffects (effects) {
				return filter(effects, (effect) => {
					return !!effect.name
				})
			},
			effectTextTooltip (effect, showAll) {
				if (this.allText) return
				if (showAll || (effect.text && !this.isEffectTextException(effect))) {
					return effect.text
				}
			},
			isEffectTextException (effect) {
				return !!this.allText || startsWith(effect.name, 'Focus') || startsWith(effect.name, 'Respark')
			},
			isReadySummon (card) {
				return card.type == 'Ready Spell' && startsWith(card.name, 'Summon')
			}
		}
	}
</script>
